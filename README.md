# Ollama Agents - Desktop App (Python)

This repository contains a lightweight desktop application scaffold (PySide6) that integrates local Ollama models and Hugging Face models/spaces for chat and simple autonomous task execution.

Features
- Local chat using Ollama (via ollama-python or CLI fallback)
- Optional Hugging Face model/space integration
- Run shell commands and Python snippets from the UI
- Model selection presets

Notes and prerequisites
- This app expects Ollama to be installed locally for full local model usage. See https://ollama.com for install instructions.
- For Hugging Face Spaces or private models, set HUGGINGFACE_API_TOKEN as an environment variable.
- The code intentionally keeps execution capabilities basic. Running arbitrary shell commands or Python code can be dangerous; use with caution.

Installation (Debian/Arch/RHEL)

1. Ensure Python 3.10+ is installed.
2. Create a virtual environment and install requirements:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

3. Run the app:
   python main.py

Packaging
- For Debian/Arch/RHEL packaging, consider building a system Python virtualenv and creating a launcher script and .desktop file for integration.

Extending to other providers
- The repo includes simple wrappers (ollama_client.py and hf_client.py). You can extend these to call remote OpenAI/Anthropic/Grok-like APIs using their official SDKs — be mindful of credentials and pricing. The current scaffold focuses on Ollama and Hugging Face as requested.
