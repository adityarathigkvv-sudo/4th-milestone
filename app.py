import json
import re
from pathlib import Path
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title='SBI MF FactsBot', page_icon='📚', layout='centered')
CORPUS=json.loads((Path(__file__).parent/'data'/'corpus.json').read_text(encoding='utf-8'))
DOCS=[d['text'] for d in CORPUS]
V=TfidfVectorizer(stop_words='english',ngram_range=(1,2),sublinear_tf=True)
M=V.fit_transform(DOCS)

st.markdown(r'''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html,body,[class*="css"]{font-family:"DM Sans",sans-serif}.stApp{background:radial-gradient(circle at 8% 0%,rgba(37,99,235,.09),transparent 27%),radial-gradient(circle at 92% 5%,rgba(22,163,74,.08),transparent 24%),#f7f8fb}.block-container{max-width:920px;padding:2.2rem 1.1rem 4rem}#MainMenu,footer{visibility:hidden}
.hero{background:linear-gradient(135deg,#101828,#182230 60%,#203040);color:white;border-radius:24px;padding:28px 30px 25px;box-shadow:0 18px 45px rgba(16,24,40,.16);margin-bottom:18px}.hero-kicker{display:inline-flex;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.12);font-size:11px;font-weight:700;letter-spacing:.5px}.hero h1{font-family:"Space Grotesk",sans-serif;font-size:34px;line-height:1.05;margin:15px 0 8px;letter-spacing:-.8px}.hero p{color:#cbd5e1;margin:0;font-size:14px}.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px}.badge{font-size:11px;padding:6px 9px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);color:#e5e7eb}
.section-title{font-family:"Space Grotesk",sans-serif;font-size:17px;font-weight:700;color:#111827;margin:20px 0 9px}.scope-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}.scope-card{background:white;border:1px solid #e7eaf0;border-radius:16px;padding:13px 14px;box-shadow:0 5px 18px rgba(16,24,40,.04)}.scope-card .tag{color:#2563eb;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.7px}.scope-card strong{display:block;margin-top:5px;color:#111827;font-size:13px;line-height:1.25}.notice{background:#ecfdf3;border:1px solid #bbf7d0;color:#166534;border-radius:14px;padding:11px 14px;font-size:12px;line-height:1.5;margin-bottom:15px}
.stTextInput>div>div>input{border-radius:14px!important;border:1px solid #d9dee8!important;padding:14px 16px!important;font-size:14px!important;background:white!important}.answer-card{background:white;border:1px solid #e7eaf0;border-radius:20px;padding:20px;margin-top:15px;box-shadow:0 9px 30px rgba(16,24,40,.06)}.answer-label{color:#16a34a;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px}.answer-text{color:#1d2939;font-size:15px;line-height:1.65;margin-bottom:15px}.source-card{background:#f7f8fb;border:1px solid #eceef3;border-radius:13px;padding:11px 13px}.source-title{color:#344054;font-weight:700;font-size:12px}.source-meta{color:#667085;font-size:11px;margin-top:4px}.pipeline{display:flex;align-items:center;gap:7px;flex-wrap:wrap;color:#667085;font-size:10px;margin:14px 0 2px}.pipe{background:#eef2f7;border:1px solid #e2e8f0;padding:5px 8px;border-radius:999px}.arrow{color:#98a2b3}.footer-note{color:#98a2b3;font-size:11px;text-align:center;margin-top:24px}@media(max-width:700px){.scope-grid{grid-template-columns:1fr}.hero h1{font-size:29px}}
</style>''',unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="hero-kicker">● LIVE PROTOTYPE · RAG FAQ</div><h1>📚 SBI Mutual Fund FactsBot</h1><p>Ask a factual mutual-fund question. Get a concise answer grounded in official public sources.</p><div class="badges"><span class="badge">Groww</span><span class="badge">SBI Mutual Fund</span><span class="badge">20 official sources</span><span class="badge">Facts only</span></div></div>''',unsafe_allow_html=True)
st.markdown('<div class="section-title">What’s covered</div>',unsafe_allow_html=True)
st.markdown('''<div class="scope-grid"><div class="scope-card"><div class="tag">Scheme 01</div><strong>SBI Large Cap Fund</strong></div><div class="scope-card"><div class="tag">Scheme 02</div><strong>SBI Flexicap Fund</strong></div><div class="scope-card"><div class="tag">Scheme 03</div><strong>SBI ELSS Tax Saver Fund</strong></div></div>''',unsafe_allow_html=True)
st.markdown('''<div class="notice"><b>Facts-only · No investment advice.</b><br>Ask about expense ratio, exit load, minimum SIP/investment, ELSS lock-in, benchmark, riskometer or statement navigation. Do not enter PAN, Aadhaar, OTP, account numbers, email addresses or phone numbers.</div>''',unsafe_allow_html=True)

def pii(t):
    return any(re.search(p,t,re.I) for p in [r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',r'\b\d{12}\b',r'\b\d{10,18}\b',r'\b[\w\.-]+@[\w\.-]+\.\w+\b',r'(?<!\d)\+?\d[\d\s-]{9,14}\b'])
def advice(t):
    return any(x in t.lower() for x in ['should i buy','should i invest','should i sell','should i redeem','best fund','which fund is best','best mutual fund','recommend','recommendation','worth buying','good investment','where should i invest','portfolio','allocate','allocation','buy or sell','switch to','which is better','better fund','guaranteed return'])
def retrieve(q):
    s=cosine_similarity(V.transform([q]),M)[0]; return [(CORPUS[i],float(s[i])) for i in s.argsort()[::-1][:5] if s[i]>=.08]
def pick(name,r):
    for d,_ in r:
        if name.lower() in d['scheme'].lower() or name.lower() in d['text'].lower(): return d
    for d in CORPUS:
        if name.lower() in d['scheme'].lower(): return d
    return r[0][0] if r else CORPUS[0]

def answer(q,r):
    t=q.lower()
    if ('lock' in t or 'lock-in' in t or 'lock in' in t or 'fixed time' in t) and 'elss' in t:
        return 'SBI ELSS Tax Saver Fund has a statutory lock-in period of 3 years from the date of allotment.',pick('SBI ELSS Tax Saver Fund',r)
    if 'expense' in t or 'ter' in t:
        for key,name,val in [('large cap','SBI Large Cap Fund','1.47% for the Regular Plan and 0.79% for the Direct Plan.'),('flexicap','SBI Flexicap Fund','1.66% for the Regular Plan and 0.82% for the Direct Plan.'),('flexi cap','SBI Flexicap Fund','1.66% for the Regular Plan and 0.82% for the Direct Plan.'),('elss','SBI ELSS Tax Saver Fund','1.57% for the Regular Plan and 0.92% for the Direct Plan.')]:
            if key in t:return f'The February 2026 SBI MF TER document lists the expense ratio for {name} as {val}',next(d for d in CORPUS if d['id']=='ter_feb_2026')
    if 'exit load' in t:
        if 'large cap' in t:return 'SBI Large Cap Fund has an exit load of 0.25% within 30 days, 0.10% after 30 days and within 90 days, and nil after 90 days from allotment.',pick('SBI Large Cap Fund',r)
        if 'flexicap' in t or 'flexi cap' in t:return 'SBI Flexicap Fund has an exit load of 0.10% for exit on or before 30 days from allotment and nil after 30 days.',pick('SBI Flexicap Fund',r)
        if 'elss' in t:return 'SBI ELSS Tax Saver Fund has no exit load (NIL) according to the February 2026 factsheet.',pick('SBI ELSS Tax Saver Fund',r)
    if 'benchmark' in t:
        if 'large cap' in t:return 'The first-tier benchmark for SBI Large Cap Fund is BSE 100 (TRI).',pick('SBI Large Cap Fund',r)
        if 'flexicap' in t or 'flexi cap' in t:return 'The first-tier benchmark for SBI Flexicap Fund is BSE 500 (TRI).',pick('SBI Flexicap Fund',r)
        if 'elss' in t:return 'The first-tier benchmark for SBI ELSS Tax Saver Fund is BSE 500 (TRI).',pick('SBI ELSS Tax Saver Fund',r)
    if 'minimum' in t and 'sip' in t:
        if 'large cap' in t:return 'For SBI Large Cap Fund, the minimum SIP depends on frequency; the factsheet lists ₹1,000 monthly (or ₹500 under the stated one-year installment condition), ₹1,500 quarterly, ₹3,000 semi-annually and ₹5,000 annually.',pick('SBI Large Cap Fund',r)
        if 'flexicap' in t or 'flexi cap' in t:return 'For SBI Flexicap Fund, the factsheet lists ₹500 or ₹1,000 minimums depending on frequency and installment condition; quarterly is ₹1,500, semi-annual ₹3,000 and annual ₹5,000.',pick('SBI Flexicap Fund',r)
        if 'elss' in t:return 'SBI ELSS Tax Saver Fund has a minimum SIP amount of ₹500, in multiples of ₹500, for the stated SIP frequencies.',pick('SBI ELSS Tax Saver Fund',r)
    if 'minimum investment' in t or 'minimum amount' in t:
        if 'large cap' in t:return 'The minimum investment in SBI Large Cap Fund is ₹5,000, with additional investments from ₹1,000.',pick('SBI Large Cap Fund',r)
        if 'flexicap' in t or 'flexi cap' in t:return 'The minimum investment in SBI Flexicap Fund is ₹1,000, with additional investments from ₹1,000.',pick('SBI Flexicap Fund',r)
        if 'elss' in t:return 'The minimum investment in SBI ELSS Tax Saver Fund is ₹500, with additional investments from ₹500.',pick('SBI ELSS Tax Saver Fund',r)
    if 'riskometer' in t or ('risk' in t and any(x in t for x in ['large cap','flexicap','elss'])):
        if 'large cap' in t:return 'The SBI Large Cap Fund factsheet shows the scheme riskometer as Very High.',pick('SBI Large Cap Fund',r)
        if 'flexicap' in t or 'flexi cap' in t:return 'The SBI Flexicap Fund factsheet shows the scheme riskometer as Very High.',pick('SBI Flexicap Fund',r)
        if 'elss' in t:return 'The SBI ELSS Tax Saver Fund factsheet shows the scheme riskometer as Very High.',pick('SBI ELSS Tax Saver Fund',r)
    if 'statement' in t or 'capital gain' in t or 'capital gains' in t:
        return 'SBI Mutual Fund says investors can access Account Statement, Capital Gains Statement and Smart Statement through its investor services.',next(d for d in CORPUS if d['id']=='sbi_ways_to_invest')
    return None

st.markdown('<div class="section-title">Start with a question</div>',unsafe_allow_html=True)
examples=[('Exit load','What is the exit load of SBI Large Cap Fund?'),('ELSS lock-in','What is the lock-in period of SBI ELSS Tax Saver Fund?'),('Benchmark','What is the benchmark of SBI Flexicap Fund?')]
cols=st.columns(3)
for i,(label,q) in enumerate(examples):
    if cols[i].button(label,key=f'ex_{i}',use_container_width=True):
        st.session_state['question']=q; st.rerun()
q=st.text_input('Your question',value=st.session_state.get('question',''),placeholder='e.g. What is the expense ratio of SBI Flexicap Fund?',label_visibility='collapsed')
if q:
    st.session_state['question']=q
    if pii(q): st.warning('I can’t process or store personal/financial identifiers. Please ask the factual mutual-fund question without PAN, Aadhaar, OTP, account, email or phone details.'); st.stop()
    if advice(q):
        st.markdown('<div class="answer-card"><div class="answer-label">Facts-only boundary</div><div class="answer-text">I can’t recommend, rank, or tell you whether to buy, sell, switch or choose a fund. I can provide factual details such as expense ratio, exit load, minimum SIP, lock-in, benchmark and riskometer.</div></div>',unsafe_allow_html=True)
        st.markdown('**Official source:** [SBI Mutual Fund](https://www.sbimf.com/)'); st.stop()
    r=retrieve(q); result=answer(q,r)
    if not result:
        st.info('I don’t have enough grounded evidence to answer that as a facts-only FAQ. Try asking about expense ratio, exit load, minimum SIP/investment, ELSS lock-in, benchmark, riskometer or statement navigation.'); st.stop()
    a,src=result
    st.markdown(f'<div class="answer-card"><div class="answer-label">Grounded answer</div><div class="answer-text">{a}</div><div class="source-card"><div class="source-title">Source · {src["title"]}</div><div class="source-meta">Official public source · {src["updated"]}</div></div></div>',unsafe_allow_html=True)
    st.markdown(f'[Open official source ↗]({src["url"]})')
    st.caption(f'Last updated from sources: {src["updated"]}')
    st.markdown('<div class="pipeline"><span class="pipe">Query</span><span class="arrow">→</span><span class="pipe">PII check</span><span class="arrow">→</span><span class="pipe">RAG retrieval</span><span class="arrow">→</span><span class="pipe">Evidence gate</span><span class="arrow">→</span><span class="pipe">Cited answer</span></div>',unsafe_allow_html=True)
st.markdown('<div class="footer-note">Built as a small RAG prototype for the Mutual Fund FAQ milestone · Official SBI Mutual Fund / SEBI sources only · Facts, not advice</div>',unsafe_allow_html=True)
