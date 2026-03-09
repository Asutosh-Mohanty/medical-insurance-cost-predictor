import streamlit as st
import pickle
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════
USD_TO_INR = 83.5

def to_inr(v):    return v * USD_TO_INR
def fmt_inr(v, short=False):
    val = to_inr(v)
    if short:
        if val >= 1_00_00_000: return f"₹{val/1_00_00_000:.1f}Cr"
        if val >= 1_00_000:    return f"₹{val/1_00_000:.1f}L"
        return f"₹{val:,.0f}"
    return f"₹{val:,.0f}"

st.set_page_config(
    page_title="InsureIQ — AI Cost Predictor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ──
for key, default in [("page","form"),("inputs",{}),("animating",False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL CSS  — animations, layout, components
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing:border-box; }
html, body, [class*="css"] { font-family:'Inter',sans-serif; }

/* ═══════════════════════════════════════
   BACKGROUND
═══════════════════════════════════════ */
.stApp {
    min-height:100vh;
    background-color:#020c18;
    background-image:
        linear-gradient(135deg,
            rgba(0,8,22,0.93) 0%,
            rgba(0,14,35,0.88) 45%,
            rgba(2,6,20,0.94) 100%),
        url("https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf?w=1920&q=85");
    background-size:cover;
    background-position:center;
    background-repeat:no-repeat;
    background-attachment:fixed;
}

/* Floating ambient orbs */
.stApp::before {
    content:''; position:fixed; top:-15%; left:-10%;
    width:60vw; height:60vw;
    background:radial-gradient(circle,rgba(0,220,120,0.08) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
    animation:orbFloat1 24s ease-in-out infinite alternate; z-index:0;
}
.stApp::after {
    content:''; position:fixed; bottom:-15%; right:-10%;
    width:55vw; height:55vw;
    background:radial-gradient(circle,rgba(0,110,255,0.08) 0%,transparent 65%);
    border-radius:50%; pointer-events:none;
    animation:orbFloat2 28s ease-in-out infinite alternate; z-index:0;
}
@keyframes orbFloat1 {
    0%   { transform:translate(0,0) scale(1); }
    33%  { transform:translate(4vw,6vh) scale(1.08); }
    66%  { transform:translate(-3vw,3vh) scale(0.95); }
    100% { transform:translate(6vw,-2vh) scale(1.12); }
}
@keyframes orbFloat2 {
    0%   { transform:translate(0,0) scale(1); }
    33%  { transform:translate(-5vw,-4vh) scale(1.06); }
    66%  { transform:translate(3vw,-6vh) scale(1.1); }
    100% { transform:translate(-4vw,3vh) scale(0.97); }
}

/* Animated top accent bar */
.stApp > div:first-child::before {
    content:''; position:fixed; top:0; left:0;
    width:100%; height:2px;
    background:linear-gradient(90deg,
        transparent 0%, #00e888 20%, #0099ff 50%, #7c3aed 80%, transparent 100%);
    background-size:200% 100%;
    animation:scanBar 4s linear infinite;
    z-index:9999; pointer-events:none;
}
@keyframes scanBar {
    0%   { background-position:200% 0; }
    100% { background-position:-200% 0; }
}

/* Floating particles (CSS only) */
.particle {
    position:fixed; border-radius:50%; pointer-events:none; z-index:1;
    animation:particleDrift linear infinite;
}
@keyframes particleDrift {
    0%   { transform:translateY(100vh) scale(0); opacity:0; }
    10%  { opacity:1; }
    90%  { opacity:0.4; }
    100% { transform:translateY(-10vh) scale(1); opacity:0; }
}

/* ═══════════════════════════════════════
   LAYOUT
═══════════════════════════════════════ */
#MainMenu, footer, header { visibility:hidden; }
[data-testid="stDecoration"] { display:none; }
[data-testid="stSidebar"]    { display:none; }
.block-container {
    max-width:1120px !important;
    padding:2.2rem 2rem !important;
}

/* Page transition */
@keyframes pageSlideIn {
    from { opacity:0; transform:translateY(28px) scale(0.98); }
    to   { opacity:1; transform:translateY(0)   scale(1);    }
}
.page-enter { animation:pageSlideIn 0.55s cubic-bezier(0.22,1,0.36,1) both; }

/* ═══════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════ */
.page-title {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(1.9rem,3.5vw,2.9rem); font-weight:900;
    background:linear-gradient(120deg,#ffffff 0%,#80ffcc 35%,#60b8ff 75%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1.1; margin-bottom:0.4rem;
    animation:titleReveal 0.8s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes titleReveal {
    from { opacity:0; transform:translateX(-20px); filter:blur(6px); }
    to   { opacity:1; transform:translateX(0);     filter:blur(0);   }
}
.page-sub {
    color:#8ecbb8; font-size:0.95rem; font-weight:500;
    letter-spacing:0.04em; margin-bottom:2.2rem;
    animation:fadeSlide 0.7s 0.15s ease both;
}
@keyframes fadeSlide {
    from { opacity:0; transform:translateY(10px); }
    to   { opacity:1; transform:translateY(0); }
}
.section-label {
    font-family:'Orbitron',sans-serif;
    font-size:0.65rem; font-weight:700; color:#00e888;
    text-transform:uppercase; letter-spacing:0.2em;
    margin:1.6rem 0 0.9rem;
    animation:fadeSlide 0.5s ease both;
}

/* ═══════════════════════════════════════
   GLASS CARD
═══════════════════════════════════════ */
.glass {
    background:linear-gradient(135deg,
        rgba(0,35,22,0.94) 0%,
        rgba(0,18,44,0.95) 55%,
        rgba(0,22,58,0.93) 100%);
    border:1px solid rgba(0,200,100,0.28);
    border-radius:18px; padding:1.8rem;
    backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
    position:relative; overflow:hidden;
    transition:border-color 0.4s, box-shadow 0.4s, transform 0.3s;
    animation:glassAppear 0.6s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes glassAppear {
    from { opacity:0; transform:translateY(16px) scale(0.98); }
    to   { opacity:1; transform:translateY(0)    scale(1);    }
}
.glass::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,220,120,0.55),rgba(0,150,255,0.35),transparent);
}
/* Shimmer sweep on hover */
.glass::after {
    content:''; position:absolute; top:0; left:-100%; width:100%; height:100%;
    background:linear-gradient(90deg,transparent,rgba(0,255,150,0.04),transparent);
    transition:left 0.6s ease; pointer-events:none;
}
.glass:hover::after { left:100%; }
.glass:hover {
    border-color:rgba(0,220,120,0.45);
    box-shadow:0 12px 50px rgba(0,200,100,0.14);
    transform:translateY(-2px);
}

/* ═══════════════════════════════════════
   SLIDERS
═══════════════════════════════════════ */
[data-testid="stSlider"]>div>div>div>div {
    background:linear-gradient(135deg,#00c875,#0077ff) !important;
    box-shadow:0 0 14px rgba(0,200,117,0.85) !important;
    transition:box-shadow 0.3s !important;
}
[data-testid="stSlider"]>div>div>div>div:hover {
    box-shadow:0 0 22px rgba(0,200,117,1) !important;
    transform:scale(1.2) !important;
}
[data-testid="stSlider"]>div>div>div {
    background:rgba(0,200,100,0.14) !important;
}
[data-testid="stSlider"] label,
div[data-baseweb="slider"] p {
    color:#8ecbb8 !important; font-weight:500 !important; font-size:0.88rem !important;
}
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
    color:#c0ffe0 !important; font-weight:600 !important;
}

/* ═══════════════════════════════════════
   SELECTBOX
═══════════════════════════════════════ */
div[data-baseweb="select"]>div {
    background:rgba(0,20,45,0.92) !important;
    border:1px solid rgba(0,200,100,0.28) !important;
    border-radius:10px !important; color:#c0ffe0 !important;
    font-size:0.9rem !important;
    transition:border-color 0.3s, box-shadow 0.3s !important;
}
div[data-baseweb="select"]>div:hover {
    border-color:rgba(0,220,120,0.55) !important;
    box-shadow:0 0 18px rgba(0,200,100,0.12) !important;
}
div[data-baseweb="select"] svg   { fill:#00c875 !important; }
div[data-baseweb="select"] li    { background:rgba(0,18,40,0.98) !important; color:#c0ffe0 !important; }
div[data-baseweb="select"] li:hover { background:rgba(0,200,100,0.16) !important; }
label[data-testid="stWidgetLabel"] p,
.stSelectbox label p, .stSlider label p {
    color:#8ecbb8 !important; font-weight:500 !important; font-size:0.88rem !important;
}

/* ═══════════════════════════════════════
   BUTTON
═══════════════════════════════════════ */
div.stButton>button {
    background:linear-gradient(135deg,#00c875 0%,#0077ff 55%,#7c3aed 100%) !important;
    color:#fff !important;
    font-family:'Orbitron',sans-serif !important; font-weight:700 !important;
    font-size:0.88rem !important; letter-spacing:0.12em !important;
    border:none !important; border-radius:12px !important;
    padding:0.9rem 2rem !important; width:100% !important;
    transition:all 0.35s cubic-bezier(0.22,1,0.36,1) !important;
    box-shadow:0 4px 26px rgba(0,200,100,0.45) !important;
    text-transform:uppercase !important;
    position:relative !important; overflow:hidden !important;
}
div.stButton>button::after {
    content:'' !important; position:absolute !important;
    top:0 !important; left:-100% !important;
    width:100% !important; height:100% !important;
    background:linear-gradient(90deg,transparent,rgba(255,255,255,0.15),transparent) !important;
    transition:left 0.5s ease !important;
}
div.stButton>button:hover::after { left:100% !important; }
div.stButton>button:hover {
    transform:translateY(-4px) scale(1.01) !important;
    box-shadow:0 16px 42px rgba(0,200,100,0.65) !important;
    filter:brightness(1.1) !important;
}
div.stButton>button:active {
    transform:scale(0.97) translateY(1px) !important;
    box-shadow:0 2px 12px rgba(0,200,100,0.35) !important;
}

/* ═══════════════════════════════════════
   RESULT CARD
═══════════════════════════════════════ */
@keyframes cardEntrance {
    0%   { opacity:0; transform:scale(0.88) translateY(18px); filter:blur(4px); }
    60%  { transform:scale(1.03) translateY(-3px); filter:blur(0); }
    80%  { transform:scale(0.99) translateY(1px); }
    100% { opacity:1; transform:scale(1) translateY(0); }
}
@keyframes glowBreath {
    0%,100% {
        box-shadow:
            0 0 40px rgba(0,200,100,0.14),
            0 0 80px rgba(0,100,255,0.06),
            inset 0 1px 0 rgba(255,255,255,0.07);
    }
    50% {
        box-shadow:
            0 0 70px rgba(0,200,100,0.28),
            0 0 120px rgba(0,100,255,0.10),
            inset 0 1px 0 rgba(255,255,255,0.12);
    }
}
.result-card {
    background:linear-gradient(145deg,
        rgba(0,45,28,0.97) 0%,
        rgba(0,20,55,0.97) 55%,
        rgba(0,35,85,0.96) 100%);
    border:1px solid rgba(0,220,120,0.42);
    border-radius:24px; padding:2.8rem 2.2rem; text-align:center;
    backdrop-filter:blur(28px); -webkit-backdrop-filter:blur(28px);
    animation:cardEntrance 0.75s cubic-bezier(0.22,1,0.36,1) both,
              glowBreath 5s 1s ease-in-out infinite;
    position:relative; overflow:hidden;
}
/* Top shimmer line */
.result-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,
        transparent, rgba(0,220,120,0.8), rgba(0,150,255,0.5), transparent);
    animation:shimmerLine 3s ease-in-out infinite;
}
@keyframes shimmerLine {
    0%,100% { opacity:0.6; }
    50%     { opacity:1; }
}
/* Radial inner glow */
.result-card::after {
    content:''; position:absolute;
    top:-40%; left:50%; transform:translateX(-50%);
    width:80%; height:80%;
    background:radial-gradient(ellipse,rgba(0,200,100,0.06) 0%,transparent 70%);
    pointer-events:none;
    animation:innerGlow 5s ease-in-out infinite alternate;
}
@keyframes innerGlow {
    from { opacity:0.4; transform:translateX(-50%) scale(0.9); }
    to   { opacity:1;   transform:translateX(-50%) scale(1.1); }
}
.result-label {
    font-family:'Orbitron',sans-serif; font-size:0.72rem; font-weight:700;
    color:#00e888; letter-spacing:0.25em; text-transform:uppercase; margin-bottom:0.6rem;
    animation:fadeSlide 0.5s 0.3s ease both;
}
@keyframes amountReveal {
    0%   { opacity:0; transform:scale(0.75) translateY(10px); filter:blur(12px); }
    70%  { transform:scale(1.04); filter:blur(0); }
    100% { opacity:1; transform:scale(1); }
}
.result-amount {
    font-family:'Orbitron',sans-serif;
    font-size:clamp(2.4rem,5vw,4.2rem); font-weight:900;
    background:linear-gradient(135deg,#80ffcc 0%,#ffffff 45%,#60b8ff 90%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; line-height:1; margin:0.3rem 0 0.7rem;
    animation:amountReveal 0.8s 0.25s cubic-bezier(0.22,1,0.36,1) both;
    position:relative; z-index:2;
}
.result-usd {
    font-family:'Inter',sans-serif; font-size:0.88rem; color:#5ab890;
    margin-bottom:0.8rem; font-weight:500;
    animation:fadeSlide 0.5s 0.5s ease both;
}

/* ═══════════════════════════════════════
   BADGES
═══════════════════════════════════════ */
.badge {
    display:inline-flex; align-items:center; gap:0.4rem;
    padding:0.4rem 1.2rem; border-radius:100px;
    font-size:0.72rem; font-weight:700;
    font-family:'Orbitron',sans-serif; letter-spacing:0.1em;
    text-transform:uppercase;
    transition:transform 0.25s, box-shadow 0.25s;
    animation:badgePop 0.5s 0.55s cubic-bezier(0.34,1.56,0.64,1) both;
}
@keyframes badgePop {
    from { opacity:0; transform:scale(0.7); }
    to   { opacity:1; transform:scale(1); }
}
.badge:hover { transform:scale(1.08); }
.badge-low    { background:rgba(0,200,100,0.14);color:#00e888;border:1px solid rgba(0,220,120,0.40);box-shadow:0 0 18px rgba(0,200,100,0.20) }
.badge-medium { background:rgba(255,185,0,0.14); color:#ffbe00;border:1px solid rgba(255,185,0,0.40);box-shadow:0 0 18px rgba(255,185,0,0.20) }
.badge-high   { background:rgba(255,60,60,0.14); color:#ff5555;border:1px solid rgba(255,70,70,0.40);box-shadow:0 0 18px rgba(255,60,60,0.20) }

/* ═══════════════════════════════════════
   MODEL BADGE
═══════════════════════════════════════ */
.model-badge {
    display:inline-flex; align-items:center; gap:0.5rem;
    padding:0.32rem 0.9rem; border-radius:8px;
    font-size:0.68rem; font-weight:700;
    font-family:'Orbitron',sans-serif; letter-spacing:0.08em;
    background:rgba(99,102,241,0.16); color:#a78bfa;
    border:1px solid rgba(99,102,241,0.32);
    transition:box-shadow 0.3s;
}
.model-badge:hover { box-shadow:0 0 20px rgba(99,102,241,0.3); }

/* ═══════════════════════════════════════
   KPI CARDS
═══════════════════════════════════════ */
.kpi-row { display:flex; gap:0.7rem; flex-wrap:wrap; margin-bottom:1.2rem; }
.kpi {
    flex:1; min-width:68px;
    background:linear-gradient(135deg,rgba(0,55,32,0.92),rgba(0,28,65,0.94));
    border:1px solid rgba(0,200,100,0.28); border-radius:13px;
    padding:0.88rem 0.5rem; text-align:center;
    transition:all 0.35s cubic-bezier(0.22,1,0.36,1);
    position:relative; overflow:hidden;
    animation:kpiSlide 0.5s ease both;
}
.kpi:nth-child(1) { animation-delay:0.1s }
.kpi:nth-child(2) { animation-delay:0.2s }
.kpi:nth-child(3) { animation-delay:0.3s }
@keyframes kpiSlide {
    from { opacity:0; transform:translateY(12px); }
    to   { opacity:1; transform:translateY(0); }
}
.kpi::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,220,120,0.5),transparent);
}
.kpi:hover {
    transform:translateY(-5px) scale(1.03);
    box-shadow:0 10px 32px rgba(0,200,100,0.20);
    border-color:rgba(0,220,120,0.50);
}
.kpi-val { font-family:'Orbitron',sans-serif; font-size:1.3rem; font-weight:700; color:#00e888; }
.kpi-lbl { font-size:0.62rem; color:#6aaa90; text-transform:uppercase; letter-spacing:0.12em; margin-top:0.2rem; font-weight:600; }

/* ═══════════════════════════════════════
   COMPARISON CARDS
═══════════════════════════════════════ */
.cmp {
    background:linear-gradient(135deg,rgba(0,42,26,0.93),rgba(0,20,52,0.95));
    border:1px solid rgba(0,200,100,0.22); border-radius:14px;
    padding:1.1rem 0.7rem; text-align:center;
    transition:all 0.35s cubic-bezier(0.22,1,0.36,1);
    position:relative; overflow:hidden;
}
.cmp::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,220,120,0.4),transparent);
}
.cmp:hover {
    transform:translateY(-5px) scale(1.02);
    box-shadow:0 12px 36px rgba(0,200,100,0.16);
    border-color:rgba(0,220,120,0.42);
}
.cmp-icon  { font-size:1.35rem; margin-bottom:0.3rem; }
.cmp-label { font-size:0.60rem; color:#6aaa90; text-transform:uppercase; letter-spacing:0.12em; font-family:'Orbitron',sans-serif; font-weight:600; }
.cmp-val   { font-family:'Orbitron',sans-serif; font-size:clamp(0.85rem,1.4vw,1rem); font-weight:700; color:#c0ffe0; margin:0.25rem 0; }
.cmp-delta { font-size:0.78rem; font-weight:600; }

/* ═══════════════════════════════════════
   TABS
═══════════════════════════════════════ */
[data-testid="stTabs"] button {
    font-family:'Inter',sans-serif !important; font-weight:600 !important;
    font-size:0.83rem !important; color:#6aaa90 !important;
    letter-spacing:0.03em !important;
    transition:color 0.2s, background 0.2s !important;
    border-radius:6px 6px 0 0 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color:#00e888 !important; border-bottom-color:#00e888 !important;
    background:rgba(0,200,100,0.06) !important;
}
[data-testid="stTabs"] button:hover { color:#80ffcc !important; background:rgba(0,200,100,0.04) !important; }

/* ═══════════════════════════════════════
   DIVIDER
═══════════════════════════════════════ */
hr.fancy {
    border:none; height:1px; margin:1.8rem 0;
    background:linear-gradient(90deg,
        transparent,rgba(0,220,120,0.35),rgba(0,150,255,0.22),transparent);
    animation:hrReveal 0.8s ease both;
}
@keyframes hrReveal {
    from { transform:scaleX(0); opacity:0; }
    to   { transform:scaleX(1); opacity:1; }
}

/* ═══════════════════════════════════════
   BMI BAR
═══════════════════════════════════════ */
.bmi-bar-wrap { margin:0.4rem 0 1rem; }
.bmi-bar-track { height:7px; border-radius:7px; background:rgba(255,255,255,0.07); position:relative; overflow:hidden; }
.bmi-bar-fill  { height:100%; border-radius:7px; transition:width 0.6s cubic-bezier(0.22,1,0.36,1); }
.bmi-label     { font-size:0.75rem; font-weight:700; font-family:'Orbitron',sans-serif; letter-spacing:0.08em; margin-top:0.38rem; }

/* ═══════════════════════════════════════
   STAT CHIPS
═══════════════════════════════════════ */
.stat-row  { display:flex; gap:0.6rem; margin-top:1rem; flex-wrap:wrap; }
.stat-chip {
    flex:1; min-width:80px; padding:0.55rem 0.6rem; border-radius:10px;
    background:rgba(0,40,25,0.88); border:1px solid rgba(0,200,100,0.2);
    text-align:center;
    transition:all 0.3s cubic-bezier(0.22,1,0.36,1);
}
.stat-chip:hover {
    background:rgba(0,55,35,0.92); border-color:rgba(0,200,100,0.38);
    transform:translateY(-2px);
}
.stat-chip-val { font-family:'Orbitron',sans-serif; font-size:0.9rem; font-weight:700; color:#80ffcc; }
.stat-chip-lbl { font-size:0.58rem; color:#5a9a7a; text-transform:uppercase; letter-spacing:0.1em; margin-top:0.15rem; font-weight:600; }

/* ═══════════════════════════════════════
   ALERT BOXES
═══════════════════════════════════════ */
.alert-box {
    padding:0.65rem 1rem; border-radius:10px; margin-top:0.8rem;
    animation:alertSlide 0.4s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes alertSlide {
    from { opacity:0; transform:translateX(-10px); }
    to   { opacity:1; transform:translateX(0); }
}
.alert-smoke { background:rgba(255,60,60,0.10); border:1px solid rgba(255,80,80,0.28); }
.alert-obese { background:rgba(255,180,0,0.09);  border:1px solid rgba(255,180,0,0.26); }

/* ═══════════════════════════════════════
   FEATURE IMPORTANCE BARS
═══════════════════════════════════════ */
.feat-bar-wrap { margin:0.3rem 0 0.8rem; }
.feat-bar-track {
    height:5px; border-radius:5px; background:rgba(255,255,255,0.06);
    overflow:hidden; margin-top:0.2rem;
}
.feat-bar-fill {
    height:100%; border-radius:5px;
    animation:barGrow 0.8s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes barGrow {
    from { width:0 !important; }
}

/* ═══════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════ */
@media(max-width:768px){
    .block-container { padding:1rem !important; }
    .result-amount   { font-size:2rem; }
    .kpi-val         { font-size:1rem; }
    .cmp-val         { font-size:0.82rem; }
    .page-title      { font-size:1.6rem; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FLOATING PARTICLES
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div aria-hidden="true">
  <div class="particle" style="left:8%;  width:3px;height:3px;background:#00e888;opacity:0.4;animation-duration:18s;animation-delay:0s;"></div>
  <div class="particle" style="left:22%; width:2px;height:2px;background:#60b8ff;opacity:0.35;animation-duration:24s;animation-delay:3s;"></div>
  <div class="particle" style="left:38%; width:2px;height:2px;background:#00e888;opacity:0.3;animation-duration:20s;animation-delay:7s;"></div>
  <div class="particle" style="left:55%; width:3px;height:3px;background:#a78bfa;opacity:0.35;animation-duration:22s;animation-delay:2s;"></div>
  <div class="particle" style="left:70%; width:2px;height:2px;background:#60b8ff;opacity:0.3;animation-duration:19s;animation-delay:9s;"></div>
  <div class="particle" style="left:85%; width:3px;height:3px;background:#00e888;opacity:0.4;animation-duration:26s;animation-delay:5s;"></div>
  <div class="particle" style="left:15%; width:2px;height:2px;background:#a78bfa;opacity:0.3;animation-duration:21s;animation-delay:11s;"></div>
  <div class="particle" style="left:48%; width:2px;height:2px;background:#ffbe00;opacity:0.25;animation-duration:23s;animation-delay:14s;"></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  LOAD MODEL & DATA
# ══════════════════════════════════════════════════════════════════════════════
# ── Path resolver: always looks in the SAME folder as app.py ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _find(filename):
    """Look for file in same folder as app.py, then cwd as fallback."""
    candidates = [
        os.path.join(BASE_DIR, filename),   # same folder as app.py  ← primary
        os.path.join(os.getcwd(), filename), # wherever you ran streamlit from
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"\n\n❌  Could not find: {filename}"
        f"\n    Put it in the same folder as app.py:"
        f"\n    👉  {BASE_DIR}\\"
    )

@st.cache_resource
def load_model():
    return pickle.load(open(_find("insurance_model.pkl"), "rb"))

@st.cache_resource
def load_features():
    return pickle.load(open(_find("model_features.pkl"), "rb"))

@st.cache_data
def load_data():
    df = pd.read_csv(_find("insurance.csv"))
    df["charges_inr"] = df["charges"] * USD_TO_INR
    return df

@st.cache_data
def load_score():
    try:
        return json.load(open(_find("model_score.json")))
    except Exception:
        return {"r2": 0.87}

model       = load_model()
features    = load_features()
df          = load_data()
score_data  = load_score()
r2_val      = score_data["r2"]
r2_disp     = f"{r2_val:.2f}"
model_name  = type(model).__name__
model_label = "Random Forest" if "Forest" in model_name else "Linear Reg"

# ══════════════════════════════════════════════════════════════════════════════
#  PREDICTION HELPER
# ══════════════════════════════════════════════════════════════════════════════
REGION_MAP = {
    "southeast": [1,0,0],
    "southwest": [0,1,0],
    "northwest": [0,0,1],
    "northeast": [0,0,0],
}

def predict(age, sex, bmi, children, smoker, region):
    row = [
        age,
        1 if sex    == "Male" else 0,
        bmi,
        children,
        1 if smoker == "Yes"  else 0,
        bmi * age,
        1 if bmi >= 30 else 0,
        *REGION_MAP[region.lower()],
    ]
    return max(0.0, model.predict(np.array(row).reshape(1,-1))[0])

# ══════════════════════════════════════════════════════════════════════════════
#  CHART HELPER
# ══════════════════════════════════════════════════════════════════════════════
def base_layout(height=300, show_legend=True, title_text=None, **extra):
    layout = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#6aaa90", size=11),
        margin=dict(l=8, r=8, t=40 if title_text else 20, b=8),
        height=height, showlegend=show_legend,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#8ecbb8", size=11),
                    bordercolor="rgba(0,200,100,0.12)", borderwidth=1),
    )
    if title_text:
        layout["title"] = dict(text=title_text, font=dict(color="#8ecbb8", size=12, family="Orbitron"))
    layout.update(extra)
    return layout

GRID = dict(gridcolor="rgba(0,200,100,0.06)", gridwidth=1, zeroline=False)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 1 — HEALTH PROFILE FORM
# ══════════════════════════════════════════════════════════════════════════════
def render_form():
    st.markdown('<div class="page-enter">', unsafe_allow_html=True)

    # ── Logo ──
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:2.6rem;
        animation:fadeSlide 0.5s ease both;">
        <span style="font-size:2.2rem;filter:drop-shadow(0 0 12px rgba(0,200,100,0.6));">🏥</span>
        <div>
            <p style="font-family:'Orbitron',sans-serif;font-size:1.45rem;font-weight:900;
                background:linear-gradient(135deg,#00e888,#60b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin:0;letter-spacing:0.06em;">InsureIQ</p>
            <p style="color:#5aaa88;font-size:0.66rem;margin:0;letter-spacing:0.12em;
                text-transform:uppercase;font-weight:600;">AI Medical Cost Predictor</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="page-title">Your Health Profile</p>', unsafe_allow_html=True)
    st.markdown("<p class='page-sub'>Fill in your details — our AI will predict your annual insurance cost.</p>",
                unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")

    # ── LEFT card ──
    with col_l:
        st.markdown('<div class="glass" style="animation-delay:0.1s">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">👤 Personal Information</p>', unsafe_allow_html=True)
        age      = st.slider("Age", 18, 65, st.session_state.inputs.get("age", 30))
        sex_opts = ["Male","Female"]
        sex      = st.selectbox("Biological Sex", sex_opts,
                                index=sex_opts.index(st.session_state.inputs.get("sex","Male")))
        children = st.slider("No. of Children / Dependants", 0, 5,
                             st.session_state.inputs.get("children", 0))
        st.markdown('<p class="section-label" style="margin-top:1.4rem;">📍 Region</p>',
                    unsafe_allow_html=True)
        region_opts = ["Northeast","Northwest","Southeast","Southwest"]
        region = st.selectbox("Your Region", region_opts,
                              index=region_opts.index(st.session_state.inputs.get("region","Northeast")))
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT card ──
    with col_r:
        st.markdown('<div class="glass" style="animation-delay:0.2s">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">🫀 Health Details</p>', unsafe_allow_html=True)
        bmi = st.slider("Body Mass Index (BMI)", 15.0, 55.0,
                        float(st.session_state.inputs.get("bmi", 25.0)), 0.1)

        bmi_cat = ("Underweight" if bmi < 18.5 else
                   "Normal"      if bmi < 25   else
                   "Overweight"  if bmi < 30   else "Obese")
        bmi_color, bmi_pct = {
            "Underweight":("#60b8ff",18), "Normal":("#00e888",42),
            "Overweight":("#ffbe00",68),  "Obese":("#ff5555",94),
        }[bmi_cat]

        st.markdown(f"""
        <div class="bmi-bar-wrap">
            <div class="bmi-bar-track">
                <div class="bmi-bar-fill"
                     style="width:{bmi_pct}%;background:{bmi_color};
                            box-shadow:0 0 10px {bmi_color}88;"></div>
            </div>
            <p class="bmi-label" style="color:{bmi_color};">
                ▸ {bmi_cat}
                <span style="font-size:0.6rem;opacity:0.65;margin-left:0.4rem;">(BMI {bmi:.1f})</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

        smoker_opts = ["No","Yes"]
        smoker = st.selectbox("Do you smoke?", smoker_opts,
                              index=smoker_opts.index(st.session_state.inputs.get("smoker","No")))

        if smoker == "Yes":
            st.markdown("""
            <div class="alert-box alert-smoke">
                <p style="color:#ff8888;font-size:0.78rem;margin:0;font-weight:600;">
                    🚬 Smoking can raise your premium by up to <strong>₹10–12L / year</strong>
                </p>
            </div>""", unsafe_allow_html=True)

        if bmi >= 30:
            st.markdown("""
            <div class="alert-box alert-obese">
                <p style="color:#ffcc44;font-size:0.75rem;margin:0;font-weight:600;">
                    ⚠️ BMI ≥ 30 — flagged as <strong>Obese</strong> by the model, raising predicted cost.
                </p>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Live Preview Card ──
    prev_usd   = predict(age, sex, bmi, children, smoker, region)
    risk_level = "Low" if prev_usd < 8000 else ("Medium" if prev_usd < 20000 else "High")
    risk_class = {"Low":"badge-low","Medium":"badge-medium","High":"badge-high"}[risk_level]
    risk_emoji = {"Low":"💚","Medium":"🟡","High":"🔴"}[risk_level]

    st.markdown(f"""
    <div class="glass" style="text-align:center;padding:1.6rem 1.8rem;
         margin-bottom:1.6rem;animation-delay:0.3s;">
        <p style="font-family:'Orbitron',sans-serif;font-size:0.6rem;color:#00e888;
            letter-spacing:0.24em;text-transform:uppercase;margin-bottom:0.4rem;">
            ⚡ Live Preview
        </p>
        <p style="font-family:'Orbitron',sans-serif;font-size:2.4rem;font-weight:900;
            background:linear-gradient(135deg,#80ffcc,#ffffff,#60b8ff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;margin:0.2rem 0 0.3rem;line-height:1.1;">
            {fmt_inr(prev_usd)}
        </p>
        <p style="font-family:'Inter',sans-serif;font-size:0.8rem;color:#4a9a80;
            margin:0 0 0.6rem;font-weight:500;">
            ≈ ${prev_usd:,.0f} USD &nbsp;·&nbsp; Annual Estimate
        </p>
        <span class="badge {risk_class}">{risk_emoji}&nbsp;{risk_level} Risk</span>
        <div class="stat-row" style="margin-top:1.1rem;">
            <div class="stat-chip"><div class="stat-chip-val">{age}</div><div class="stat-chip-lbl">Age</div></div>
            <div class="stat-chip"><div class="stat-chip-val">{bmi:.1f}</div><div class="stat-chip-lbl">BMI</div></div>
            <div class="stat-chip"><div class="stat-chip-val">{children}</div><div class="stat-chip-lbl">Kids</div></div>
            <div class="stat-chip"><div class="stat-chip-val">{'🚬' if smoker=='Yes' else '✅'}</div><div class="stat-chip-lbl">Smoke</div></div>
            <div class="stat-chip"><div class="stat-chip-val" style="font-size:0.68rem;">{region[:3].upper()}</div><div class="stat-chip-lbl">Region</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CTA button ──
    _, mid, _ = st.columns([1,2,1])
    with mid:
        if st.button("⚡  VIEW FULL REPORT  →"):
            st.session_state.inputs = {
                "age":age, "sex":sex, "bmi":bmi,
                "children":children, "smoker":smoker, "region":region,
            }
            st.session_state.page = "results"
            st.rerun()

    st.markdown(f"""
    <div style="text-align:center;margin-top:1.8rem;">
        <span class="model-badge">🤖 {model_label} &nbsp;·&nbsp; R² {r2_disp}</span>
        <p style="color:#2a6a4a;font-size:0.62rem;margin-top:0.65rem;
            font-family:'Orbitron',sans-serif;letter-spacing:0.1em;">
            INSUREIQ · FOR EDUCATIONAL PURPOSES ONLY · ₹ INDIAN RUPEES
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # page-enter


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE 2 — RESULTS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def render_results():
    st.markdown('<div class="page-enter">', unsafe_allow_html=True)

    inp      = st.session_state.inputs
    age, sex, bmi, children, smoker, region = (
        inp["age"], inp["sex"], inp["bmi"],
        inp["children"], inp["smoker"], inp["region"],
    )
    pred_usd = predict(age, sex, bmi, children, smoker, region)
    pred_inr = to_inr(pred_usd)
    bmi_cat  = ("Underweight" if bmi<18.5 else "Normal" if bmi<25 else "Overweight" if bmi<30 else "Obese")

    risk_level = "Low" if pred_usd<8000 else ("Medium" if pred_usd<20000 else "High")
    risk_class = {"Low":"badge-low","Medium":"badge-medium","High":"badge-high"}[risk_level]
    risk_emoji = {"Low":"💚","Medium":"🟡","High":"🔴"}[risk_level]

    inr_max      = to_inr(65000)
    inr_pred_cap = min(pred_inr, inr_max)
    inr_mean     = to_inr(df["charges"].mean())
    tick_usd     = [0, 15000, 30000, 45000, 60000]

    # ── Top bar ──
    top_l, top_r = st.columns([3, 1.3], gap="large")
    with top_l:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem;">
            <span style="font-size:1.7rem;filter:drop-shadow(0 0 10px rgba(0,200,100,0.5));">🏥</span>
            <p style="font-family:'Orbitron',sans-serif;font-size:1.2rem;font-weight:900;
                background:linear-gradient(135deg,#00e888,#60b8ff);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;margin:0;">InsureIQ</p>
        </div>""", unsafe_allow_html=True)
        st.markdown('<p class="page-title">Your Insurance Report</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="page-sub">Profile: {age}yo {sex} · BMI {bmi:.1f} ({bmi_cat}) · '
            f'{"Smoker" if smoker=="Yes" else "Non-smoker"} · {region}</p>',
            unsafe_allow_html=True)

    with top_r:
        st.markdown(f"""
        <div class="kpi-row" style="margin-top:0.9rem;">
            <div class="kpi">
                <div class="kpi-val">{df.shape[0]:,}</div>
                <div class="kpi-lbl">Records</div>
            </div>
            <div class="kpi">
                <div class="kpi-val">{r2_disp}</div>
                <div class="kpi-lbl">R² (Test)</div>
            </div>
            <div class="kpi">
                <div class="kpi-val" style="font-size:0.75rem;padding-top:0.32rem;">
                    {model_label.split()[0]}
                </div>
                <div class="kpi-lbl">Model</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    bc, _ = st.columns([1,7])
    with bc:
        if st.button("← BACK"):
            st.session_state.page = "form"
            st.rerun()

    st.markdown("<hr class='fancy'>", unsafe_allow_html=True)

    # ── Main 2-col layout ──
    left_col, right_col = st.columns([1.5, 2], gap="large")

    # ═══ LEFT ═══
    with left_col:

        # ── Result card ──
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">⚡ Predicted Annual Cost</div>
            <div class="result-amount">{fmt_inr(pred_usd)}</div>
            <div class="result-usd">≈ ${pred_usd:,.0f} USD &nbsp;·&nbsp; per year</div>
            <span class="badge {risk_class}">{risk_emoji}&nbsp;{risk_level} Risk</span>
            <p style="color:#8ecbb8;font-size:0.73rem;margin-top:1.1rem;line-height:2.1;font-weight:500;">
                {age}yo {sex} &nbsp;·&nbsp; BMI {bmi:.1f} ({bmi_cat})<br>
                {children} child{'ren' if children!=1 else ''} &nbsp;·&nbsp;
                {'🚬 Smoker' if smoker=='Yes' else '✅ Non-smoker'} &nbsp;·&nbsp; {region}
            </p>
            <span class="model-badge" style="margin-top:0.6rem;">🤖 {model_label} · R² {r2_disp}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Gauge ──
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=inr_pred_cap,
            delta={"reference":inr_mean, "valueformat":",.0f",
                   "increasing":{"color":"#ff5555"}, "decreasing":{"color":"#00e888"}},
            number={"prefix":"₹","valueformat":",.0f",
                    "font":{"size":16,"color":"#80ffcc","family":"Orbitron"}},
            title={"text":"vs Dataset Average","font":{"color":"#5a9a7a","size":10}},
            gauge=dict(
                axis=dict(range=[0,inr_max],
                          tickvals=[to_inr(v) for v in tick_usd],
                          ticktext=[fmt_inr(v,short=True) for v in tick_usd],
                          tickcolor="rgba(0,200,100,0.2)",
                          tickfont=dict(color="#5a9a7a",size=8)),
                bar=dict(color="rgba(0,220,120,0.88)", thickness=0.22),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                steps=[
                    dict(range=[0,            to_inr(8000)],  color="rgba(0,200,100,0.07)"),
                    dict(range=[to_inr(8000),  to_inr(20000)],color="rgba(255,185,0,0.07)"),
                    dict(range=[to_inr(20000), inr_max],       color="rgba(255,60,60,0.07)"),
                ],
                threshold=dict(line=dict(color="#00e888",width=2),
                               thickness=0.75, value=inr_pred_cap),
            ),
        ))
        gauge.update_layout(**base_layout(height=218, show_legend=False))
        st.plotly_chart(gauge, use_container_width=True, config={"displayModeBar":False})

        # ── Cost Factor Breakdown ──
        st.markdown('<p class="section-label">📊 Cost Factor Breakdown</p>', unsafe_allow_html=True)
        obese       = 1 if bmi >= 30 else 0
        bmi_age_val = bmi * age
        factors = {
            "Base":       (to_inr(2500),                          "#6366f1"),
            "Age":        (to_inr(max(0,(age-18)*180)),           "#38bdf8"),
            "BMI":        (to_inr(max(0,(bmi-18.5)*160)),         "#a78bfa"),
            "BMI × Age":  (to_inr(max(0,bmi_age_val*0.5)),        "#22d3ee"),
            "Obese Flag": (to_inr(obese*3500),                    "#f59e0b"),
            "Smoking":    (to_inr(14000 if smoker=="Yes" else 0), "#ff5555"),
            "Children":   (to_inr(children*380),                  "#00e888"),
        }
        bar_fig = go.Figure()
        for name, (amt, color) in factors.items():
            bar_fig.add_trace(go.Bar(
                x=[amt], y=[name], orientation="h",
                marker_color=color, marker_line_width=0,
                text=fmt_inr(amt/USD_TO_INR, short=True),
                textposition="outside", textfont=dict(color="#6aaa90",size=9),
                showlegend=False, name=name,
            ))
        bar_fig.update_layout(
            **base_layout(height=245, show_legend=False, barmode="overlay"),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, color="#5a9a7a", tickfont=dict(size=10)),
        )
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar":False})

        # ── Feature importance inline bars ──
        st.markdown('<p class="section-label">🧠 Top Risk Drivers</p>', unsafe_allow_html=True)
        drivers = [
            ("Smoking Status", 0.62 if smoker=="Yes" else 0.10, "#ff5555"),
            ("BMI Score",      min(1.0,(bmi-15)/40),            "#f59e0b"),
            ("Age Factor",     min(1.0,(age-18)/47),            "#38bdf8"),
            ("BMI × Age",      min(1.0,bmi_age_val/2000),       "#22d3ee"),
            ("Region",         0.15,                             "#a78bfa"),
        ]
        for label, pct, color in drivers:
            st.markdown(f"""
            <div class="feat-bar-wrap">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.72rem;color:#8ecbb8;font-weight:500;">{label}</span>
                    <span style="font-size:0.7rem;color:{color};font-family:'Orbitron',sans-serif;
                        font-weight:700;">{pct*100:.0f}%</span>
                </div>
                <div class="feat-bar-track">
                    <div class="feat-bar-fill"
                         style="width:{pct*100:.0f}%;background:{color};
                                box-shadow:0 0 8px {color}66;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ═══ RIGHT ═══
    with right_col:
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📈 Age vs Charges","🗺️ Regional","⚖️ BMI Impact","📦 Distribution"])

        with tab1:
            fig1 = px.scatter(df, x="age", y="charges_inr", color="smoker",
                              color_discrete_map={"yes":"#ff5555","no":"#38bdf8"},
                              opacity=0.5,
                              labels={"age":"Age","charges_inr":"Annual Charges (₹)","smoker":"Smoker"})
            fig1.add_trace(go.Scatter(x=[age], y=[pred_inr], mode="markers",
                marker=dict(size=22,color="#00e888",symbol="star",line=dict(color="white",width=2.5)),
                name="⭐ You"))
            fig1.update_layout(
                **base_layout(height=360, title_text="AGE vs INSURANCE CHARGES"),
                xaxis=dict(title="Age",**GRID),
                yaxis=dict(title="Annual Charges (₹)",tickformat="₹,.0f",**GRID))
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar":False})

        with tab2:
            reg_avg = df.groupby("region")["charges_inr"].mean().reset_index()
            reg_avg.columns = ["Region","Avg (₹)"]
            bar_colors = ["#00e888" if r==region.lower() else "#1e3a5f" for r in reg_avg["Region"]]
            fig2a = go.Figure(go.Bar(
                x=reg_avg["Region"], y=reg_avg["Avg (₹)"],
                marker_color=bar_colors, marker_line_width=0,
                text=[fmt_inr(v/USD_TO_INR,short=True) for v in reg_avg["Avg (₹)"]],
                textposition="outside", textfont=dict(color="#6aaa90",size=10)))
            fig2a.update_layout(
                **base_layout(height=260,show_legend=False,title_text="AVG COST BY REGION  (🟢 = YOURS)"),
                xaxis=dict(**GRID,title=""), yaxis=dict(tickformat="₹,.0f",**GRID))
            st.plotly_chart(fig2a, use_container_width=True, config={"displayModeBar":False})

            rsmk = df.groupby(["region","smoker"])["charges_inr"].mean().reset_index()
            fig2b = px.bar(rsmk, x="region", y="charges_inr", color="smoker", barmode="group",
                           color_discrete_map={"yes":"#ff5555","no":"#00e888"},
                           labels={"charges_inr":"Avg (₹)","region":"Region","smoker":"Smoker"})
            fig2b.update_layout(
                **base_layout(height=260,title_text="SMOKER vs NON-SMOKER BY REGION"),
                xaxis=dict(**GRID,title=""), yaxis=dict(tickformat="₹,.0f",**GRID))
            st.plotly_chart(fig2b, use_container_width=True, config={"displayModeBar":False})

        with tab3:
            fig3 = px.scatter(df, x="bmi", y="charges_inr", color="smoker",
                              trendline="ols", opacity=0.5,
                              color_discrete_map={"yes":"#ff5555","no":"#38bdf8"},
                              labels={"bmi":"BMI","charges_inr":"Annual Charges (₹)","smoker":"Smoker"})
            fig3.add_vline(x=bmi, line_dash="dash", line_color="#00e888", line_width=2,
                           annotation_text=f" Your BMI: {bmi:.1f}",
                           annotation_font=dict(color="#00e888",size=11))
            for zone,x0,x1,col in [
                ("Underweight",15,18.5,"rgba(56,189,248,0.04)"),
                ("Normal",18.5,25,"rgba(0,220,120,0.04)"),
                ("Overweight",25,30,"rgba(255,185,0,0.04)"),
                ("Obese",30,55,"rgba(255,60,60,0.04)"),
            ]:
                fig3.add_vrect(x0=x0,x1=x1,fillcolor=col,line_width=0,
                               annotation_text=zone,annotation_position="top left",
                               annotation_font=dict(size=9,color="#5a9a7a"))
            fig3.update_layout(
                **base_layout(height=370,title_text="BMI vs INSURANCE CHARGES"),
                xaxis=dict(**GRID,title="BMI"),
                yaxis=dict(tickformat="₹,.0f",**GRID,title="Annual Charges (₹)"))
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

        with tab4:
            fig4a = px.histogram(df, x="charges_inr", nbins=55,
                                 color_discrete_sequence=["#00c875"],
                                 labels={"charges_inr":"Annual Charges (₹)"}, opacity=0.75)
            fig4a.add_vline(x=pred_inr, line_dash="dash", line_color="#ffbe00", line_width=2,
                            annotation_text=f" You: {fmt_inr(pred_usd,short=True)}",
                            annotation_font=dict(color="#ffbe00",size=11))
            fig4a.add_vline(x=inr_mean, line_dash="dot", line_color="#38bdf8", line_width=1.5,
                            annotation_text=f" Avg: {fmt_inr(df['charges'].mean(),short=True)}",
                            annotation_font=dict(color="#38bdf8",size=10))
            fig4a.update_layout(
                **base_layout(height=248,show_legend=False,
                              title_text="DISTRIBUTION OF INSURANCE CHARGES"),
                xaxis=dict(tickformat="₹,.0f",**GRID), yaxis=dict(**GRID))
            st.plotly_chart(fig4a, use_container_width=True, config={"displayModeBar":False})

            p1,p2 = st.columns(2)
            with p1:
                smk = df["smoker"].value_counts().reset_index()
                smk.columns = ["Status","Count"]
                fig4b = px.pie(smk, names="Status", values="Count", hole=0.62,
                               color_discrete_sequence=["#ff5555","#00e888"])
                fig4b.update_layout(**base_layout(height=215,title_text="SMOKER RATIO"))
                fig4b.update_traces(textfont=dict(color="#8ecbb8"))
                st.plotly_chart(fig4b, use_container_width=True, config={"displayModeBar":False})
            with p2:
                sx = df["sex"].value_counts().reset_index()
                sx.columns = ["Sex","Count"]
                fig4c = px.pie(sx, names="Sex", values="Count", hole=0.62,
                               color_discrete_sequence=["#38bdf8","#a78bfa"])
                fig4c.update_layout(**base_layout(height=215,title_text="SEX RATIO"))
                fig4c.update_traces(textfont=dict(color="#8ecbb8"))
                st.plotly_chart(fig4c, use_container_width=True, config={"displayModeBar":False})

    # ── Comparison Row ──
    st.markdown("<hr class='fancy'>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">🔍 How You Compare</p>', unsafe_allow_html=True)

    overall_avg = df["charges"].mean()
    age_avg     = df[df["age"].between(age-5,age+5)]["charges"].mean()
    smoker_avg  = df[df["smoker"]==("yes" if smoker=="Yes" else "no")]["charges"].mean()
    region_avg  = df[df["region"]==region.lower()]["charges"].mean()

    for col,(icon,label,avg_usd) in zip(st.columns(4),[
        ("📊","Dataset Average",                             overall_avg),
        ("🎂",f"Age {age-5}–{age+5}",                       age_avg),
        ("🚬","Smokers" if smoker=="Yes" else "Non-Smokers", smoker_avg),
        ("📍", region,                                       region_avg),
    ]):
        avg_usd = avg_usd if not pd.isna(avg_usd) else 0.0
        avg_inr = to_inr(avg_usd)
        delta   = pred_inr - avg_inr
        dcolor  = "#ff5555" if delta > 0 else "#00e888"
        sign    = "+" if delta > 0 else "−"
        with col:
            st.markdown(f"""
            <div class="cmp">
                <div class="cmp-icon">{icon}</div>
                <div class="cmp-label">{label}</div>
                <div class="cmp-val">{fmt_inr(avg_usd,short=True)}</div>
                <div class="cmp-delta" style="color:{dcolor}">
                    {sign} {fmt_inr(abs(delta)/USD_TO_INR,short=True)}
                </div>
            </div>""", unsafe_allow_html=True)

    # ── Trajectory ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">📉 Cost Trajectory — How Your Premium Grows With Age</p>',
                unsafe_allow_html=True)

    ages_range = list(range(18, 66))
    traj_inr   = [to_inr(predict(a,sex,bmi,children,smoker,region)) for a in ages_range]

    traj = go.Figure()
    traj.add_trace(go.Scatter(x=ages_range, y=traj_inr, mode="lines",
        line=dict(color="#00e888",width=2.5),
        fill="tozeroy", fillcolor="rgba(0,220,120,0.06)", name="Projected Cost"))
    traj.add_trace(go.Scatter(x=[age], y=[pred_inr], mode="markers",
        marker=dict(size=16,color="#ffbe00",symbol="star",line=dict(color="white",width=2)),
        name="⭐ You Now"))
    traj.update_layout(
        **base_layout(height=240,title_text="ESTIMATED ANNUAL COST vs AGE (YOUR PROFILE)"),
        xaxis=dict(title="Age",**GRID),
        yaxis=dict(title="Est. Annual Cost (₹)",tickformat="₹,.0f",**GRID))
    st.plotly_chart(traj, use_container_width=True, config={"displayModeBar":False})

    # ── Footer ──
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1rem;
        border-top:1px solid rgba(0,220,120,0.10);margin-top:1rem;">
        <span class="model-badge">🤖 {model_label} &nbsp;·&nbsp; R² {r2_disp}</span>
        <p style="color:#2a6a4a;font-size:0.6rem;margin-top:0.65rem;
            font-family:'Orbitron',sans-serif;letter-spacing:0.14em;">
            INSUREIQ · STREAMLIT + SCIKIT-LEARN · ₹ INDIAN RUPEES · EDUCATIONAL USE ONLY
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # page-enter


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "form":
    render_form()
else:
    render_results()
