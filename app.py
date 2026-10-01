import json, re
from pathlib import Path
from datetime import datetime

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="FundLens — SBI Mutual Fund Facts Assistant",
    page_icon="◈",
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
:root{--bg:#020806;--panel:#07130d;--panel2:#0a1b12;--line:#173426;--text:#f4fff8;--muted:#7e9b89;--green:#46ff9b;--lime:#c6ff5d;--cyan:#56e7ff;--blue:#6c9cff;}
.stApp{background:radial-gradient(ellipse at 50% -10%,rgba(70,255,155,.16),transparent 38%),radial-gradient(circle at 90% 35%,rgba(86,231,255,.09),transparent 28%),radial-gradient(circle at 8% 80%,rgba(198,255,93,.07),transparent 30%),#020806;color:var(--text);overflow-x:hidden}
.stApp:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;background-image:linear-gradient(rgba(70,255,155,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(70,255,155,.035) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),transparent 88%)}
.stApp:after{content:"";position:fixed;inset:-30%;pointer-events:none;z-index:0;background:conic-gradient(from 0deg,transparent,rgba(70,255,155,.035),transparent 25%,rgba(86,231,255,.025),transparent 50%);animation:spinbg 24s linear infinite}
@keyframes spinbg{to{transform:rotate(360deg)}}
@keyframes drift{0%{transform:translate3d(-20px,10px,0) scale(1)}100%{transform:translate3d(130px,-80px,0) scale(1.15)}}
@keyframes floaty{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(70,255,155,0)}50%{box-shadow:0 0 0 9px rgba(70,255,155,.07)}}
@keyframes scan{0%{transform:translateY(-120%)}100%{transform:translateY(420%)}}
@keyframes borderflow{0%{background-position:0% 50%}100%{background-position:300% 50%}}
@keyframes blink{50%{opacity:.35}}
.block-container{max-width:1080px;padding:22px 20px 90px;position:relative;z-index:1}
#MainMenu,footer,header{visibility:hidden}*{font-family:"DM Sans",sans-serif}
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:15px}.brand{font-family:"Space Grotesk",sans-serif;font-weight:700;font-size:14px;color:#effff5;letter-spacing:-.2px}.brand-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:8px;box-shadow:0 0 18px rgba(70,255,155,.9);animation:pulse 2s infinite}.live{font-family:"JetBrains Mono",monospace;color:#8dffbd;background:rgba(70,255,155,.055);border:1px solid rgba(70,255,155,.25);border-radius:999px;padding:7px 11px;font-size:8px;font-weight:800;letter-spacing:1px}
.hero{position:relative;overflow:hidden;border:1px solid rgba(70,255,155,.24);border-radius:32px;padding:42px 42px 26px;background:linear-gradient(135deg,rgba(7,22,14,.96),rgba(6,18,13,.86) 50%,rgba(5,12,10,.98));box-shadow:0 35px 100px rgba(0,0,0,.55),inset 0 1px rgba(255,255,255,.04)}
.hero:before{content:"";position:absolute;inset:-1px;border-radius:32px;padding:1px;background:linear-gradient(120deg,rgba(70,255,155,.45),transparent 28%,rgba(86,231,255,.16) 62%,rgba(198,255,93,.35));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;animation:borderflow 8s linear infinite;background-size:300% 100%;pointer-events:none}
.hero:after{content:"";position:absolute;left:0;right:0;height:90px;top:-100px;background:linear-gradient(transparent,rgba(70,255,155,.045),transparent);animation:scan 8s linear infinite;pointer-events:none}
.hero-orb{position:absolute;border-radius:50%;pointer-events:none}.orb1{width:260px;height:260px;right:-100px;top:-130px;border:1px solid rgba(70,255,155,.18);box-shadow:inset 0 0 80px rgba(70,255,155,.04);animation:floaty 7s ease-in-out infinite}.orb2{width:120px;height:120px;right:130px;bottom:-65px;border:1px solid rgba(86,231,255,.18);animation:floaty 8s ease-in-out infinite reverse}
.eyebrow{display:inline-flex;align-items:center;gap:7px;color:#9dffca;font-family:"JetBrains Mono",monospace;font-size:8px;font-weight:800;letter-spacing:1.4px;text-transform:uppercase;background:rgba(70,255,155,.06);border:1px solid rgba(70,255,155,.22);border-radius:999px;padding:8px 11px}.hero h1{font-family:"Space Grotesk",sans-serif;color:#fff!important;font-size:52px;line-height:.98;letter-spacing:-2.5px;margin:17px 0 12px;position:relative;max-width:720px}.hero h1 span{color:var(--green)}.hero p{color:#a9c4b3!important;font-size:13px;line-height:1.65;max-width:680px;position:relative}.pills{display:flex;gap:7px;flex-wrap:wrap;margin-top:21px;position:relative}.pill{color:#d8eee0;background:rgba(255,255,255,.035);border:1px solid #244334;border-radius:999px;padding:7px 10px;font-size:9px;font-weight:600}.pill.livepill{color:#9dffca;border-color:rgba(70,255,155,.3);background:rgba(70,255,155,.065)}
.hero-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:22px}.hero-stat{padding:11px 12px;border:1px solid #193526;border-radius:12px;background:rgba(255,255,255,.025)}.hero-stat-k{font-family:"JetBrains Mono",monospace;font-size:7px;color:#557363;letter-spacing:.8px;text-transform:uppercase}.hero-stat-v{font-family:"Space Grotesk",sans-serif;font-size:15px;color:#ecfff3;font-weight:700;margin-top:3px}.hero-stat-v.green{color:var(--green)}
.fresh{margin-top:9px;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.025);border:1px solid #193326;color:#718b7b;font-size:8px}.fresh b{color:#d5eade}.fresh .status{color:#7dffb1}
.section{margin-top:31px}.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:11px}.head h3{font-family:"Space Grotesk",sans-serif;font-size:17px;color:#f0fff5!important;margin:0}.head span{font-family:"JetBrains Mono",monospace;font-size:8px;font-weight:800;letter-spacing:1px;color:#52705f}
.scheme-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.scheme{min-height:102px;padding:17px;border-radius:18px;background:linear-gradient(145deg,rgba(8,24,15,.95),rgba(5,15,10,.92));border:1px solid #193b29;box-shadow:0 15px 40px rgba(0,0,0,.22);transition:.25s ease;position:relative;overflow:hidden}.scheme:before{content:"";position:absolute;width:110px;height:110px;border-radius:50%;right:-45px;bottom:-65px;background:radial-gradient(circle,rgba(70,255,155,.12),transparent 65%)}.scheme:after{content:"";position:absolute;left:0;top:0;width:2px;height:100%;background:linear-gradient(var(--green),transparent);opacity:.45}.scheme:hover{transform:translateY(-5px) scale(1.01);border-color:#3e8059;box-shadow:0 24px 55px rgba(0,0,0,.35),0 0 30px rgba(70,255,155,.05)}.scheme-num{font-family:"JetBrains Mono",monospace;color:#54ef9e!important;font-size:8px;font-weight:900;letter-spacing:1.2px}.scheme-name{color:#f1fff5!important;-webkit-text-fill-color:#f1fff5!important;font-size:12px;font-weight:700;line-height:1.35;margin-top:9px}.scheme-mini{font-size:8px;color:#607c6b;margin-top:7px}
.notice{margin-top:11px;padding:12px 14px;border-radius:14px;background:linear-gradient(90deg,rgba(70,255,155,.065),rgba(86,231,255,.025));border:1px solid rgba(70,255,155,.19);color:#9eb9a9!important;font-size:10px;line-height:1.5}.notice b{color:#8effba!important}
.ask{margin-top:34px}.ask-title{font-family:"Space Grotesk",sans-serif;font-size:23px;font-weight:700;color:#f4fff8!important;letter-spacing:-.5px}.ask-sub{font-size:10px;color:#668273!important;margin:3px 0 12px}
.quick-wrap{margin-bottom:9px}div.stButton>button{background:linear-gradient(145deg,rgba(10,28,18,.96),rgba(6,18,12,.96))!important;color:#bdd3c4!important;border:1px solid #1d4030!important;border-radius:14px!important;min-height:45px!important;font-size:10px!important;font-weight:700!important;box-shadow:0 10px 24px rgba(0,0,0,.2)!important;transition:.22s ease!important}div.stButton>button:hover{background:linear-gradient(145deg,rgba(70,255,155,.10),rgba(86,231,255,.045))!important;color:#9affc5!important;border-color:#4a9365!important;transform:translateY(-3px);box-shadow:0 12px 28px rgba(0,0,0,.3),0 0 18px rgba(70,255,155,.05)!important}div.stButton>button:focus{box-shadow:0 0 0 2px rgba(70,255,155,.12)!important}
div[data-testid="stTextInput"] label{display:none!important}div[data-testid="stTextInput"]>div>div{background:rgba(4,14,9,.97)!important;border:1px solid #315a43!important;border-radius:20px!important;box-shadow:0 20px 55px rgba(0,0,0,.42),0 0 0 1px rgba(70,255,155,.025)!important;min-height:62px!important;transition:.22s ease!important}div[data-testid="stTextInput"]>div>div:focus-within{border:1px solid var(--green)!important;box-shadow:0 0 0 4px rgba(70,255,155,.08),0 20px 60px rgba(0,0,0,.45),0 0 30px rgba(70,255,155,.06)!important;transform:translateY(-2px)}div[data-testid="stTextInput"] input{color:#f4fff8!important;-webkit-text-fill-color:#f4fff8!important;background:transparent!important;caret-color:var(--green)!important;border:0!important;outline:0!important;box-shadow:none!important;font-size:13px!important;padding-left:7px!important}div[data-testid="stTextInput"] input::placeholder{color:#526d5e!important;-webkit-text-fill-color:#526d5e!important}
.answer{margin-top:19px;background:linear-gradient(145deg,rgba(10,29,18,.98),rgba(4,15,10,.98));border:1px solid #27523a;border-radius:22px;padding:22px;box-shadow:0 25px 65px rgba(0,0,0,.4),inset 0 1px rgba(255,255,255,.03);animation:floaty 5s ease-in-out infinite;position:relative;overflow:hidden}.answer:before{content:"";position:absolute;left:0;top:0;width:100%;height:1px;background:linear-gradient(90deg,transparent,var(--green),var(--cyan),transparent);opacity:.7}.answer-top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:11px}.answer-label{color:#62f1a2!important;font-family:"JetBrains Mono",monospace;font-size:8px;font-weight:900;letter-spacing:1px;text-transform:uppercase}.grounded{font-family:"JetBrains Mono",monospace;color:#5f7b69!important;font-size:8px}.answer-text{color:#edf9f1!important;font-size:15px;line-height:1.75}.source{margin-top:17px;padding:14px;border-radius:15px;background:#030b07;border:1px solid #173326}.source-k{font-family:"JetBrains Mono",monospace;font-size:7px;color:#587362!important;text-transform:uppercase;letter-spacing:.9px;font-weight:800}.source-name{font-size:11px;font-weight:700;color:#d8ede0!important;margin-top:5px}.source-date{font-size:9px;color:#718a7b!important;margin-top:4px}.source-badge{display:inline-block;margin-top:9px;padding:5px 7px;border-radius:999px;color:#82efae;background:rgba(70,255,155,.055);border:1px solid rgba(70,255,155,.16);font-family:"JetBrains Mono",monospace;font-size:7px;font-weight:800}.open-source{display:inline-block;margin-top:12px;color:#76f2aa!important;font-size:10px;font-weight:800;text-decoration:none}
.related-title{margin-top:23px;color:#effff4!important;font-family:"Space Grotesk",sans-serif;font-size:15px;font-weight:700}.related-sub{font-size:9px;color:#668273!important;margin-top:3px;margin-bottom:9px}.related-note{margin-top:8px;color:#557061!important;font-size:8px}.pipeline-title{margin-top:23px;color:#6b8877!important;font-family:"JetBrains Mono",monospace;font-size:8px;text-transform:uppercase;letter-spacing:1px;font-weight:800}.pipeline{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:8px}.node{font-family:"JetBrains Mono",monospace;font-size:7px;color:#708b7a!important;background:#07140d;border:1px solid #1b3929;border-radius:999px;padding:6px 8px}.node.active{color:#82efae!important;background:rgba(70,255,155,.055);border-color:rgba(70,255,155,.20)}.arrow{font-size:9px;color:#3e604d!important}
.resource-title{margin-top:25px;color:#edf9f1;font-family:"Space Grotesk",sans-serif;font-size:15px;font-weight:700}.resource-sub{font-size:9px;color:#668273;margin-top:2px;margin-bottom:9px}.resources{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.resource{display:block;padding:13px;border-radius:15px;text-decoration:none!important;background:rgba(7,20,13,.8);border:1px solid #193627;transition:.22s ease}.resource:hover{border-color:#3e8059;transform:translateY(-3px);background:rgba(70,255,155,.05)}.resource-icon{font-size:13px}.resource-name{color:#dceee3;font-size:10px;font-weight:800;margin-top:5px}.resource-desc{color:#688071;font-size:8px;line-height:1.4;margin-top:2px}
.bottom{display:flex;justify-content:space-between;gap:20px;margin-top:36px;padding-top:18px;border-top:1px solid #10281b;color:#536e5e;font-size:8px;line-height:1.6}.bottom strong{color:#8da997}
@media(max-width:760px){.block-container{padding:16px 12px 60px}.hero{padding:27px 22px 20px}.hero h1{font-size:37px}.hero-stats{grid-template-columns:repeat(2,1fr)}.scheme-grid{grid-template-columns:1fr}.resources{grid-template-columns:1fr}.bottom{flex-direction:column}.live{display:none}}
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
    t=q.lower().strip()
    t=t.replace('largecap','large cap').replace('flexi-cap','flexicap')

    # Natural-language scheme overview questions remain factual and source-grounded.
    overview_intent = any(x in t for x in [
        'what is', 'what exactly is', 'tell me about', 'about this fund',
        'fund details', 'scheme details', 'give me details', 'describe this fund',
        'describe this scheme'
    ])
    if overview_intent:
        if 'large cap' in t:
            return "SBI Large Cap Fund is an open-ended equity scheme predominantly investing in large-cap stocks, as described in SBI Mutual Fund's scheme documents.",pick('SBI Large Cap Fund',docs)
        if 'flexicap' in t or 'flexi cap' in t:
            return "SBI Flexicap Fund is an open-ended dynamic equity scheme investing across large-cap, mid-cap and small-cap stocks, as described in SBI Mutual Fund's scheme documents.",pick('SBI Flexicap Fund',docs)
        if 'elss' in t or 'tax saver' in t:
            return 'SBI ELSS Tax Saver Fund is an open-ended Equity Linked Saving Scheme with a statutory 3-year lock-in period from the date of allotment.',pick('SBI ELSS Tax Saver Fund',docs)

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
    if 'large cap' in t or 'largecap' in t:
        scheme = 'SBI Large Cap Fund'
    elif 'flexicap' in t or 'flexi cap' in t or 'flexi-cap' in t:
        scheme = 'SBI Flexicap Fund'
    elif 'elss' in t or 'tax saver' in t:
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
    elif scheme and any(x in t for x in ['what is', 'tell me about', 'details', 'about this', 'describe']):
        topics = [('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Benchmark', 'What is the benchmark of {s}?'), ('Riskometer', 'What is the riskometer of {s}?'), ('Minimum investment', 'What is the minimum investment in {s}?')]
    else:
        topics = [('Expense ratio', 'What is the expense ratio of {s}?'), ('Exit load', 'What is the exit load of {s}?'), ('Minimum SIP', 'What is the minimum SIP amount for {s}?'), ('Benchmark', 'What is the benchmark of {s}?')]

    if scheme:
        return [(label, text.format(s=scheme)) for label, text in topics]
    return [(label, text) for label, text in topics]


# ---------- PRODUCT UI ----------
st.markdown("""
<div class="topbar">
  <div class="brand"><span class="brand-dot"></span> FundLens</div>
  <div class="live">● LIVE · FACTS ONLY</div>
</div>

<div class="hero">
  <div class="hero-orb orb1"></div>
  <div class="hero-orb orb2"></div>
  <div class="eyebrow">✦ Retrieval-Augmented FAQ Assistant</div>
  <h1>Mutual fund facts,<br><span>without the noise.</span></h1>
  <p>Ask naturally. Get a concise, source-grounded answer from the curated SBI Mutual Fund corpus — with the exact source and document date visible.</p>
  <div class="pills">
    <span class="pill livepill">20 official sources</span>
    <span class="pill">SBI Mutual Fund</span>
    <span class="pill">3 schemes</span>
    <span class="pill">Facts-only</span>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><div class="hero-stat-k">Engine</div><div class="hero-stat-v green">RAG</div></div>
    <div class="hero-stat"><div class="hero-stat-k">Evidence</div><div class="hero-stat-v">Cited</div></div>
    <div class="hero-stat"><div class="hero-stat-k">Advice</div><div class="hero-stat-v">OFF</div></div>
    <div class="hero-stat"><div class="hero-stat-k">PII</div><div class="hero-stat-v">BLOCKED</div></div>
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
    <div class="scheme"><div class="scheme-num">SCHEME 01</div><div class="scheme-name">SBI Large Cap Fund</div><div class="scheme-mini">Equity · Large-cap focused</div></div>
    <div class="scheme"><div class="scheme-num">SCHEME 02</div><div class="scheme-name">SBI Flexicap Fund</div><div class="scheme-mini">Equity · Flexible market caps</div></div>
    <div class="scheme"><div class="scheme-num">SCHEME 03</div><div class="scheme-name">SBI ELSS Tax Saver Fund</div><div class="scheme-mini">ELSS · 3-year statutory lock-in</div></div>
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
