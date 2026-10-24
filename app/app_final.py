import os, re, sys
import joblib
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "notebooks"))
from src.features import extract_features, FEATURES
import bookish_ui as ui

st.set_page_config(page_title="ChapterPulse", page_icon="📖", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=DM+Sans:wght@400;500;700&display=swap');
:root{--ink:#1B1420;--paper:#F7F1E5;--saffron:#E0A030;--clay:#B5543A;--card:#FFFBF1;--line:#E2D6BC;}
html, body, .stApp, [data-testid="stAppViewContainer"]{background:var(--paper)!important;font-family:'DM Sans',sans-serif;}
[data-testid="stHeader"]{background:transparent!important;}
#MainMenu, footer{visibility:hidden;}
.block-container{max-width:1100px;padding-top:1.5rem;padding-bottom:4rem;}
.stMarkdown p, .stMarkdown li, [data-testid="stWidgetLabel"] p{color:var(--ink)!important;}
.hero{background:radial-gradient(circle at 85% 15%, #6a3243 0%, var(--ink) 58%);border-radius:28px;padding:68px 56px;margin-bottom:12px;}
.hero .eyebrow{color:var(--saffron)!important;letter-spacing:.18em;font-size:.8rem;font-weight:700;margin:0;}
.hero .title{font-family:'Fraunces',serif;color:var(--paper);font-size:3.6rem;line-height:1.04;font-weight:600;margin:.25em 0 .35em;max-width:760px;}
.hero .title em{color:var(--saffron);font-weight:400;}
.hero .lead{color:#E9DFC9!important;font-size:1.1rem;max-width:620px;line-height:1.6;}
.pills span{display:inline-block;border:1px solid #8a6a5a;color:var(--paper);border-radius:999px;padding:6px 16px;margin:14px 10px 0 0;font-size:.85rem;}
.sec-kicker{color:var(--clay);letter-spacing:.16em;font-size:.78rem;font-weight:700;margin-top:56px;}
.sec-title{font-family:'Fraunces',serif;font-size:2.4rem;line-height:1.1;font-weight:600;color:var(--ink);margin:.1em 0 .5em;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:26px;}
.card .num{font-family:'Fraunces',serif;font-size:2rem;color:var(--clay);}
.card h4{font-family:'Fraunces',serif;font-size:1.25rem;margin:.2em 0;color:var(--ink);}
.card p{margin:0;line-height:1.55;color:#4a3f4d;}
.dark{background:var(--ink);border-radius:22px;padding:26px;}
.dark h4,.dark p{color:var(--paper)!important;}
.dark .num{color:var(--saffron);}
textarea{background:var(--card)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;}
[data-baseweb="textarea"],[data-baseweb="base-input"]{background:var(--card)!important;border-radius:16px!important;}
.stButton>button{background:var(--ink);color:var(--paper);border:none;border-radius:999px;padding:.65rem 1.5rem;font-weight:700;}
.stButton>button:hover{background:var(--saffron);color:var(--ink);}
.small-label{font-size:.75rem;letter-spacing:.12em;text-transform:uppercase;color:#8a7a68;font-weight:700;}
.result{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:10px;}
@media(max-width:800px){.result{grid-template-columns:1fr;}.hero{padding:40px 26px;}.hero .title{font-size:2.5rem;}}
.bignum{font-family:'Fraunces',serif;font-size:3.6rem;color:var(--saffron);line-height:1.1;}
.track{background:#3a2e3d;border-radius:999px;height:14px;margin:14px 0 8px;}
.fill{background:linear-gradient(90deg,var(--saffron),var(--clay));height:14px;border-radius:999px;}
.fgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:10px;}
.fcard{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;}
.fnum{font-family:'Fraunces',serif;font-size:2rem;color:var(--ink);}
.fnote{font-size:.85rem;color:#6a5d6c;line-height:1.4;}
.foot{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);font-size:.85rem;color:#6a5d6c;}
</style>""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    return joblib.load(os.path.join(ROOT, "models", "model_real.pkl"))


@st.cache_data
def load_reference():
    p = os.path.join(ROOT, "data", "stories_sample.csv")
    return pd.read_csv(p)["log_views"].dropna().values if os.path.exists(p) else None


bundle = load_model()
model, cols = bundle["model"], bundle["features"]
ref = load_reference()
@st.cache_data
def load_ref_features():
    p = os.path.join(ROOT, "data", "features_all.csv")
    return pd.read_csv(p) if os.path.exists(p) else None


ref_feats = load_ref_features()
@st.cache_data
def load_benchmark():
    f = os.path.join(ROOT, "data", "features_all.csv")
    s = os.path.join(ROOT, "data", "stories_sample.csv")
    if not (os.path.exists(f) and os.path.exists(s)):
        return None
    m = pd.read_csv(f).merge(pd.read_csv(s)[["story_id", "log_views"]], on="story_id")
    top = m[m["log_views"] >= m["log_views"].median()]
    return top[FEATURES].median()


benchmark = load_benchmark()
SAMPLE = os.path.join(ROOT, "data", "demo_story.txt")
st.session_state.setdefault("story_text", "")
st.session_state.setdefault("year", 2010)


def use_sample():
    if os.path.exists(SAMPLE):
        with open(SAMPLE, encoding="utf-8") as f:
            st.session_state["story_text"] = f.read()
        st.session_state["year"] = 2009


# ---------- HERO ----------
ui.inject_css()
ui.welcome_toast()
ui.hero()

# ---------- HOW IT WORKS ----------
st.markdown("""<div class="sec-kicker">HOW IT WORKS</div>
<div class="sec-title">Three steps, no magic</div>
<div class="cards">
<div class="card"><div class="num">01</div><h4>Paste</h4><p>Drop in one to five opening chapters of a story, separated by a line with three dashes.</p></div>
<div class="card"><div class="num">02</div><h4>Measure</h4><p>Text mining counts sentence length, dialogue, mood and how each chapter ends.</p></div>
<div class="card"><div class="num">03</div><h4>Read</h4><p>A model trained on real stories shows a rough view estimate, plus the clues behind it.</p></div>
</div>""", unsafe_allow_html=True)

# ---------- TRY IT ----------
st.markdown('<div class="sec-kicker">TRY IT</div><div class="sec-title">Paste a story, get a reading</div>',
            unsafe_allow_html=True)
left, right = st.columns([1.6, 1], gap="large")
with left:
    st.text_area("Opening chapters (a line with only --- between chapters)", height=320,
                 key="story_text", placeholder="Paste chapter 1 here...\n---\nPaste chapter 2 here...")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.number_input("Year published", min_value=2009, max_value=2026, key="year")
    with c2:
        st.write("")
        st.button("Use sample story", on_click=use_sample)
    with c3:
        st.write("")
        go = st.button("Read my story →", type="primary")
with right:
    st.markdown("""<div class="dark"><div class="small-label">WHAT TO PASTE</div>
<h4>Tips for a good reading</h4>
<p>• English text only<br>• 1 to 8 chapters, 100+ words each<br>• One story at a time<br>• Set the year it was posted</p></div>""",
                unsafe_allow_html=True)

# ---------- RESULT ----------
if go:
    st.session_state["shown"] = True
if st.session_state.get("shown"):
    parts = re.split(r"\n\s*---\s*\n", st.session_state["story_text"])
    chapters = [c.strip() for c in parts if len(c.split()) >= 100][:8]
    if not chapters:
        st.error("Please paste at least one chapter with 100+ words.")
    else:
        per = pd.DataFrame([extract_features(c) for c in chapters])[FEATURES]
        avg = per.mean()
        x = pd.DataFrame([{"publish_year": st.session_state["year"], **avg.to_dict()}])[cols]
        pred = float(model.predict(x)[0])
        views = 10 ** pred
        if ref is not None:
            pct = float((ref < pred).mean() * 100)
            sd = float(ref.std())
            rng = f'<div class="small-label">Typical range: {10**(pred-sd):,.0f} to {10**(pred+sd):,.0f}</div>'
        else:
            pct, rng = 50.0, ""
        band = "Quieter than most" if pct < 33 else ("Around the middle" if pct < 67 else "Louder than most")

        st.markdown('<div class="sec-kicker">YOUR READING</div><div class="sec-title">What the data says</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="result">
<div class="dark"><div class="small-label">ROUGH ESTIMATE</div><div class="bignum">{views:,.0f}</div>
<p>views for a story like this</p>{rng}</div>
<div class="dark"><div class="small-label">WHERE IT SITS</div><h4>{band}</h4>
<div class="track"><div class="fill" style="width:{pct:.0f}%"></div></div>
<p>Higher than about {pct:.0f}% of the stories in the dataset.</p>
<p style="font-size:.85rem;opacity:.8">The model rarely predicts extremes, which shows how weak the text signal is.</p></div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title" style="font-size:1.6rem;margin-top:34px">How strong is each chapter’s ending hook?</div>',
                    unsafe_allow_html=True)
        chart = pd.DataFrame({"Cliffhanger score": per["cliffhanger_score"].values},
                             index=[f"Ch {i+1}" for i in range(len(per))])
        st.bar_chart(chart, color="#E0A030", height=240)

        def card(label, value, note):
            return (f'<div class="fcard"><div class="small-label">{label}</div>'
                    f'<div class="fnum">{value}</div><div class="fnote">{note}</div></div>')
        cards = "".join([
            card("Chapter length", f"{avg['word_count']:,.0f}", "words per chapter, the strongest text signal in my study"),
            card("Sentence length", f"{avg['avg_sentence_len']:.1f}", "words per sentence; shorter feels faster"),
            card("Dialogue density", f"{avg['dialogue_ratio']*100:.0f}", "quote marks per 100 words"),
            card("Ending questions", f"{avg['end_questions']:.1f}", "question marks in the last 150 words"),
            card("Ending exclamations", f"{avg['end_exclaims']:.1f}", "exclamation marks in the last 150 words"),
            card("Suspense words", f"{avg['end_suspense_words']:.1f}", "tense words near the ending"),
            card("Cliffhanger score", f"{avg['cliffhanger_score']:.1f}", "my own recipe; see the findings below"),
        ])
        st.markdown(f'<div class="fgrid">{cards}</div>', unsafe_allow_html=True)
        ui.render_tips(avg, benchmark, key="main")
# ---------- FINDINGS ----------
st.markdown("""<div class="sec-kicker">THE RESEARCH</div>
<div class="sec-title">What the data actually showed</div>
<div class="cards">
<div class="card"><div class="num">06%</div><h4>Text explains little</h4><p>On stories the model never saw, text features explained about 6% of the variation in views (R² = 0.064).</p></div>
<div class="card"><div class="num">↑</div><h4>Length leads</h4><p>Chapter length was the strongest text-based signal. It is an association, not proof of cause.</p></div>
<div class="card"><div class="num">0</div><h4>Cliffhanger score: no lift</h4><p>My own cliffhanger score did not improve predictions here. A null result is still a result, and I report it.</p></div>
</div>
<p style="margin-top:18px">Story structure, such as how many chapters a story has, explained much more (R² about 0.47), but it partly reflects popularity itself, since writers keep going when readers keep reading.</p>""",
            unsafe_allow_html=True)

st.markdown("""<div class="foot"><b>Data and ethics.</b> Built on the public Asianfanfics archive on Hugging Face
(trentmkelly/asianfanfics, CC-BY-SA-4.0). Usernames were removed and never used. Authors' consent was not individually
verified. This tool finds patterns, not proof, and offers a guide, not a verdict.</div>""", unsafe_allow_html=True)