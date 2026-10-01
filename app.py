import json, re
from pathlib import Path
from datetime import date
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="SBI MF FactsBot", page_icon="📚", layout="centered")

CORPUS = json.loads((Path(__file__).parent / "data" / "corpus.json").read_text(encoding="utf-8"))
DOCS = [x["text"] for x in CORPUS]
VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1,2), sublinear_tf=True)
MATRIX = VECTORIZER.fit_transform(DOCS)

st.markdown("""
<style>
.block-container {max-width: 900px; padding-top: 2rem;}
.small {color:#666; font-size:.88rem;}
.answer {padding: 1rem 1.1rem; border:1px solid #ddd; border-radius:14px; background:#fafafa;}
</style>
""", unsafe_allow_html=True)

st.title("📚 SBI Mutual Fund FactsBot")
st.caption("Groww • SBI Mutual Fund • Facts-only RAG prototype")

st.info("**Facts-only. No investment advice.** Ask about SBI Large Cap Fund, SBI Flexicap Fund or SBI ELSS Tax Saver Fund. Do not enter PAN, Aadhaar, OTP, account numbers, email addresses or phone numbers.")

examples = [
    "What is the exit load of SBI Large Cap Fund?",
    "What is the minimum SIP for SBI ELSS Tax Saver Fund?",
    "What is the benchmark of SBI Flexicap Fund?"
]
st.write("**Try:**")
cols = st.columns(3)
for i, q in enumerate(examples):
    if cols[i].button(q, use_container_width=True):
        st.session_state["question"] = q

