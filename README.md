# FightRAG

## Run the application

The repository contains the prepared ChromaDB index and evaluation results, so the PDFs do not need to be processed again. The original PDFs and intermediate files can be included separately in the submitted ZIP, but they are not required to run the app.

### 1. Create and activate a virtual environment

Open PowerShell in the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install the dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure the Groq API

Create`.env`, then add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

The API key is required for generating new answers. The saved evaluation results can be viewed without generating them again.

### 4. Start Streamlit

```powershell
python -m streamlit run streamlit_app.py --server.fileWatcherType none
```

Open the local URL printed in the terminal. The application contains the **Rulebook Assistant** and **Model Insights** tabs.

## Deploy on Streamlit Community Cloud

Push the repository including `streamlit_app.py`, `requirements.txt`, `app/`, `src/`, `data/chroma_db/`, `data/evaluation/` and `.streamlit/config.toml`. In Streamlit Cloud use:

- main file path: `streamlit_app.py`
- Python version: `3.13`
- secrets: `GROQ_API_KEY` and `GROQ_MODEL`

The `.env` file and `.streamlit/secrets.toml` must never be committed.

## Project overview

FightRAG is a question-answering system for combat sports rules. It works with three rule systems:

- MMA - ABC Unified Rules of MMA
- Muay Thai - IFMA Rules and Regulations
- K-1 Style - WAKO K-1 base rules and amendment

The goal was to test whether sport-aware retrieval produces more accurate answers than general RAG or an LLM without documents.

## Answering modes

| Mode | How it works | Why it is included |
|---|---|---|
| **LLM Only** | The model answers without rulebook context. | Provides a baseline. |
| **General RAG** | Searches all indexed rulebooks and returns the six closest passages. | Represents a standard RAG system. |
| **Sport-aware RAG** | Detects the sports in the question and divides the six results between them. | Prevents one sport from dominating comparison questions. |

All modes use the same `openai/gpt-oss-20b` model through the Groq API. This keeps the comparison focused on retrieval rather than the language model.

## How the system works

```text
PDF rulebooks
    -> text extraction by page
    -> cleaning and chunking
    -> multilingual embeddings
    -> ChromaDB retrieval
    -> Groq answer with inline citations
```

The PDFs were processed page by page so the original document and page number could be preserved. The text was split into chunks of at most 2200 characters with a small overlap. This keeps enough context around a rule while allowing precise retrieval.

The `intfloat/multilingual-e5-small` model creates the embeddings. ChromaDB stores the vectors together with the sport, document name, document type and PDF page.

The RAG prompt tells the model to:

- use only the retrieved rulebook passages;
- keep rules from different sports separate;
- cite factual statements with source numbers;
- admit when the supplied context is insufficient;
- apply the WAKO amendment when it conflicts with the older K-1 rules.

If no sport is detected, Sport-aware RAG falls back to general retrieval. If retrieval returns no passage, the system does not send an empty context to the model.

## Project structure

```text
FightRAG/
|-- streamlit_app.py    # Local and Streamlit Cloud entry point
|-- app/
|   |-- main.py          # Builds the Streamlit interface
|   |-- assistant.py     # Chat, citations and error handling
|   |-- insights.py      # Evaluation dashboard
|   `-- theme.py         # Interface styling
|-- src/
|   |-- config.py        # Models, paths and retrieval settings
|   |-- pdf_processor.py # Extracts text and metadata from PDFs
|   |-- chunking.py      # Cleans and splits the extracted text
|   |-- vector_store.py  # Builds the embedding index in ChromaDB
|   |-- sport_detector.py# Detects MMA, Muay Thai and K-1 in questions
|   |-- retrieval.py     # General and sport-aware retrieval
|   |-- rag.py           # Builds the RAG context and prompt
|   |-- llm.py           # Calls the Groq API
|   `-- pipeline.py      # Connects the three answering modes
|-- scripts/             # Validation, evaluation and diagnostic tools
|-- data/
|   |-- raw/             # Original PDF rulebooks
|   |-- processed/       # Extracted pages and text chunks
|   |-- chroma_db/       # Prepared vector database
|   `-- evaluation/      # Questions, answers, scores and summaries
|-- .streamlit/          # Streamlit configuration
`-- requirements.txt     # Python dependencies
```

## Evaluation

The evaluation contains 30 questions: 8 development questions and 22 final evaluation questions. Each question was answered with all three methods, giving 90 manually reviewed answers.

The scoring scale was:

- `0` - incorrect
- `1` - partially correct
- `2` - correct

Results on the 22 evaluation questions:

| Method | Normalized score |
|---|---:|
| LLM Only | 34.1% |
| General RAG | 38.6% |
| Sport-aware RAG | 61.4% |

The normalized score is the earned score divided by the maximum possible score. It is not classification accuracy.

The result supports the main idea of the project: sport-aware retrieval helped most on questions that compared multiple sports. The evaluation is limited because the dataset is small and the answers were scored by one reviewer.

The **Model Insights** tab displays the overall results, category-level scores, individual model answers, reviewer notes and downloadable evaluation data.
