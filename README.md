# VoxNote AI

VoxNote AI transcribes audio with Groq Whisper, summarizes it with LangChain
and Groq, and converts text to speech locally with `pyttsx3`.

## Setup

Create and activate the `uk` virtual environment:

```bash
/usr/bin/python -m venv uk
source uk/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GROQ_API_KEY` to your Groq API key.

On Linux, `pyttsx3` also needs an eSpeak-compatible speech engine. On Debian or
Ubuntu, install it with:

```bash
sudo apt install espeak-ng
```

## Run

```bash
streamlit run app.py
```
