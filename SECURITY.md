# Security

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Report via a
[private security advisory](https://github.com/dsk-dev-ai/smart-resume-builder-ai/security/advisories)
on GitHub. We aim to acknowledge reports within 3 business days.

## Dependencies

This app optionally calls a local [Ollama](https://ollama.com/) server for
resume text generation. By default it does not send data to third-party
services.

- Never commit API keys or secrets.
- PDFs are generated locally with ReportLab; review generated downloads for
  content injection if you customize prompts.