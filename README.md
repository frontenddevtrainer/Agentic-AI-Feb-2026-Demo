# Agentic AI - LangChain Multi-Provider Setup

A LangChain project supporting multiple LLM providers: **Gemini**, **Anthropic**, **Groq**, and **OpenAI**.

---

## Prerequisites

- Python 3.10+
- `pip`

---

## 1. Clone / Open the Project

```bash
cd "Agentic AI Feb 2026"
```

---

## 2. Create & Activate Virtual Environment

```bash
python -m venv venv
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Install the provider package(s) you plan to use:

| Provider  | Install command                          |
|-----------|------------------------------------------|
| Gemini    | `pip install langchain-google-genai`     |
| Anthropic | `pip install langchain-anthropic`        |
| Groq      | `pip install langchain-groq`             |
| OpenAI    | `pip install langchain-openai`           |

---

## 4. Configure Environment Variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

Open `.env` and add the key for the provider you want to use:

```env
# Choose one provider and set its key
LLM_PROVIDER=gemini        # options: gemini | anthropic | groq | openai

GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
```

### Where to get API keys

| Provider  | URL                                         |
|-----------|---------------------------------------------|
| Gemini    | https://aistudio.google.com/app/apikey      |
| Anthropic | https://console.anthropic.com/settings/keys |
| Groq      | https://console.groq.com/keys               |
| OpenAI    | https://platform.openai.com/api-keys        |

---

## 5. Run the Project

```bash
python main.py
```

The active provider is controlled by `LLM_PROVIDER` in your `.env` file.

---

## Project Structure

```
Agentic AI Feb 2026/
├── main.py            # Main entry point
├── requirements.txt   # Core dependencies
├── .env               # Your API keys (not committed)
├── .env.example       # Template for .env
└── README.md          # This file
```