# FundLens --- SBI Mutual Fund Information Assistant

> **Facts only. No investment advice.**

FundLens is a retrieval-augmented FAQ assistant built for the
**RAG-based Mutual Fund FAQ Chatbot** milestone. It answers factual
questions about selected SBI Mutual Fund schemes using a curated corpus
of official public sources and presents the supporting source and
source-document date with the answer.

## Project Details

  -----------------------------------------------------------------------
  Item                                Selection
  ----------------------------------- -----------------------------------
  Milestone                           RAG-based Mutual Fund FAQ Chatbot

  Selected product                    Groww

  AMC                                 SBI Mutual Fund

  Schemes                             SBI Large Cap Fund, SBI Flexicap
                                      Fund, SBI ELSS Tax Saver Fund

  Interface                           Streamlit

  Retrieval                           TF-IDF / cosine-similarity
                                      retrieval

  Data                                Curated public official sources

  Advice policy                       Facts only; no investment
                                      recommendations
  -----------------------------------------------------------------------

## Problem

Mutual-fund information is spread across factsheets, TER disclosures,
scheme documents and investor-service pages. FundLens provides a focused
interface where a user can ask a factual question in natural language
and receive a concise, source-grounded response.

The assistant is designed to answer documented facts such as:

-   Expense ratio / TER
-   Exit load
-   Minimum investment
-   Minimum SIP
-   ELSS lock-in period
-   Benchmark
-   Riskometer
-   Statement and capital-gains statement navigation
-   Other documented scheme facts available in the curated corpus

## Core Product Flow

``` text
User question
      ↓
PII / sensitive-data check
      ↓
Advice / scope check
      ↓
Query understanding
      ↓
TF-IDF retrieval
      ↓
Evidence gate
      ↓
Concise factual answer
      ↓
Official source + document date
      ↓
Contextual related factual questions
```

## RAG Approach

The prototype uses a lightweight retrieval-augmented approach suitable
for the milestone:

1.  Public official documents/pages are collected into
    `data/corpus.json`.
2.  Documents are represented using TF-IDF vectors.
3.  Cosine similarity is used to retrieve relevant evidence for a user
    query.
4.  The application applies an evidence threshold before presenting a
    grounded answer.
5.  Known FAQ intents are mapped to the relevant retrieved source where
    appropriate.
6.  The final response is kept concise and includes the supporting
    source.
7.  Related questions are generated from the current topic so users can
    continue exploring factual information.

This is a **retrieval-first factual assistant**, not a generative
investment advisor.

## Natural-Language Queries

The assistant is intended to handle normal user phrasing rather than
only fixed demo questions.

Examples:

``` text
What is SBI Large Cap Fund?
Tell me about SBI Large Cap
What is the expense ratio?
How much SIP can I start with?
What is the exit load?
What benchmark does it follow?
What is the riskometer?
What is the lock-in period of SBI ELSS?
Where can I find my capital gains statement?
```

After an answer, the interface can surface related factual questions
such as:

``` text
What is the minimum investment?
What is the minimum SIP?
What is the benchmark?
What is the exit load?
What is the riskometer?
What is the expense ratio?
```

Clicking a related question sends that question back through the same
retrieval and evidence flow.

## Facts-Only Safety Boundary

FundLens does **not** provide personalized investment advice.

Questions such as:

-   Should I buy this fund?
-   Should I sell or redeem?
-   Which fund is best?
-   Which fund should I choose?
-   How should I allocate my portfolio?

are outside the assistant's scope.

For these queries, the assistant provides a polite facts-only response
and redirects the user toward factual questions it can answer.

The application also warns users not to enter sensitive personal
information such as PAN, Aadhaar, OTPs, account numbers, email addresses
or phone numbers.

## Source Grounding

The application is designed to show:

-   Source title
-   Source/document date where available
-   Official-source indication
-   Direct source link

The UI does **not** claim that the corpus is live simply because the
website itself is online. A displayed source date refers to the source
document/page used by the assistant.

### Primary official source areas

