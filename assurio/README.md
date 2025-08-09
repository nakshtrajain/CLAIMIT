# Assurio - Intelligent Clause Retriever & Decision System

Assurio is an intelligent system that uses LLM-powered semantic search to retrieve relevant clauses from insurance documents and provide automated decision-making.

---

## 🚀 Features

- **Document Upload:** Upload PDF insurance documents with drag & drop
- **Auto Indexing:** Automatic embedding generation and FAISS indexing
- **Semantic Search:** Find relevant clauses using FAISS vector search
- **LLM Reasoning:** Use Gemini to analyze clauses and make decisions
- **Entity Extraction:** Automatically extract key information from queries
- **Real-time Processing:** Background processing for large documents

---

## 🛠️ Tech Stack

- **Backend:** FastAPI (Async)
- **Embeddings:** SentenceTransformers (MiniLM)
- **Vector DB:** FAISS (Local)
- **LLM:** Google Gemini (via LangChain)
- **Document Processing:** PyPDF2
- **File Handling:** Async file operations

---

## 📁 Project Structure

```
ASSURIO/
│
├── app/
│   ├── main.py
│   ├── routes/
│   ├── utils/
│   └── templates/
│       └── enhanced.html
├── config.py
├── requirements.txt
├── static/
├── data/
│   └── uploads/
├── .env
├── README.md
└── ...
```

---

## ⚙️ Configuration

Set your environment variables in a `.env` file at the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=models/gemini-1.5-flash
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
```

---

## 🏃‍♂️ Getting Started

1. **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ASSURIO/DocuClaim
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up your `.env` file** (see above).

5. **Run the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload
    ```

6. **Access the app:**
    - Open [http://localhost:8000/](http://localhost:8000/) for the main interface.
    - Open [http://localhost:8000/docs](http://localhost:8000/docs) for API docs.

---

## 📝 Usage

- Upload PDF documents via the web interface.
- Query the system for clause retrieval and automated decision-making.
- Manage uploaded files and system health from the dashboard.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](LICENSE)

---

## 📬 Contact

For questions or support, please open an issue on the