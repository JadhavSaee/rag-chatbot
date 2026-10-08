# Sunrise Health Clinic Assistant

A RAG (retrieval-augmented generation) FAQ chatbot for a **fictional demo clinic**. It answers questions about timings, doctors, fees and policies using only the clinic's own documents, shows which file each answer came from, and falls back to the clinic's phone number when it doesn't know.

> Demo project. Sunrise Health Clinic, its doctors and its phone number are made up.

<!-- Add a screenshot or GIF here: ![demo](demo.gif) -->

## What it does

- Retrieves the most relevant passages from the clinic documents, then answers from those passages only
- Cites its sources (for example `clinic_info.txt`)
- Handles short follow-up style questions ("Doc for skin?", "Sundays?")
- Declines out-of-scope questions (trivia, prompt-injection attempts, anything the documents don't cover) with a fallback message instead of guessing
- Declines to give medical advice and suggests booking an appointment

## Stack

Python · ChromaDB (vector store) · Groq API (LLM) · Streamlit (UI)

Built entirely on free tiers.

## Project structure

```
app.py            Streamlit chat interface
rag.py            Retrieval + answer generation
ingest.py         Loads documents from docs/ into ChromaDB   [verify]
docs/             Clinic documents (clinic_info.txt, clinic_policies.txt)
run_tests.py      Runs the test questions and prints a score
test_*.py         Small scripts used while developing retrieval
.env.example      Template for your API key
```

## Run it locally

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

copy .env.example .env         # then paste your Groq API key into .env
python ingest.py               # build the vector database    [verify]
streamlit run app.py
```

Run the tests with `python run_tests.py`.

## Testing

`run_tests.py` runs 31 test questions (answerable questions, questions that should be refused, and edge cases). The current version passes 31/31.

These tests were written by me, so this is a sanity check and not a measure of real-world accuracy. The set is small and I'm still expanding it.

## Known limitations

- Knowledge is limited to the two demo documents
- Tested only on English and short Hinglish-style queries  [verify]
- Source citations appear only on the most recent answer in the UI
- Runs locally; not deployed

## Roadmap

- [ ] Telegram bot interface (next)
- [ ] Larger and harder test set
- [ ] Show sources on every message
- [ ] Deploy a public demo

## Author

Saee: B.Tech Computer Science student.
