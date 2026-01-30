# processing — PDF and Text Processing

Low-level PDF parsing and text chunking used by extraction and RAG.

**Modules:**
- **pdf_parser.py** — `extract_text_from_pdf(pdf_path) -> str`. Uses `pdfplumber`; supports multilingual (e.g. Arabic/English).
- **text_chunker.py** — `chunk_text(text, chunk_size, overlap, ...)` and `chunk_text_by_sentences(text, sentences_per_chunk, ...)`. Returns list of dicts with `text` and `metadata`.

**Used by:** Core (extraction), RAG (ingestion). No LLM or DB here.
