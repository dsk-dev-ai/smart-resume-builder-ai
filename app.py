from flask import Flask, render_template, request, send_file, flash, redirect
import os
import uuid
import json
import urllib.request
import urllib.error
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(32))

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi")


# ---------- AI GENERATION ----------
def generate_resume_text(name, skills, experience):

    prompt = f"""
    Create a professional resume for:

    Name: {name}
    Skills: {skills}
    Experience: {experience}

    Make it clean and professional.
    """

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, json.JSONDecodeError) as e:
        return f"Error: could not generate resume — Ollama unavailable ({e})"


# ---------- PDF CREATION ----------
def _wrap_text(text, max_width, c):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if c.stringWidth(test) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_pdf(text, filename):
    path = f"generated/{filename}"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 40
    max_width = width - 80

    for line in text.split("\n"):
        wrapped = _wrap_text(line, max_width, c)
        for wl in wrapped:
            c.drawString(40, y, wl)
            y -= 15
            if y < 40:
                c.showPage()
                y = height - 40

    c.save()
    return path


# ---------- HOME ----------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        skills = request.form.get("skills", "").strip()
        experience = request.form.get("experience", "").strip()

        if not name or not skills or not experience:
            flash("All fields are required.")
            return render_template("index.html")

        resume_text = generate_resume_text(name, skills, experience)

        filename = uuid.uuid4().hex + ".pdf"
        pdf_path = create_pdf(resume_text, filename)

        return render_template("preview.html", text=resume_text, filename=filename)

    return render_template("index.html")


# ---------- DOWNLOAD ----------
@app.route("/download/<filename>")
def download(filename):
    safe = os.path.basename(filename)
    path = f"generated/{safe}"
    if not os.path.isfile(path):
        flash("File not found.")
        return redirect("/")
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    os.makedirs("generated", exist_ok=True)
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
