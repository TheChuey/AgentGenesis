From inside your project’s virtual environment, run:

```bash
pip freeze > requirements.txt
```

That creates a `requirements.txt` file with all installed packages and versions.

Example:

```txt
flask==3.1.0
langchain==0.3.27
ollama==0.6.0
chromadb==1.0.12
```

## Recommended workflow

### 1. Activate your virtual environment

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 2. Generate the file

```bash
pip freeze > requirements.txt
```

### 3. Reinstall later on another machine

```bash
pip install -r requirements.txt
```

---

## Better option for cleaner projects

`pip freeze` includes everything, even packages you may not directly use.

A cleaner approach is:

```bash
pip install pipreqs
pipreqs .
```

This scans your Python files and creates a smaller `requirements.txt` based on your imports.

Example:

```txt
flask
langchain
chromadb
ollama
```

---

## Useful checks

See installed packages:

```bash
pip list
```

See package details:

```bash
pip show langchain
```

See outdated packages:

```bash
pip list --outdated
```

---

For your AI agent projects with Ollama + LangChain, many developers use:

```bash
pip freeze > requirements.txt
```

during development, then later clean it up manually before publishing.
