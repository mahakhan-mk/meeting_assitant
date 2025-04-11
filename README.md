
# 📝 Intelligent Meeting Assistant

This is a simple Streamlit app that generates a **meeting summary** and **action items** from a provided transcript using **LangGraph** and **Groq** (Llama 3).

## Setup

1. **Install Requirements:**

```bash
pip install langchain-core==0.3.49
pip install langchain-groq==0.3.2
pip install langgraph==0.3.21
pip install langgraph-checkpoint==2.0.23
pip install langgraph-prebuilt==0.1.7
pip install langgraph-sdk==0.1.60
pip install python-dotenv==1.1.0
pip install streamlit==1.44.0
```

2. **Get a Groq API Key:**

- Sign up at [groq.com](https://groq.com/).
- Create a `.env` file in the project root and add:

```
GROQ_API_KEY=your_groq_api_key_here
```

## Run the App

```bash
streamlit run app.py
```

---
