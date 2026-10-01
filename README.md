# SBI Mutual Fund FactsBot — RAG FAQ Chatbot

**Milestone:** RAG-based Mutual Fund FAQ Chatbot  
**Selected product:** Groww  
**AMC:** SBI Mutual Fund  
**Schemes:** SBI Large Cap Fund, SBI Flexicap Fund, SBI ELSS Tax Saver Fund

## What this prototype does
A small Streamlit retrieval-augmented FAQ assistant for factual mutual-fund questions. It retrieves from a curated corpus of official SBI Mutual Fund / SEBI public sources, applies an evidence gate, gives a concise answer, and shows one source link plus the source update date.

Supported factual areas:
- Expense ratio / TER
- Exit load
- Minimum SIP / minimum investment
- ELSS lock-in
- Benchmark
- Riskometer
- Statement / capital-gains statement navigation
- Basic official-source navigation

It refuses:
- Buy/sell/switch/redeem recommendations
- “Best fund” or suitability rankings
- Portfolio construction/allocation
- Return/performance comparisons
- Requests containing PII

## Architecture

`User Query → PII Check → Advice/Opinion Check → TF-IDF Retrieval → Evidence Gate → Deterministic Fact Answer → One Official Citation`

The retrieval layer is intentionally lightweight and transparent. The answer layer uses fixed fact mappings backed by retrieved documents, reducing hallucination risk for a small facts-only corpus.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload this entire project.
3. In Streamlit Community Cloud, create a new app.
4. Select the repository and branch.
5. Set the main file to `app.py`.
6. Deploy.

No API key is required by this prototype.

## Corpus
`data/corpus.json` contains the curated evidence snippets and their official source URLs. `source_list.csv` contains 20 public source URLs from SBI Mutual Fund / SEBI.

## Important limits
- This is a small educational prototype, not a live financial service.
- Scheme facts can change. The displayed facts are tied to the dated official documents in the corpus.
- It does not fetch live NAVs or calculate returns.
- It does not collect or persist user PII.
- It should not be used for investment, tax or financial decisions.

## Submission files
- `app.py` — working Streamlit prototype
- `data/corpus.json` — RAG corpus
- `source_list.csv` — 20 official URLs
- `sample_qa.md` — sample Q&A
- `disclaimer.txt` — UI disclaimer
- `PROMPT.md` — LLM/RAG guardrails and prompting logic
- `README.md` — setup, scope and limitations
- `requirements.txt` — dependencies

## Demo questions
1. What is the exit load of SBI Large Cap Fund?
2. What is the minimum SIP for SBI ELSS Tax Saver Fund?
3. What is the benchmark of SBI Flexicap Fund?

## Disclaimer
Facts-only mutual fund FAQ prototype. This assistant provides factual information from approved public SBI Mutual Fund / SEBI sources and does not provide investment, tax, legal or financial advice. Mutual fund investments are subject to market risks; read scheme-related documents carefully.
