from flask import Flask, render_template, request, send_file
import subprocess
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)

OLLAMA_PATH = r"C:\Users\kacha\AppData\Local\Programs\Ollama\ollama.exe"


# ---------- AI GENERATION ----------
def generate_resume_text(name, skills, experience):

    prompt = f"""
    Create a professional resume for:

    Name: {name}
    Skills: {skills}
    Experience: {experience}

    Make it clean and professional.
    """

    result = subprocess.run(
        [OLLAMA_PATH, "run", "phi", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    return result.stdout


# ---------- PDF CREATION ----------
def create_pdf(text, filename):
    path = f"generated/{filename}"

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    y = height - 40

    for line in text.split("\n"):
        c.drawString(40, y, line[:95])
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

        name = request.form["name"]
        skills = request.form["skills"]
        experience = request.form["experience"]

        resume_text = generate_resume_text(name, skills, experience)

        pdf_path = create_pdf(resume_text, "resume.pdf")

        return render_template("preview.html", text=resume_text)

    return render_template("index.html")


# ---------- DOWNLOAD ----------
@app.route("/download")
def download():
    return send_file("generated/resume.pdf", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

