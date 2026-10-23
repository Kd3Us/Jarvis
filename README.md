# Jarvis

Multimodal conversational assistant (text, image, voice), built with Streamlit and Groq.

## Project structure

```
backend/
  llm_agent.py        LLM / VLM / STT calls
  user_interface.py   Streamlit interface (temporary)
  prompts/system.md   System prompt
  requirements.txt
frontend/             Vite frontend (coming in JAR-08)
.env.example          Environment variables template
CONTRIBUTING.md       Workflow and conventions
```

## Setup

1. Python 3.11+ and a virtual environment.
2. `pip install -r backend/requirements.txt`
3. Copy `.env.example` to `.env` and fill in `GROQ_KEY`.

## Run

```
streamlit run backend/user_interface.py
```

## Decisions

- TTS: on hold, Groq only for now (LLM, VLM, STT). See JAR-02.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).