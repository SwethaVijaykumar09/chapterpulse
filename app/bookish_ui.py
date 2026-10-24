"""
bookish_ui.py  -  the "book" look, pop-up effects and story suggestions for ChapterPulse.
Put this file in the SAME folder as app_final.py (the app folder).
"""
import html
import re
import streamlit as st

PROJECT_NAME = "ChapterPulse"
SUBTITLE = "A Reader Engagement Predictor for Serialized Fiction"
TAGLINE = "Find out which chapters keep readers turning the page, and how to write the next one better."

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
:root{--paper:#f5eee0;--card:#fffaf0;--ink:#2a2118;--ox:#7a2e2e;--gold:#d9a22e;--sage:#2f6f5e;--muted:#7b6f5f;--edge:#e6dcc4;}
.stApp{background-color:var(--paper);background-image:radial-gradient(#e9dfc7 1px,transparent 1px);background-size:22px 22px;}
#MainMenu,footer,.stAppDeployButton{display:none!important;}

@keyframes cp-pop{0%{opacity:0;transform:translateY(26px) scale(.92)}60%{opacity:1;transform:translateY(-5px) scale(1.02)}100%{opacity:1;transform:none}}
@keyframes cp-float{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-14px) rotate(8deg)}}
@keyframes cp-swing{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}
@keyframes cp-shine{0%{background-position:0% 50%}100%{background-position:200% 50%}}

.cp-hero{position:relative;display:flex;margin:10px 10px 30px 0;animation:cp-pop .8s both;filter:drop-shadow(0 16px 26px rgba(42,33,24,.28));}
.cp-spine{width:28px;background:linear-gradient(90deg,#43181a,#6b2527 55%,#86393a);border-radius:12px 0 0 12px;box-shadow:inset -4px 0 8px rgba(0,0,0,.35);}
.cp-cover{position:relative;flex:1;overflow:hidden;color:#f8ecd0;padding:38px 44px 34px;border-radius:0 22px 22px 0;background:linear-gradient(135deg,#7a2e2e,#5a1f21);}
.cp-cover:before{content:"";position:absolute;inset:12px;border:1.5px solid rgba(217,162,46,.55);border-radius:14px;pointer-events:none;}
.cp-pages{position:absolute;right:-9px;top:12px;bottom:12px;width:11px;border-radius:0 6px 6px 0;background:repeating-linear-gradient(180deg,#fffaf0 0 3px,#e2d6b8 3px 4px);}
.cp-ribbon{position:absolute;top:-8px;right:64px;width:32px;height:92px;z-index:4;background:var(--gold);clip-path:polygon(0 0,100% 0,100% 100%,50% 82%,0 100%);transform-origin:top center;animation:cp-swing 3.6s ease-in-out infinite;}
.cp-title{position:relative;font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:3.3rem;line-height:1.05;margin:0 0 4px;
  background:linear-gradient(90deg,#f7df93,#d9a22e,#f7df93);background-size:200% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:cp-shine 6s linear infinite;}
.cp-sub{position:relative;font-family:'Lora',Georgia,serif;font-style:italic;color:#ecd9a8;font-size:1.05rem;margin-bottom:14px;}
.cp-tag{position:relative;font-family:'Lora',Georgia,serif;font-size:1.12rem;max-width:620px;line-height:1.55;margin-bottom:16px;}
.cp-chip{display:inline-block;position:relative;margin:0 8px 6px 0;padding:4px 14px;border-radius:99px;background:rgba(248,236,208,.14);border:1px solid rgba(217,162,46,.6);font-size:.82rem;font-weight:600;}
.cp-float span{position:absolute;font-size:1.6rem;opacity:.5;animation:cp-float 5s ease-in-out infinite;}

.cp-sec{display:flex;align-items:center;gap:14px;margin:34px 0 14px;font-family:'Fraunces',Georgia,serif;font-weight:700;font-size:1.6rem;color:var(--ink);}
.cp-sec:before{content:"❦";color:var(--gold);}
.cp-sec:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--gold),transparent);}

.cp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;}
.cp-card,.fgrid>*{position:relative;background:var(--card);border:1px solid var(--edge);border-radius:14px;padding:20px 20px 16px;color:var(--ink);
  box-shadow:0 2px 0 var(--edge);animation:cp-pop .65s cubic-bezier(.2,.9,.3,1.25) both;animation-delay:calc(var(--i,0)*90ms);transition:transform .25s,box-shadow .25s;}
.fgrid>*:nth-child(1){--i:1}.fgrid>*:nth-child(2){--i:2}.fgrid>*:nth-child(3){--i:3}.fgrid>*:nth-child(4){--i:4}
.fgrid>*:nth-child(5){--i:5}.fgrid>*:nth-child(6){--i:6}.fgrid>*:nth-child(7){--i:7}.fgrid>*:nth-child(8){--i:8}
.cp-card:hover,.fgrid>*:hover{transform:translateY(-7px) rotate(-.6deg);box-shadow:0 16px 28px rgba(42,33,24,.2);}
.cp-card:after{content:"";position:absolute;right:0;bottom:0;width:24px;height:24px;border-radius:0 0 14px 0;background:linear-gradient(135deg,transparent 50%,#eadfc6 50%);}
.cp-mark{position:absolute;top:-2px;left:20px;width:15px;height:28px;background:var(--ox);clip-path:polygon(0 0,100% 0,100% 100%,50% 76%,0 100%);}
.cp-card h4{font-family:'Fraunces',Georgia,serif;font-size:1.18rem;margin:10px 0 6px;color:var(--ink);}
.cp-card p{font-family:'Lora',Georgia,serif;font-size:.98rem;line-height:1.55;color:#4a3f33;margin:0 0 10px;}
.cp-badge{display:inline-block;font-size:.72rem;font-weight:700;padding:2px 10px;border-radius:99px;margin-left:6px;}
.cp-badge.data{background:#dcefe8;color:#1f5a49;}.cp-badge.craft{background:#f6e7c1;color:#7a5a10;}.cp-badge.keep{background:#e6e0f4;color:#4b3a8a;}
.cp-ex{border-left:3px solid var(--gold);background:#fbf3de;border-radius:0 8px 8px 0;padding:7px 12px;font-family:'Lora',Georgia,serif;font-size:.92rem;color:#4a3f33;}
.cp-ex b{color:var(--ox);}
.cp-stat .l{font-size:.78rem;letter-spacing:.04em;color:var(--muted);margin-top:8px;}
.cp-stat .v{font-family:'Fraunces',Georgia,serif;font-size:2.2rem;font-weight:700;line-height:1.1;}
.cp-stat .n{font-size:.88rem;color:var(--muted);margin-top:4px;}
.cp-note{font-family:'Lora',Georgia,serif;font-size:.88rem;color:var(--muted);margin-top:14px;font-style:italic;}
.stButton>button{border-radius:12px;font-weight:700;border:1.5px solid var(--ox);transition:transform .2s,box-shadow .2s;}
.stButton>button:hover{transform:translateY(-3px);box-shadow:0 8px 16px rgba(122,46,46,.25);border-color:var(--ox);color:var(--ox);}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>
"""


def _h(s):
    return re.sub(r"\n\s*", "", s)


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def welcome_toast():
    if not st.session_state.get("_cp_welcomed"):
        st.session_state["_cp_welcomed"] = True
        st.toast(f"Welcome to {PROJECT_NAME}. Open a chapter and turn the page.", icon="📖")


def hero(name=PROJECT_NAME, subtitle=SUBTITLE, tagline=TAGLINE,
         chips=("Text mining", "Explainable ML", "Story suggestions")):
    chip_html = "".join(f'<span class="cp-chip">{html.escape(c)}</span>' for c in chips)
    st.markdown(_h(f"""
    <div class="cp-hero"><div class="cp-ribbon"></div><div class="cp-spine"></div>
    <div class="cp-cover"><div class="cp-pages"></div>
    <div class="cp-float"><span style="right:9%;top:14%">✦</span><span style="right:22%;bottom:12%;animation-delay:1.2s">❦</span>
    <span style="right:34%;top:10%;animation-delay:2.1s">📖</span></div>
    <div class="cp-title">{html.escape(name)}</div><div class="cp-sub">{html.escape(subtitle)}</div>
    <div class="cp-tag">{html.escape(tagline)}</div>{chip_html}</div></div>"""), unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="cp-sec">{html.escape(title)}</div>', unsafe_allow_html=True)


def stat_cards(items):
    """items = [(label, value, note), ...]  ->  pop-up stat cards."""
    cards = "".join(
        f'<div class="cp-card cp-stat" style="--i:{i}"><div class="cp-mark"></div>'
        f'<div class="l">{html.escape(str(l))}</div><div class="v">{html.escape(str(v))}</div>'
        f'<div class="n">{html.escape(str(n))}</div></div>' for i, (l, v, n) in enumerate(items, 1))
    st.markdown(f'<div class="cp-grid">{cards}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- suggestions
def _g(d, names, default=None):
    for n in names:
        try:
            v = d[n]
        except Exception:
            continue
        try:
            v = float(v)
        except Exception:
            continue
        if v == v:
            return v
    return default


W = ("word_count", "chapter_length", "words", "length")
S = ("avg_sentence_len", "sentence_length", "sent_len")
D = ("dialogue_ratio", "dialogue_density", "dialogue")
Q = ("end_questions", "ending_questions")
X = ("end_exclaims", "end_exclamations", "ending_exclamations")
U = ("end_suspense_words", "suspense_words")
K = ("cliffhanger_score", "cliffhanger")


def _per100(v):
    return None if v is None else (v * 100 if v <= 1.5 else v)


HOOKS = [
    ("Open question", "End on the one question the reader now needs answered: <b>\"Why did he lie about the key?\"</b>"),
    ("Reveal", "Drop a fact that changes the last chapter: <b>The letter was in her own handwriting.</b>"),
    ("Danger", "Cut away at the worst moment: <b>The floor gave way, and the lights went out.</b>"),
    ("Choice", "Force a decision and stop before it: <b>Two doors. One lie. She had ten seconds.</b>"),
]


def build_suggestions(per, avg, bench=None, length_is_data_backed=True):
    t = bench if bench is not None else avg
    out = []

    w, wt = _g(per, W), _g(t, W)
    if w and wt:
        if w < 0.85 * wt:
            out.append(("📏", "Give the chapter more room", f"Your chapters average {w:,.0f} words; stronger chapters in the data are closer to {wt:,.0f}. Add one more scene beat, such as a complication, before you reach the ending.",
                        "data" if length_is_data_backed else "craft", "<b>Before:</b> arrive, talk, leave. <b>After:</b> arrive, talk, find something wrong, leave unsettled."))
        elif w > 1.15 * wt:
            out.append(("✂️", "Trim or split the chapter", f"At {w:,.0f} words you are above the typical {wt:,.0f}. Cut the slowest scene, or split the chapter at a natural suspense point so each part ends on a hook.",
                        "data" if length_is_data_backed else "craft", "Split where a secret is about to come out, not where a scene politely ends."))
        else:
            out.append(("✅", "Keep your chapter length", f"{w:,.0f} words is close to the {wt:,.0f} typical of stronger chapters. Hold this rhythm.", "keep", ""))

    s, st_ = _g(per, S), _g(t, S)
    if s and st_:
        if s > 1.15 * st_:
            out.append(("⚡", "Shorten sentences in action scenes", f"Sentences average {s:.1f} words (typical {st_:.1f}). Short sentences make tension feel faster.",
                        "craft", "<b>Before:</b> She ran toward the door as the footsteps behind her grew louder. <b>After:</b> She ran. The footsteps grew louder. The door was locked."))
        elif s < 0.85 * st_:
            out.append(("🎼", "Vary the rhythm", f"Sentences are very short ({s:.1f} words). Add an occasional long, flowing sentence so quiet moments can breathe.", "craft", ""))

    d, dt = _per100(_g(per, D)), _per100(_g(t, D))
    if d is not None and dt:
        if d < 0.8 * dt:
            out.append(("💬", "Let your characters talk", f"About {d:.0f} quote marks per 100 words, against a typical {dt:.0f}. Conversation reveals character and speeds the pace.",
                        "craft", "Turn a paragraph of explanation into an argument between two people."))
        elif d > 1.25 * dt:
            out.append(("🌄", "Ground the dialogue", f"Dialogue is heavy ({d:.0f} per 100 words, typical {dt:.0f}). Add small actions and setting so scenes do not feel like floating voices.", "craft", ""))

    q, ex, u = _g(per, Q, 0), _g(per, X, 0), _g(per, U, 0)
    if q < 1 and u < 1:
        out.append(("🔖", "Close on an open question", "Your endings rarely leave something unanswered. Finish with one thing the reader must find out next.",
                    "craft", "<b>Before:</b> She went to bed. <b>After:</b> She went to bed. Then the lock turned, from the outside."))
    elif ex >= 2 and u < 1:
        out.append(("🤫", "Swap shouting for a quiet reveal", f"Your endings use many exclamation marks ({ex:.1f}) but few tense words ({u:.1f}). A calm, chilling line often hooks harder than volume.",
                    "craft", "<b>Before:</b> \"Run!\" he screamed! <b>After:</b> He smiled. \"You never asked who sent the letter.\""))

    c, ct = _g(per, K), _g(t, K)
    if c is not None and ct and c < ct:
        out.append(("🪝", "Strengthen the ending hook", f"Your cliffhanger score is {c:.1f} against {ct:.1f} for the typical chapter. Try one of the four hook recipes in your blueprint.", "craft", ""))

    if len(out) < 3:
        out.append(("🌱", "Try one experiment", "Rewrite only your last three sentences using a hook recipe, then compare how the chapter feels.", "craft", ""))
    return out


def _cards_html(sugs):
    label = {"data": "Data-backed", "craft": "Craft advice", "keep": "Keep doing"}
    cards = ""
    for i, (icon, title, text, tag, ex) in enumerate(sugs, 1):
        exh = f'<div class="cp-ex">{ex}</div>' if ex else ""
        cards += (f'<div class="cp-card" style="--i:{i}"><div class="cp-mark"></div>'
                  f'<span style="font-size:1.5rem">{icon}</span><span class="cp-badge {tag}">{label[tag]}</span>'
                  f'<h4>{html.escape(title)}</h4><p>{html.escape(text)}</p>{exh}</div>')
    return f'<div class="cp-grid">{cards}</div>'


def _blueprint_html(per, avg, bench, note):
    t = bench if bench is not None else avg
    w, s, d = _g(t, W), _g(t, S), _per100(_g(t, D))
    spec = []
    if w: spec.append(f"about <b>{w:,.0f} words</b>")
    if s: spec.append(f"sentences averaging <b>{s:.1f} words</b>")
    if d is not None: spec.append(f"roughly <b>{d:.0f} quote marks per 100 words</b>")
    spec_txt = ", ".join(spec) if spec else "your usual length and pace"
    hooks = "".join(f'<li><b>{n}.</b> {e}</li>' for n, e in HOOKS)
    return _h(f"""
    <div class="cp-card" style="--i:0"><div class="cp-mark"></div>
    <h4>Act 1: Open in motion</h4><p>Start the first 150 words with action, a line of dialogue or a surprising detail. Name your main character early.</p>
    <h4>Act 2: Build the middle</h4><p>Aim for {spec_txt}. Add one complication the character did not expect.</p>
    <h4>Act 3: Choose your hook</h4><p><ul style="margin:0 0 8px 18px;font-family:Lora,serif;line-height:1.6">{hooks}</ul></p>
    <h4>Story seed for your next chapter</h4>
    <div class="cp-ex">Let <b>[character]</b> discover <b>[a secret]</b> just as <b>[an interruption]</b> happens. Do not resolve it. End on <b>[a question / a choice / a reveal]</b>.</div>
    <div class="cp-note">{html.escape(note)}</div></div>""")


_dialog = getattr(st, "dialog", None)
if _dialog:
    @_dialog("✨ Your next-chapter blueprint", width="large")
    def _show_blueprint(markup):
        st.markdown(markup, unsafe_allow_html=True)


NOTE = ("In this study, text features explained little on unseen stories, and ending-hook features did not lift "
        "predictions. Treat craft advice as writing guidance, not a guaranteed boost.")


def render_tips(per, avg, bench=None, key="tips", note=NOTE):
    """per = this chapter/story's numbers, avg = dataset average (dicts or pandas Series)."""
    sugs = build_suggestions(per, avg, bench)
    section("How to write it better")
    st.markdown(_cards_html(sugs), unsafe_allow_html=True)
    st.markdown(f'<div class="cp-note">{html.escape(note)}</div>', unsafe_allow_html=True)
    st.write("")
    if st.button("✨ Open my story blueprint", key=f"bp_{key}"):
        st.toast("Your story blueprint is ready", icon="✨")
        markup = _blueprint_html(per, avg, bench, note)
        if _dialog:
            _show_blueprint(markup)
        else:
            with st.expander("Your next-chapter blueprint", expanded=True):
                st.markdown(markup, unsafe_allow_html=True)