-   SBI Mutual Fund homepage
-   SBI Mutual Fund Factsheets
-   SBI Mutual Fund Total Expense Ratio disclosures
-   SBI Mutual Fund SID / KIM documents
-   SBI Mutual Fund investor-service / statement navigation

The detailed source inventory is maintained in:

`source_list.csv`

## Selected Schemes

### SBI Large Cap Fund

The curated corpus contains factual information such as minimum
investment, SIP requirements, exit-load structure, benchmark, riskometer
and expense-ratio disclosures.

### SBI Flexicap Fund

The curated corpus contains factual information such as minimum
investment, SIP requirements, exit load, benchmark, riskometer and
expense-ratio disclosures.

### SBI ELSS Tax Saver Fund

The curated corpus contains factual information such as the statutory
three-year lock-in, minimum investment/SIP, exit load, benchmark,
riskometer and expense-ratio disclosures.

> Source dates are shown in the application based on the particular
> official document used. The corpus is a curated snapshot and should
> not be described as real-time data.

## Interface

The current interface is designed as a premium, interactive fintech/AI
experience rather than a plain FAQ form.

Key UI elements include:

-   FundLens product branding
-   Futuristic animated background and glass-style cards
-   Interactive scheme cards
-   Natural-language search
-   Example questions
-   Contextual related-question buttons
-   Grounded answer cards
-   Source evidence cards
-   Clickable official-resource links
-   RAG pipeline explanation
-   Facts-only status indicators
-   Responsive layout

Interactive elements are intended to lead to an actual question, answer,
source, or official resource rather than being decorative-only UI.

## Repository Structure

``` text
4th-milestone/
│
├── app.py
├── data/
│   └── corpus.json
├── source_list.csv
├── sample_qa.md
├── disclaimer.txt
├── DEMO_SCRIPT.md
├── PROMPT.md
├── requirements.txt
├── .gitignore
└── README.md
```

## Running Locally

Install dependencies:

``` bash
pip install -r requirements.txt
```

Run the Streamlit application:

``` bash
streamlit run app.py
```

The application should then open in the local Streamlit interface.

## Sample Q&A

See:

`sample_qa.md`

The sample set demonstrates factual questions, grounded answers, source
citations and the facts-only boundary.

## Disclaimer

The assistant provides general factual information from selected public
sources. It does not provide investment, financial, tax, legal or
trading advice, and it does not recommend buying, selling, switching or
allocating investments.

Users should refer to the official source documents for the complete and
latest applicable information.

See:

`disclaimer.txt`

## Limitations

-   The prototype uses a curated corpus rather than continuously
    crawling the web.
-   Source freshness depends on the documents/pages included in the
    corpus.
-   The assistant only covers the selected schemes and factual topics
    represented in the corpus.
-   A failed evidence check should result in a transparent limitation
    rather than an invented answer.
-   Source-document dates should be interpreted as the dates of the
    cited source, not as a claim that the entire assistant is
    live-updated.

## Deliverables

-   [x] Working RAG FAQ prototype
-   [x] Selected product and AMC
-   [x] Three selected schemes
-   [x] Curated public-source corpus
-   [x] Source list
-   [x] Sample Q&A
-   [x] Facts-only disclaimer
-   [x] Interactive UI
-   [x] Source-grounded responses
-   [x] Contextual follow-up questions

## Demo

**Live prototype:**\
`https://4th-milestone-qv66wmtr2zqyu3jdhttzw.streamlit.app`

**GitHub repository:**\
`https://github.com/adityarathigkv-sudo/4th-milestone`

## Demo Story

A short demo can follow this sequence:

1.  Introduce FundLens and the selected SBI Mutual Fund scope.
2.  Show the three supported schemes.
3.  Ask a natural-language factual question.
4.  Show the concise grounded answer.
5.  Open the cited official source.
6.  Click a contextual related question.
7.  Ask an investment-advice question and demonstrate the facts-only
    boundary.
8.  Briefly explain the retrieval → evidence → citation flow.

## Credits / Context

Built as a Product Management Fellowship milestone to demonstrate
retrieval-grounded product design, source transparency, safety
boundaries and an interactive FAQ experience.
