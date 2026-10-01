import json, re
from pathlib import Path
from datetime import datetime

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="SBI MF FactsBot",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE = Path(__file__).parent
CORPUS = json.loads((BASE / "data" / "corpus.json").read_text(encoding="utf-8"))
DOCS = [d["text"] for d in CORPUS]

VECTORIZER = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    sublinear_tf=True,
)
MATRIX = VECTORIZER.fit_transform(DOCS)

OFFICIAL_LINKS = [
    ("📄", "Factsheets", "Monthly scheme factsheets & portfolio details", "https://www.sbimf.com/factsheets"),
    ("◈", "Total Expense Ratio", "Current & historical TER disclosures", "https://www.sbimf.com/total-expense-ratio"),
    ("▣", "SID / KIM", "Official scheme documents", "https://www.sbimf.com/offer-document-sid-kim"),
    ("↗", "Statements", "Account & capital-gains statement navigation", "https://www.sbimf.com/ways-to-invest"),
    ("◎", "SBI Mutual Fund", "Official AMC website", "https://www.sbimf.com/"),
]

st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root{
 --bg:#06110c; --panel:#0b1710; --panel2:#0f2016; --line:#203a29;
 --text:#f3fbf6; --muted:#91a99a; --green:#45f29a; --green2:#19c978;
 --lime:#b5ff69; --blue:#70b8ff;
}

.stApp{
 background:
 radial-gradient(circle at 10% 12%, rgba(69,242,154,.13), transparent 24%),
 radial-gradient(circle at 88% 18%, rgba(112,184,255,.10), transparent 23%),
 radial-gradient(circle at 50% 95%, rgba(181,255,105,.07), transparent 28%),
 var(--bg);
 color:var(--text);
 overflow-x:hidden;
}
.stApp:before{
 content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
 background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),
 linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);
 background-size:42px 42px;
 mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),transparent 82%);
}
.stApp:after{
 content:""; position:fixed; width:360px; height:360px; border-radius:50%;
 left:-150px; top:52%; pointer-events:none; z-index:0;
 background:rgba(69,242,154,.06); filter:blur(40px);
 animation:drift 9s ease-in-out infinite alternate;
}
@keyframes drift{from{transform:translate3d(0,0,0)}to{transform:translate3d(170px,-80px,0)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(69,242,154,.0)}50%{box-shadow:0 0 0 8px rgba(69,242,154,.06)}}
@keyframes shimmer{0%{background-position:0% 50%}100%{background-position:100% 50%}}

.block-container{
 max-width:980px; padding:24px 20px 80px; position:relative; z-index:1;
}
#MainMenu,footer,header{visibility:hidden}
*{font-family:"DM Sans",sans-serif}

.topbar{
 display:flex; align-items:center; justify-content:space-between; margin-bottom:14px;
}
.brand{font-family:"Space Grotesk",sans-serif;font-weight:700;font-size:14px;color:#eafff1}
.brand-dot{
 display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);
 margin-right:7px;box-shadow:0 0 16px rgba(69,242,154,.8);animation:pulse 2.2s infinite;
}
.live{
 color:#82f4b1;background:rgba(69,242,154,.07);border:1px solid rgba(69,242,154,.24);
 border-radius:999px;padding:6px 10px;font-size:9px;font-weight:800;letter-spacing:.8px;
}