q = st.text_input("Your question", value=st.session_state.get("question",""), placeholder="e.g. What is the expense ratio of SBI Flexicap Fund?")
if q:
    PII_PATTERNS = [
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", r"\b\d{12}\b", r"\b\d{10,18}\b",
        r"\b\d{6,}\b", r"\b[\w\.-]+@[\w\.-]+\.\w+\b", r"(?<!\d)\+?\d[\d\s-]{9,14}\b"
    ]
    if any(re.search(p, q, flags=re.I) for p in PII_PATTERNS):
        st.warning("I can’t process or store personal/financial identifiers. Please ask the factual mutual-fund question without PAN, Aadhaar, OTP, account, email or phone details.")
        st.stop()

    advice_terms = [
        "should i buy","should i invest","should i sell","should i redeem","best fund",
        "which fund is best","best mutual fund","recommend","recommendation","worth buying",
        "good investment","where should i invest","portfolio","allocate","allocation",
        "buy or sell","switch to","which is better","better fund","guaranteed return"
    ]
    if any(t in q.lower() for t in advice_terms):
        st.warning("I’m a facts-only assistant, so I can’t recommend, rank, or tell you whether to buy, sell, switch, or choose a fund. I can provide factual details such as expense ratio, exit load, minimum SIP, lock-in, benchmark and riskometer.")
        st.markdown("[Official SBI Mutual Fund investor information](https://www.sbimf.com/)")
        st.stop()

    query_vec = VECTORIZER.transform([q])
    scores = cosine_similarity(query_vec, MATRIX)[0]
    top_idx = scores.argsort()[::-1][:5]
    selected = [CORPUS[i] for i in top_idx if scores[i] >= 0.10][:3]

    if not selected:
        st.warning("I couldn’t find enough supporting evidence in the curated official-source corpus. Please ask a narrower factual question about the three in-scope schemes.")
        st.stop()

    # Lightweight evidence gate: require query overlap with retrieved evidence.
    q_tokens = set(re.findall(r"[a-zA-Z]{3,}", q.lower()))
    evidence_text = " ".join(x["text"].lower() for x in selected)
    overlap = len(q_tokens.intersection(set(re.findall(r"[a-zA-Z]{3,}", evidence_text))))
    if overlap < 2:
        st.warning("I don’t have enough grounded evidence to answer that from the approved corpus.")
        st.stop()

    # Deterministic factual answer generation keeps the prototype citation-grounded
    # and avoids unsupported model hallucinations.
    ql = q.lower()
    answer = None
    source = selected[0]

    def pick(scheme_name):
        for d in selected:
            if scheme_name.lower() in d["scheme"].lower() or scheme_name.lower() in d["text"].lower():
                return d
        return selected[0]

    if "expense" in ql or "ter" in ql:
        for name in ["SBI Large Cap Fund","SBI Flexicap Fund","SBI ELSS Tax Saver Fund"]:
            if name.lower() in ql:
                source = pick(name); break
        vals = {
            "SBI Large Cap Fund":"1.47% Regular Plan and 0.79% Direct Plan",
            "SBI Flexicap Fund":"1.66% Regular Plan and 0.82% Direct Plan",
            "SBI ELSS Tax Saver Fund":"1.57% Regular Plan and 0.92% Direct Plan"
        }
        for name,val in vals.items():
            if name.lower() in ql:
                answer=f"The February 2026 SBI MF TER document lists the expense ratio for {name} as {val}. This figure is dated 28 February 2026."
                source=next(d for d in CORPUS if d["id"]=="ter_feb_2026"); break

    elif "exit load" in ql:
        if "large cap" in ql:
            answer="SBI Large Cap Fund has an exit load of 0.25% within 30 days, 0.10% after 30 days and within 90 days, and nil after 90 days from allotment."
            source=pick("SBI Large Cap Fund")
        elif "flexicap" in ql or "flexi cap" in ql:
            answer="SBI Flexicap Fund has an exit load of 0.10% for exit on or before 30 days from allotment and nil after 30 days."
            source=pick("SBI Flexicap Fund")
        elif "elss" in ql:
            answer="SBI ELSS Tax Saver Fund has no exit load (NIL) according to the February 2026 factsheet."
            source=pick("SBI ELSS Tax Saver Fund")

    elif "lock" in ql:
        if "elss" in ql:
            answer="SBI ELSS Tax Saver Fund has a statutory lock-in period of 3 years from the date of allotment."
            source=pick("SBI ELSS Tax Saver Fund")
        else:
            answer="The 3-year statutory lock-in in this corpus applies to SBI ELSS Tax Saver Fund; SBI Large Cap Fund and SBI Flexicap Fund are not identified as having that ELSS lock-in in the cited scheme factsheets."

    elif "benchmark" in ql:
        if "large cap" in ql:
            answer="The first-tier benchmark for SBI Large Cap Fund is BSE 100 (TRI)."; source=pick("SBI Large Cap Fund")
        elif "flexicap" in ql or "flexi cap" in ql:
            answer="The first-tier benchmark for SBI Flexicap Fund is BSE 500 (TRI)."; source=pick("SBI Flexicap Fund")
        elif "elss" in ql:
            answer="The first-tier benchmark for SBI ELSS Tax Saver Fund is BSE 500 (TRI)."; source=pick("SBI ELSS Tax Saver Fund")

    elif "minimum sip" in ql or ("sip" in ql and "minimum" in ql):
        if "large cap" in ql:
            answer="For SBI Large Cap Fund, the minimum SIP depends on frequency; the factsheet lists ₹1,000 monthly (or ₹500 under the stated one-year installment condition), ₹1,500 quarterly, ₹3,000 semi-annually and ₹5,000 annually."
            source=pick("SBI Large Cap Fund")
        elif "flexicap" in ql or "flexi cap" in ql:
            answer="For SBI Flexicap Fund, the factsheet lists ₹500 or ₹1,000 minimums depending on frequency and installment condition; quarterly is ₹1,500, semi-annual ₹3,000 and annual ₹5,000."
            source=pick("SBI Flexicap Fund")
        elif "elss" in ql:
            answer="SBI ELSS Tax Saver Fund has a minimum SIP amount of ₹500, in multiples of ₹500, for the stated SIP frequencies."
            source=pick("SBI ELSS Tax Saver Fund")

    elif "minimum investment" in ql or "minimum amount" in ql:
        if "large cap" in ql:
            answer="The minimum investment in SBI Large Cap Fund is ₹5,000, with additional investments from ₹1,000."
            source=pick("SBI Large Cap Fund")
        elif "flexicap" in ql or "flexi cap" in ql:
            answer="The minimum investment in SBI Flexicap Fund is ₹1,000, with additional investments from ₹1,000."
            source=pick("SBI Flexicap Fund")
        elif "elss" in ql:
            answer="The minimum investment in SBI ELSS Tax Saver Fund is ₹500, with additional investments from ₹500."
            source=pick("SBI ELSS Tax Saver Fund")

    elif "riskometer" in ql or "risk" in ql:
        if "large cap" in ql:
            answer="The SBI Large Cap Fund factsheet shows the scheme riskometer as Very High."
            source=pick("SBI Large Cap Fund")
        elif "flexicap" in ql or "flexi cap" in ql:
            answer="The SBI Flexicap Fund factsheet shows the scheme riskometer as Very High."
            source=pick("SBI Flexicap Fund")
        elif "elss" in ql:
            answer="The SBI ELSS Tax Saver Fund factsheet shows the scheme riskometer as Very High."
            source=pick("SBI ELSS Tax Saver Fund")
        else:
            answer="SEBI describes the Riskometer as a standardized tool showing a mutual-fund scheme's risk level from Low to Very High."
            source=next(d for d in CORPUS if d["id"]=="sebi_riskometer")

    elif "statement" in ql or "capital gain" in ql or "capital gains" in ql:
        answer="SBI Mutual Fund says investors can access Account Statement, Capital Gains Statement and Smart Statement through its investor services. Use the official SBI MF statement page rather than entering any personal details into this chatbot."
        source=next(d for d in CORPUS if d["id"]=="sbi_ways_to_invest")

    else:
        answer=None

    if not answer:
        st.info("I can answer supported facts such as expense ratio, exit load, minimum SIP/investment, ELSS lock-in, benchmark, riskometer, NAV navigation and statement-download navigation.")
        source=selected[0]
        answer="The approved corpus contains official SBI Mutual Fund information for these topics, but I need a narrower factual question to give a grounded answer."

    st.markdown('<div class="answer">', unsafe_allow_html=True)
    st.write(answer)
    st.markdown(f"**Source:** [{source['title']}]({source['url']})")
    st.markdown(f"**Last updated from sources:** {source['updated']}")
    st.markdown('</div>', unsafe_allow_html=True)