.hero{
 position:relative;overflow:hidden;border:1px solid #21432e;border-radius:28px;padding:34px;
 background:
 radial-gradient(circle at 86% 20%,rgba(69,242,154,.13),transparent 27%),
 linear-gradient(135deg,#0b1b11,#10271a 56%,#0a1510);
 box-shadow:0 30px 90px rgba(0,0,0,.34);
}
.hero-orb{position:absolute;border-radius:50%;pointer-events:none;opacity:.7}
.orb1{width:170px;height:170px;right:-65px;top:-80px;border:1px solid rgba(69,242,154,.20);animation:floaty 6s ease-in-out infinite}
.orb2{width:90px;height:90px;right:105px;bottom:-45px;border:1px solid rgba(112,184,255,.18);animation:floaty 7s ease-in-out infinite reverse}
.eyebrow{
 display:inline-flex;align-items:center;gap:7px;color:#8af7b7;font-size:9px;font-weight:900;
 letter-spacing:1.2px;text-transform:uppercase;background:rgba(69,242,154,.07);
 border:1px solid rgba(69,242,154,.20);border-radius:999px;padding:7px 10px;
}
.hero h1{
 font-family:"Space Grotesk",sans-serif;color:#fff!important;font-size:42px;line-height:1.02;
 letter-spacing:-1.4px;margin:14px 0 10px;position:relative;
}
.hero p{color:#b8cdbf!important;font-size:13px;line-height:1.6;max-width:720px;position:relative}
.pills{display:flex;gap:7px;flex-wrap:wrap;margin-top:20px;position:relative}
.pill{
 color:#d9ebe0;background:rgba(255,255,255,.045);border:1px solid #2b4435;
 border-radius:999px;padding:7px 10px;font-size:9px;font-weight:600;
}
.pill.livepill{color:#8ff5b7;border-color:rgba(69,242,154,.25);background:rgba(69,242,154,.06)}

.fresh{
 margin-top:14px;display:flex;align-items:center;justify-content:space-between;gap:12px;
 padding:10px 12px;border-radius:14px;background:rgba(255,255,255,.035);
 border:1px solid #1f3628;color:#7f9788;font-size:9px;
}
.fresh b{color:#d7e9dd}
.fresh .status{color:#7df2aa}

.section{margin-top:27px}
.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:11px}
.head h3{font-family:"Space Grotesk",sans-serif;font-size:17px;color:#eff9f2!important;margin:0}
.head span{font-size:9px;font-weight:800;letter-spacing:.8px;color:#66806e}

.scheme-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.scheme{
 min-height:84px;padding:15px;border-radius:17px;background:rgba(11,23,16,.82);
 border:1px solid #20392a;box-shadow:0 12px 30px rgba(0,0,0,.15);
 transition:.22s ease;position:relative;overflow:hidden;
}
.scheme:after{content:"";position:absolute;width:80px;height:80px;border-radius:50%;right:-40px;bottom:-50px;background:rgba(69,242,154,.06)}
.scheme:hover{transform:translateY(-3px);border-color:#37664a;box-shadow:0 18px 38px rgba(0,0,0,.25)}
.scheme-num{color:#57eda0!important;font-size:9px;font-weight:900;letter-spacing:1px}
.scheme-name{color:#f1f8f3!important;-webkit-text-fill-color:#f1f8f3!important;font-size:12px;font-weight:700;line-height:1.35;margin-top:7px}

.notice{
 margin-top:11px;padding:12px 14px;border-radius:14px;
 background:linear-gradient(90deg,rgba(69,242,154,.065),rgba(69,242,154,.025));
 border:1px solid rgba(69,242,154,.20);color:#a7c1b0!important;font-size:10.5px;line-height:1.5;
}
.notice b{color:#8af3b5!important}

.ask{margin-top:30px}
.ask-title{font-family:"Space Grotesk",sans-serif;font-size:21px;font-weight:700;color:#f4fbf6!important}
.ask-sub{font-size:11px;color:#71897a!important;margin:3px 0 12px}

.quick-wrap{margin-bottom:9px}
div.stButton>button{
 background:rgba(14,29,20,.85)!important;color:#b9cdbf!important;
 border:1px solid #243e2e!important;border-radius:13px!important;min-height:42px!important;
 font-size:10px!important;font-weight:700!important;box-shadow:0 8px 20px rgba(0,0,0,.16)!important;
 transition:.2s ease!important;
}
div.stButton>button:hover{
 background:rgba(69,242,154,.08)!important;color:#8cf4b6!important;
 border-color:#39714f!important;transform:translateY(-2px);
}
div.stButton>button:focus{box-shadow:0 0 0 2px rgba(69,242,154,.12)!important}

div[data-testid="stTextInput"] label{display:none!important}
div[data-testid="stTextInput"]>div>div{
 background:rgba(10,20,14,.94)!important;border:1px solid #31533e!important;border-radius:19px!important;
 box-shadow:0 18px 45px rgba(0,0,0,.28),0 0 0 1px rgba(69,242,154,.03)!important;
 min-height:58px!important;transition:.22s ease!important;
}
div[data-testid="stTextInput"]>div>div:focus-within{
 border:1px solid #45f29a!important;
 box-shadow:0 0 0 4px rgba(69,242,154,.08),0 20px 55px rgba(0,0,0,.34)!important;
 transform:translateY(-2px);
}
div[data-testid="stTextInput"] input{
 color:#f4fbf6!important;-webkit-text-fill-color:#f4fbf6!important;background:transparent!important;
 caret-color:#45f29a!important;border:0!important;outline:0!important;box-shadow:none!important;
 font-size:13px!important;padding-left:5px!important;
}
div[data-testid="stTextInput"] input::placeholder{color:#607567!important;-webkit-text-fill-color:#607567!important}

.answer{
 margin-top:18px;background:linear-gradient(145deg,#0d1c13,#0a1610);
 border:1px solid #244530;border-radius:22px;padding:21px;
 box-shadow:0 20px 55px rgba(0,0,0,.28);animation:floaty 5s ease-in-out infinite;
}
.answer-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:11px}
.answer-label{color:#62f1a2!important;font-size:9px;font-weight:900;letter-spacing:1px;text-transform:uppercase}
.grounded{color:#667f6d!important;font-size:9px}
.answer-text{color:#edf7f0!important;font-size:15px;line-height:1.7}
.source{
 margin-top:16px;padding:13px;border-radius:14px;background:#08120c;border:1px solid #1f3526;
}
.source-k{font-size:8px;color:#6f8877!important;text-transform:uppercase;letter-spacing:.8px;font-weight:800}
.source-name{font-size:11px;font-weight:700;color:#d7e9dc!important;margin-top:4px}
.source-date{font-size:9px;color:#718979!important;margin-top:4px}
.source-badge{
 display:inline-block;margin-top:8px;padding:5px 7px;border-radius:999px;
 color:#82efae;background:rgba(69,242,154,.06);border:1px solid rgba(69,242,154,.16);font-size:8px;font-weight:800;
}
.open-source{display:inline-block;margin-top:12px;color:#76f2aa!important;font-size:10px;font-weight:800;text-decoration:none}

.resource-title{
 margin-top:23px;color:#edf8f1;font-family:"Space Grotesk",sans-serif;font-size:15px;font-weight:700;
}
.resource-sub{font-size:10px;color:#6e8576;margin-top:2px;margin-bottom:9px}
.resources{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.resource{
 display:block;padding:12px 13px;border-radius:14px;text-decoration:none!important;
 background:rgba(12,25,17,.72);border:1px solid #1f3828;transition:.2s ease;
}
.resource:hover{border-color:#3d7652;transform:translateY(-2px);background:rgba(69,242,154,.055)}
.resource-icon{font-size:13px}
.resource-name{color:#dcece2;font-size:10px;font-weight:800;margin-top:5px}
.resource-desc{color:#6f8777;font-size:8.5px;line-height:1.4;margin-top:2px}


.related-title{margin-top:22px;color:#edf8f1!important;font-family:"Space Grotesk",sans-serif;font-size:14px;font-weight:700}
.related-sub{font-size:9.5px;color:#718979!important;margin-top:3px;margin-bottom:9px}
.related-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-top:8px}
.related-note{margin-top:8px;color:#5f7667!important;font-size:8.5px}
.pipeline-title{margin-top:21px;color:#718979!important;font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:800}
.pipeline{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:8px}
.node{font-size:8px;color:#789080!important;background:#0b1710;border:1px solid #20392a;border-radius:999px;padding:6px 8px}
.node.active{color:#82efae!important;background:rgba(69,242,154,.055);border-color:rgba(69,242,154,.20)}
.arrow{font-size:9px;color:#3f5b48!important}

.bottom{
 margin-top:32px;padding-top:15px;border-top:1px solid #172b1e;
 display:flex;justify-content:space-between;color:#52685a!important;font-size:9px;
}
.bottom strong{color:#76917e!important}

@media(max-width:700px){
 .scheme-grid,.resources{grid-template-columns:1fr}
 .hero h1{font-size:31px}.hero{padding:25px}
 .fresh{align-items:flex-start;flex-direction:column}
 .bottom{flex-direction:column;gap:8px}
}
</style>
""", unsafe_allow_html=True)

def contains_pii(t):
    return any(re.search(p,t,re.I) for p in [r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',r'\b\d{12}\b',r'\b\d{10,18}\b',r'\b[\w\.-]+@[\w\.-]+\.\w+\b',r'(?<!\d)\+?\d[\d\s-]{9,14}\b'])

def is_advice(t):
    terms=['should i buy','should i invest','should i sell','should i redeem','best fund','which fund is best','best mutual fund','recommend','recommendation','worth buying','good investment','where should i invest','portfolio','allocate','allocation','buy or sell','switch to','which is better','better fund','guaranteed return']
    return any(x in t.lower() for x in terms)

def retrieve(q):
    v=VECTORIZER.transform([q]); scores=cosine_similarity(v,MATRIX)[0]
    return [(CORPUS[i],float(scores[i])) for i in scores.argsort()[::-1][:5] if scores[i]>=.08]

def pick(scheme,docs):
    for d,_ in docs:
        if scheme.lower() in d['scheme'].lower() or scheme.lower() in d['text'].lower(): return d
    return next((d for d in CORPUS if scheme.lower() in d['scheme'].lower()),docs[0][0] if docs else CORPUS[0])

def answer(q,docs):
    t=q.lower()
    if ('lock' in t or 'lock-in' in t or 'lock in' in t or 'fixed time' in t) and 'elss' in t:return 'SBI ELSS Tax Saver Fund has a statutory lock-in period of 3 years from the date of allotment.',pick('SBI ELSS Tax Saver Fund',docs)
    if 'expense' in t or 'ter' in t:
        vals={'large cap':('SBI Large Cap Fund','1.47% for the Regular Plan and 0.79% for the Direct Plan.'),'flexicap':('SBI Flexicap Fund','1.66% for the Regular Plan and 0.82% for the Direct Plan.'),'flexi cap':('SBI Flexicap Fund','1.66% for the Regular Plan and 0.82% for the Direct Plan.'),'elss':('SBI ELSS Tax Saver Fund','1.57% for the Regular Plan and 0.92% for the Direct Plan.')}
        for k,(s,v) in vals.items():
            if k in t:return f'The February 2026 SBI MF TER document lists the expense ratio for {s} as {v}',next(d for d in CORPUS if d['id']=='ter_feb_2026')
    if 'exit load' in t:
        if 'large cap' in t:return 'SBI Large Cap Fund has an exit load of 0.25% within 30 days, 0.10% after 30 days and within 90 days, and nil after 90 days from allotment.',pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:return 'SBI Flexicap Fund has an exit load of 0.10% for exit on or before 30 days from allotment and nil after 30 days.',pick('SBI Flexicap Fund',docs)
        if 'elss' in t:return 'SBI ELSS Tax Saver Fund has no exit load (NIL) according to the February 2026 factsheet.',pick('SBI ELSS Tax Saver Fund',docs)
    if 'benchmark' in t:
        if 'large cap' in t:return 'The first-tier benchmark for SBI Large Cap Fund is BSE 100 (TRI).',pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:return 'The first-tier benchmark for SBI Flexicap Fund is BSE 500 (TRI).',pick('SBI Flexicap Fund',docs)
        if 'elss' in t:return 'The first-tier benchmark for SBI ELSS Tax Saver Fund is BSE 500 (TRI).',pick('SBI ELSS Tax Saver Fund',docs)
    if 'minimum' in t and 'sip' in t:
        if 'large cap' in t:return 'For SBI Large Cap Fund, the minimum SIP depends on frequency; the factsheet lists ₹1,000 monthly (or ₹500 under the stated one-year installment condition), ₹1,500 quarterly, ₹3,000 semi-annually and ₹5,000 annually.',pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:return 'For SBI Flexicap Fund, the factsheet lists ₹500 or ₹1,000 minimums depending on frequency and installment condition; quarterly is ₹1,500, semi-annual ₹3,000 and annual ₹5,000.',pick('SBI Flexicap Fund',docs)
        if 'elss' in t:return 'SBI ELSS Tax Saver Fund has a minimum SIP amount of ₹500, in multiples of ₹500, for the stated SIP frequencies.',pick('SBI ELSS Tax Saver Fund',docs)
    if 'minimum investment' in t or 'minimum amount' in t:
        if 'large cap' in t:return 'The minimum investment in SBI Large Cap Fund is ₹5,000, with additional investments from ₹1,000.',pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:return 'The minimum investment in SBI Flexicap Fund is ₹1,000, with additional investments from ₹1,000.',pick('SBI Flexicap Fund',docs)
        if 'elss' in t:return 'The minimum investment in SBI ELSS Tax Saver Fund is ₹500, with additional investments from ₹500.',pick('SBI ELSS Tax Saver Fund',docs)
    if 'riskometer' in t or ('risk' in t and any(x in t for x in ['large cap','flexicap','elss'])):
        if 'large cap' in t:return 'The SBI Large Cap Fund factsheet shows the scheme riskometer as Very High.',pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:return 'The SBI Flexicap Fund factsheet shows the scheme riskometer as Very High.',pick('SBI Flexicap Fund',docs)
        if 'elss' in t:return 'The SBI ELSS Tax Saver Fund factsheet shows the scheme riskometer as Very High.',pick('SBI ELSS Tax Saver Fund',docs)
    if 'statement' in t or 'capital gain' in t or 'capital gains' in t:return 'SBI Mutual Fund says investors can access Account Statement, Capital Gains Statement and Smart Statement through its investor services.',next(d for d in CORPUS if d['id']=='sbi_ways_to_invest')
    return None



def related_questions(q):
    t=q.lower()
    scheme = None
    if 'large cap' in t:
        scheme = 'SBI Large Cap Fund'
    elif 'flexicap' in t or 'flexi cap' in t:
        scheme = 'SBI Flexicap Fund'
    elif 'elss' in t:
        scheme = 'SBI ELSS Tax Saver Fund'

    if any(x in t for x in ['expense ratio','ter']):
        topics = [('Exit load', 'What is the exit load of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Benchmark', 'What is the benchmark of {s}?'), ('Riskometer', 'What is the riskometer of {s}?')]
    elif 'exit load' in t:
        topics = [('Expense ratio', 'What is the expense ratio of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Minimum investment', 'What is the minimum investment in {s}?'), ('Benchmark', 'What is the benchmark of {s}?')]
    elif 'lock' in t and 'elss' in t:
        topics = [('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Minimum investment', 'What is the minimum investment in {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Riskometer', 'What is the riskometer of {s}?')]
    elif 'benchmark' in t:
        topics = [('Riskometer', 'What is the riskometer of {s}?'), ('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Minimum investment', 'What is the minimum investment in {s}?')]
    elif 'riskometer' in t or ('risk' in t and scheme):
        topics = [('Benchmark', 'What is the benchmark of {s}?'), ('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?')]
    elif 'minimum sip' in t or ('minimum' in t and 'sip' in t):
        topics = [('Minimum investment', 'What is the minimum investment in {s}?'), ('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Benchmark', 'What is the benchmark of {s}?')]
    elif 'minimum investment' in t or 'minimum amount' in t:
        topics = [('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Benchmark', 'What is the benchmark of {s}?')]
    elif 'statement' in t or 'capital gain' in t:
        topics = [('Account statement', 'Where can I access my SBI Mutual Fund account statement?'), ('Capital gains', 'Where can I access my SBI Mutual Fund capital gains statement?'), ('Smart Statement', 'What is the SBI Mutual Fund Smart Statement?'), ('Factsheets', 'Where can I find SBI Mutual Fund factsheets?')]
    else:
        topics = [('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Benchmark', 'What is the benchmark of {s}?')]

    if scheme:
        return [(label, text.format(s=scheme)) for label, text in topics]
    return [(label, text) for label, text in topics]


# ---------- PRODUCT UI ----------
st.markdown("""
<div class="topbar">
  <div class="brand"><span class="brand-dot"></span> SBI MF FactsBot</div>
  <div class="live">● LIVE · FACTS ONLY</div>
</div>

<div class="hero">
  <div class="hero-orb orb1"></div>
  <div class="hero-orb orb2"></div>
  <div class="eyebrow">✦ Retrieval-Augmented FAQ Assistant</div>
  <h1>Mutual fund facts,<br>without the noise.</h1>
  <p>Ask a precise question about selected SBI Mutual Fund schemes and get a concise answer grounded in official public sources.</p>
  <div class="pills">
    <span class="pill livepill">20 official sources</span>
    <span class="pill">SBI Mutual Fund</span>
    <span class="pill">3 schemes</span>
    <span class="pill">Facts-only</span>
  </div>
  <div class="fresh">
    <span>DATA FRESHNESS · <b>Source document dates are shown with every answer</b></span>
    <span class="status">✓ Official public sources</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="section">
  <div class="head"><h3>Knowledge scope</h3><span>CURATED CORPUS</span></div>
  <div class="scheme-grid">
    <div class="scheme"><div class="scheme-num">SCHEME 01</div><div class="scheme-name">SBI Large Cap Fund</div></div>
    <div class="scheme"><div class="scheme-num">SCHEME 02</div><div class="scheme-name">SBI Flexicap Fund</div></div>
    <div class="scheme"><div class="scheme-num">SCHEME 03</div><div class="scheme-name">SBI ELSS Tax Saver Fund</div></div>
  </div>
  <div class="notice"><b>Facts-only · No investment advice.</b> Ask about expense ratio, exit load, minimum SIP/investment, ELSS lock-in, benchmark, riskometer or statement navigation. Never enter PAN, Aadhaar, OTP, account numbers, email addresses or phone numbers.</div>
</div>

<div class="ask">
  <div class="ask-title">What do you want to know?</div>
  <div class="ask-sub">Choose a common fact or search the curated official corpus.</div>
</div>
""", unsafe_allow_html=True)

examples = [
    ("↗  Exit load", "What is the exit load of SBI Large Cap Fund?"),
    ("◈  ELSS lock-in", "What is the lock-in period of SBI ELSS Tax Saver Fund?"),
    ("◇  Benchmark", "What is the benchmark of SBI Flexicap Fund?"),
]
cols = st.columns(3)
for i, (label, q) in enumerate(examples):
    if cols[i].button(label, key=f"example_{i}", use_container_width=True):
        st.session_state["question"] = q
        st.rerun()

question = st.text_input(
    "Question",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What is the expense ratio of SBI Flexicap Fund?",
    label_visibility="collapsed",
)

if question:
    st.session_state["question"] = question

    if contains_pii(question):
        st.error("For privacy, I can’t process personal or financial identifiers. Ask the mutual-fund fact without PAN, Aadhaar, OTP, account, email or phone details.")
        st.stop()

    if is_advice(question):
        st.markdown("""
        <div class="answer">
          <div class="answer-top">
            <div class="answer-label">● Facts-only boundary</div>
            <div class="grounded">SAFE RESPONSE</div>
          </div>
          <div class="answer-text">I can’t recommend, rank, or tell you whether to buy, sell, switch or choose a fund. I can provide factual details such as expense ratio, exit load, minimum SIP, lock-in, benchmark and riskometer.</div>
          <div class="source">
            <div class="source-k">Official source</div>
            <div class="source-name">SBI Mutual Fund — Disclaimer</div>
            <div class="source-date">Official public source</div>
            <div class="source-badge">FACTS · NOT ADVICE</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("[Open official disclaimer ↗](https://www.sbimf.com/disclaimer)")
        st.stop()

    retrieved = retrieve(question)
    result = answer(question, retrieved)

    if not result:
        st.info("I don’t have enough grounded evidence for that question. Try expense ratio, exit load, minimum SIP/investment, ELSS lock-in, benchmark, riskometer or statement navigation.")
        st.stop()

    answer_text, source = result
    source_date = source.get("updated", "Date not stated on source page")

    st.markdown(
        f"""
        <div class="answer">
          <div class="answer-top">
            <div class="answer-label">● Grounded answer</div>
            <div class="grounded">RAG · OFFICIAL SOURCE</div>
          </div>
          <div class="answer-text">{answer_text}</div>

          <div class="source">
            <div class="source-k">Source evidence</div>
            <div class="source-name">{source["title"]}</div>
            <div class="source-date">Source document / page date: <b>{source_date}</b></div>
            <div class="source-badge">✓ OFFICIAL SBI MUTUAL FUND SOURCE</div>
          </div>

          <a class="open-source" href="{source["url"]}" target="_blank">Open this exact source ↗</a>
        </div>

        </div>

        <div class="pipeline-title">How this answer was grounded</div>
        <div class="pipeline">
          <span class="node">User query</span><span class="arrow">→</span>
          <span class="node">PII check</span><span class="arrow">→</span>
          <span class="node active">TF-IDF retrieval</span><span class="arrow">→</span>
          <span class="node active">Evidence gate</span><span class="arrow">→</span>
          <span class="node active">Cited answer</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    related = related_questions(question)
    st.markdown(
        '<div class="related-title">Still exploring this? 👇</div>'
        '<div class="related-sub">Related factual questions — informational only. No recommendations or trading advice.</div>',
        unsafe_allow_html=True,
    )
    rcols = st.columns(2)
    for i, (label, rq) in enumerate(related):
        if rcols[i % 2].button(f"{label}  →", key=f"related_{i}_{hash(question)}", use_container_width=True):
            st.session_state["question"] = rq
            st.rerun()
    st.markdown('<div class="related-note">These suggestions stay within the facts-only scope of the selected official sources.</div>', unsafe_allow_html=True)

    # Separate official links section — not mixed into the answer.
    st.markdown("""
    <div class="resource-title">More official information</div>
    <div class="resource-sub">Useful source pages to verify or explore the same topic.</div>
    <div class="resources">
    """, unsafe_allow_html=True)

    # Render two-column HTML cards as links.
    cards = []
    for icon, name, desc, url in OFFICIAL_LINKS:
        cards.append(
            f'<a class="resource" href="{url}" target="_blank">'
            f'<div class="resource-icon">{icon}</div>'
            f'<div class="resource-name">{name} ↗</div>'
            f'<div class="resource-desc">{desc}</div>'
            f'</a>'
        )
    st.markdown("".join(cards) + "</div>", unsafe_allow_html=True)

    st.caption(f"Last updated from sources: {source_date}")

st.markdown("""
<div class="bottom">
  <div><strong>RAG FAQ Prototype</strong><br>Groww · SBI Mutual Fund · Facts-only</div>
  <div><strong>Transparency</strong><br>Source date shown · Official links · No PII storage · No investment advice</div>
</div>
""", unsafe_allow_html=True)
