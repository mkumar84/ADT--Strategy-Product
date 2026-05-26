# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

def hex_rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RBC ADT · Product Strategy",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design tokens ─────────────────────────────────────────────────────────────
RBC_BLUE  = "#003168"
RBC_GOLD  = "#FFBF00"
RBC_TEXT  = "#1A1A2E"
RBC_MUTED = "#6B7280"

STATUS_CLR = {
    "Delivered":   "#22C55E",
    "In Progress": "#3B82F6",
    "Planned":     "#A855F7",
    "On Hold":     "#F59E0B",
}
LOB_CLR = {
    "Personal & Commercial Banking": "#3B82F6",
    "Wealth Management":             "#8B5CF6",
    "Capital Markets":               "#10B981",
    "Insurance":                     "#F59E0B",
    "Investor & Treasury Services":  "#EF4444",
    "Enterprise / Cross-LOB":        "#6366F1",
}
PHASE_CLR = {
    "Foundation":          "#22C55E",
    "Data Connectivity":   "#3B82F6",
    "Intelligence Layer":  "#A855F7",
    "Enterprise Scale":    "#F59E0B",
}
BANK_CLR = {
    "RBC":              RBC_BLUE,
    "TD Bank":          "#00A651",
    "BMO":              "#0079C2",
    "Scotiabank":       "#C8102E",
    "CIBC":             "#C41F3E",
    "National Bank":    "#E31837",
    "JPMorgan Chase":   "#1C2E4A",
}

# ── Global CSS (Wealthsimple layout + Lemonade pill micro-interactions) ───────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {RBC_TEXT};
    background: #F7F8FA;
  }}
  .block-container {{ padding: 1.5rem 2.5rem 3rem; max-width: 1460px; }}

  /* ── Lemonade-inspired pill shake + pop ─────────────────────── */
  @keyframes pill-pop {{
    0%   {{ transform: scale(1)    rotate(0deg)  translateY(0px);  }}
    22%  {{ transform: scale(1.15) rotate(-6deg) translateY(-6px); }}
    44%  {{ transform: scale(1.18) rotate(6deg)  translateY(-7px); }}
    66%  {{ transform: scale(1.13) rotate(-3deg) translateY(-5px); }}
    88%  {{ transform: scale(1.11) rotate(1deg)  translateY(-3px); }}
    100% {{ transform: scale(1.11) rotate(0deg)  translateY(-3px); }}
  }}
  @keyframes badge-pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(255,255,255,.55); }}
    60%  {{ box-shadow: 0 0 0 7px rgba(255,255,255,.0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(255,255,255,.0); }}
  }}

  .badge {{
    display: inline-block;
    font-size: .7rem; font-weight: 700;
    padding: .25rem .72rem;
    border-radius: 999px;
    margin: .12rem .22rem;
    color: white;
    cursor: pointer;
    will-change: transform;
    transform-origin: center bottom;
    letter-spacing: .025em;
    user-select: none;
    transition: filter .15s ease, box-shadow .15s ease;
    position: relative;
  }}
  .badge:hover {{
    animation: pill-pop .4s cubic-bezier(.36,.07,.19,.97) forwards,
               badge-pulse .6s ease .1s forwards;
    filter: brightness(1.22) saturate(1.2);
    box-shadow: 0 9px 24px rgba(0,0,0,.32);
    z-index: 20;
  }}

  /* ── Wealthsimple-style KPI card with spring lift ─────────────── */
  .kpi-card {{
    background: white;
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    border-top: 3px solid {RBC_GOLD};
    box-shadow: 0 2px 12px rgba(0,0,0,.05);
    transition: transform .25s cubic-bezier(.34,1.56,.64,1),
                box-shadow .25s ease;
    cursor: default;
    min-height: 120px;
  }}
  .kpi-card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 16px 40px rgba(0,0,0,.11);
  }}
  .kpi-label {{ font-size: .72rem; font-weight: 700; color: {RBC_MUTED};
               text-transform: uppercase; letter-spacing: .07em; margin-bottom: .45rem; }}
  .kpi-value {{ font-size: 2.05rem; font-weight: 800; color: {RBC_BLUE}; line-height: 1.1; }}
  .kpi-delta {{ font-size: .8rem; color: #22C55E; margin-top: .3rem; font-weight: 500; }}

  /* ── Section heading ──────────────────────────────────────────── */
  .section-title {{
    font-size: 1rem; font-weight: 700; color: {RBC_BLUE};
    border-bottom: 2px solid {RBC_GOLD};
    padding-bottom: .4rem; margin-bottom: 1rem;
  }}

  /* ── Initiative card with spring slide-right ──────────────────── */
  .init-card {{
    background: white; border-radius: 14px;
    padding: 1.1rem 1.35rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
    margin-bottom: .82rem; border-left: 5px solid #E5E7EB;
    transition: transform .2s cubic-bezier(.34,1.56,.64,1),
                box-shadow .2s ease;
    cursor: pointer;
  }}
  .init-card:hover {{
    transform: translateX(6px) scale(1.007);
    box-shadow: 0 10px 28px rgba(0,0,0,.1);
  }}
  .init-title {{ font-size: .96rem; font-weight: 700; }}
  .init-meta  {{ font-size: .78rem; color: {RBC_MUTED}; margin-top: .22rem; }}
  .init-desc  {{ font-size: .82rem; color: {RBC_MUTED}; margin-top: .5rem; line-height: 1.5; }}
  .init-kpi   {{ font-size: .81rem; font-weight: 600; color: {RBC_BLUE}; margin-top: .45rem; }}

  /* ── Phase card (Product Roadmap tab) ─────────────────────────── */
  .phase-card {{
    background: white; border-radius: 16px;
    padding: 1.5rem 1.35rem;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
    border-top: 5px solid #E5E7EB;
    transition: transform .22s cubic-bezier(.34,1.56,.64,1),
                box-shadow .22s ease;
    height: 100%;
  }}
  .phase-card:hover {{
    transform: translateY(-8px);
    box-shadow: 0 20px 44px rgba(0,0,0,.12);
  }}
  .phase-label {{
    display: inline-block; font-size: .68rem; font-weight: 700;
    padding: .18rem .6rem; border-radius: 6px; color: white;
    margin-bottom: .6rem; letter-spacing: .04em;
  }}
  .phase-live {{
    display: inline-block; font-size: .68rem; font-weight: 700;
    padding: .18rem .6rem; border-radius: 6px;
    background: rgba(34,197,94,.15); color: #16A34A;
    margin-left: .4rem; letter-spacing: .03em;
  }}
  .phase-title  {{ font-size: 1.05rem; font-weight: 700; margin-bottom: .2rem; }}
  .phase-period {{ font-size: .78rem; color: {RBC_MUTED}; margin-bottom: .8rem; }}
  .feat-row {{
    display: flex; align-items: flex-start; gap: .48rem;
    font-size: .82rem; color: #374151; margin-bottom: .42rem; line-height: 1.45;
  }}
  .feat-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    flex-shrink: 0; margin-top: 4px;
  }}

  /* ── Roadmap step bar at top of Product Roadmap ───────────────── */
  .rm-stepper {{
    display: flex; align-items: stretch;
    background: white; border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,.06);
    overflow: hidden; margin-bottom: 1.6rem;
  }}
  .rm-step {{
    flex: 1; padding: 1rem 1.1rem; position: relative;
    transition: background .2s ease;
    cursor: default;
  }}
  .rm-step:not(:last-child)::after {{
    content: ''; position: absolute;
    right: 0; top: 20%; bottom: 20%;
    width: 1px; background: #E5E7EB;
  }}
  .rm-step:hover {{ background: #F9FAFB; }}
  .rm-step-label {{ font-size: .7rem; font-weight: 700; text-transform: uppercase;
                   letter-spacing: .06em; margin-bottom: .2rem; }}
  .rm-step-title {{ font-size: .88rem; font-weight: 700; margin-bottom: .1rem; }}
  .rm-step-period {{ font-size: .75rem; color: {RBC_MUTED}; }}

  /* ── Competitive card ──────────────────────────────────────────── */
  .comp-card {{
    background: white; border-radius: 14px;
    padding: 1.1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
    border-left: 5px solid #E5E7EB;
    transition: transform .2s cubic-bezier(.34,1.56,.64,1),
                box-shadow .2s ease;
    height: 100%;
  }}
  .comp-card:hover {{
    transform: translateX(5px);
    box-shadow: 0 8px 24px rgba(0,0,0,.1);
  }}
  .comp-name  {{ font-size: .95rem; font-weight: 700; margin-bottom: .15rem; }}
  .comp-spend {{ font-size: .77rem; color: {RBC_MUTED}; margin-bottom: .5rem; }}
  .comp-item  {{ font-size: .8rem; color: #374151; margin-bottom: .3rem; line-height: 1.42; }}
  .disclaimer {{
    font-size: .72rem; color: {RBC_MUTED}; font-style: italic;
    background: #F9FAFB; border-radius: 8px; padding: .5rem .8rem;
    border-left: 3px solid #E5E7EB; margin-bottom: 1rem;
  }}

  /* ── Page hero header ──────────────────────────────────────────── */
  .page-header {{
    background: linear-gradient(135deg, {RBC_BLUE} 0%, #00509E 100%);
    border-radius: 18px; padding: 1.8rem 2.2rem;
    margin-bottom: 1.8rem; position: relative; overflow: hidden;
  }}
  .page-header::before {{
    content: ''; position: absolute; top: -45%; right: -3%;
    width: 290px; height: 290px;
    background: rgba(255,191,0,.13); border-radius: 50%;
    pointer-events: none;
  }}
  .page-header::after {{
    content: ''; position: absolute; bottom: -60%; left: 30%;
    width: 200px; height: 200px;
    background: rgba(255,255,255,.04); border-radius: 50%;
    pointer-events: none;
  }}
  .page-header h1 {{ font-size: 1.55rem; font-weight: 800; margin: 0; color: white; }}
  .page-header p  {{ font-size: .88rem; opacity: .72; margin: .45rem 0 0; color: white; }}
  .header-badges  {{ margin-top: .9rem; display: flex; flex-wrap: wrap; gap: .4rem; }}
  .header-badge {{
    display: inline-flex; align-items: center; gap: .3rem;
    background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25);
    color: white; font-size: .75rem; font-weight: 600;
    padding: .28rem .75rem; border-radius: 999px;
    backdrop-filter: blur(4px);
    transition: background .2s ease, transform .2s cubic-bezier(.34,1.56,.64,1);
    cursor: default;
  }}
  .header-badge:hover {{
    background: rgba(255,255,255,.25);
    transform: translateY(-2px);
  }}

  /* ── Streamlit tab overrides ───────────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {{
    gap: .35rem; border-bottom: 2px solid #E5E7EB; padding-bottom: 0;
  }}
  .stTabs [data-baseweb="tab"] {{
    font-weight: 600; font-size: .88rem;
    padding: .5rem 1.05rem; border-radius: 8px 8px 0 0;
    color: {RBC_MUTED}; background: transparent; border: none;
    transition: color .15s, background .15s;
  }}
  .stTabs [data-baseweb="tab"]:hover {{
    color: {RBC_BLUE}; background: rgba(0,49,104,.05);
  }}
  .stTabs [aria-selected="true"] {{
    color: {RBC_BLUE} !important; background: white !important;
    border-bottom: 3px solid {RBC_GOLD} !important; font-weight: 700 !important;
  }}
  /* ── Stage progression stepper ────────────────────────────────── */
  .stage-stepper {{
    display: flex; align-items: center;
    background: white; border-radius: 14px;
    padding: 1.3rem 2rem; margin-top: 1.1rem;
    box-shadow: 0 2px 10px rgba(0,0,0,.06);
  }}
  .stage-node {{
    display: flex; flex-direction: column; align-items: center;
    gap: .28rem; flex: 1; min-width: 0;
  }}
  .stage-dot {{
    width: 44px; height: 44px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: .95rem; color: white;
    cursor: default;
    box-shadow: 0 3px 10px rgba(0,0,0,.14);
    transition: transform .22s cubic-bezier(.34,1.56,.64,1),
                box-shadow .22s ease;
  }}
  .stage-dot:hover {{
    transform: scale(1.22) translateY(-3px);
    box-shadow: 0 10px 24px rgba(0,0,0,.22);
  }}
  .stage-label {{
    font-size: .76rem; font-weight: 700; color: {RBC_TEXT};
    text-align: center; white-space: nowrap;
  }}
  .stage-sub {{
    font-size: .68rem; color: {RBC_MUTED}; text-align: center;
  }}
  .stage-line {{
    flex: 0.55; height: 3px; border-radius: 2px;
    margin-bottom: 1.8rem;
  }}

  footer {{ visibility: hidden; }} #MainMenu {{ visibility: hidden; }}

  /* ── Custom footer ─────────────────────────────────────────────── */
  .custom-footer {{
    text-align: center;
    padding: 2rem 0 .5rem;
    margin-top: 3rem;
    border-top: 1px solid #E5E7EB;
    font-size: .8rem;
    color: {RBC_MUTED};
    letter-spacing: .02em;
  }}
  .custom-footer strong {{ color: {RBC_BLUE}; font-weight: 700; }}
  .custom-footer .heart {{ color: #EF4444; font-size: .95rem; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════════════════════

INITIATIVES = pd.DataFrame([
    dict(id="ADT-001", name="Client Intelligence Platform",
         lob="Personal & Commercial Banking", pillar="Client First",
         impact_type="Revenue Uplift", impact_m=85,
         status="Delivered", stage="Scale",
         start=date(2023,1,1), end=date(2024,6,30),
         description="AI-driven hyper-personalization for 17M+ retail clients; next-best-action engine across digital channels.",
         kpis="+$85M revenue | 34% offer take-up lift | NPS +12 pts"),

    dict(id="ADT-002", name="Real-Time Fraud Detection AI",
         lob="Enterprise / Cross-LOB", pillar="Do What's Right",
         impact_type="Cost Savings", impact_m=62,
         status="Delivered", stage="Scale",
         start=date(2023,4,1), end=date(2024,3,31),
         description="ML ensemble replacing rules-based fraud detection; sub-50ms decisioning across cards, wires, and e-transfers.",
         kpis="$62M fraud loss avoided | False-positive rate -41% | 99.97% uptime"),

    dict(id="ADT-003", name="AI Contact Centre — Virtual Agents",
         lob="Personal & Commercial Banking", pillar="Operational Excellence",
         impact_type="Cost Savings", impact_m=44,
         status="In Progress", stage="Pilot to Scale",
         start=date(2024,1,1), end=date(2025,6,30),
         description="Conversational AI for Tier-1 and Tier-2 inquiries with live-agent Assist overlay for complex calls.",
         kpis="$44M cost reduction target | 62% containment rate | AHT -28%"),

    dict(id="ADT-004", name="Automated Credit Decisioning",
         lob="Personal & Commercial Banking", pillar="Growth Mindset",
         impact_type="Revenue + Cost", impact_m=38,
         status="In Progress", stage="Build",
         start=date(2024,3,1), end=date(2025,9,30),
         description="End-to-end ML credit engine for personal loans and SMB credit; straight-through processing target >80%.",
         kpis="$38M impact | STP rate 82% target | Decision time: 4 days to 4 min"),

    dict(id="ADT-005", name="Intelligent Document Processing",
         lob="Enterprise / Cross-LOB", pillar="Operational Excellence",
         impact_type="Cost Savings", impact_m=32,
         status="Delivered", stage="Scale",
         start=date(2023,7,1), end=date(2024,6,30),
         description="LLM + OCR pipeline for mortgage, AML, and onboarding documents; replaces 1.2M manual reviews annually.",
         kpis="$32M savings | 93% straight-through | 1.2M reviews automated"),

    dict(id="ADT-006", name="Capital Markets AI Analytics Suite",
         lob="Capital Markets", pillar="Growth Mindset",
         impact_type="Revenue Uplift", impact_m=55,
         status="In Progress", stage="Build",
         start=date(2024,6,1), end=date(2026,3,31),
         description="Generative AI research assistant, trade-idea generation, and portfolio risk summarization for RBC CM traders.",
         kpis="$55M revenue target | 40 traders onboarded | 3 hrs/day saved per trader"),

    dict(id="ADT-007", name="Regulatory Compliance Automation",
         lob="Enterprise / Cross-LOB", pillar="Do What's Right",
         impact_type="Risk Avoidance", impact_m=28,
         status="Delivered", stage="Scale",
         start=date(2023,10,1), end=date(2024,9,30),
         description="AI monitoring for FINTRAC, AML, and KYC obligations; continuous regulatory change tracking.",
         kpis="$28M risk avoidance | 70% manual review reduction | Audit findings -55%"),

    dict(id="ADT-008", name="Wealth Advisor AI Platform",
         lob="Wealth Management", pillar="Client First",
         impact_type="Revenue Uplift", impact_m=47,
         status="In Progress", stage="Pilot",
         start=date(2024,9,1), end=date(2026,6,30),
         description="AI-generated portfolio insights, proposal drafting, and client meeting prep for 2,000+ RBC DS advisors.",
         kpis="$47M AUM uplift target | 2.5 hrs/week saved per advisor | Pilot NPS 68"),

    dict(id="ADT-009", name="AI-Enhanced Risk Models",
         lob="Capital Markets", pillar="Do What's Right",
         impact_type="Cost Savings", impact_m=41,
         status="Planned", stage="Discovery",
         start=date(2025,1,1), end=date(2026,12,31),
         description="Replace legacy VaR models with deep-learning ensemble; real-time stress testing across 80+ risk factors.",
         kpis="$41M capital efficiency | VaR accuracy +18% | Stress test: 6h to 12min"),

    dict(id="ADT-010", name="Digital Onboarding Transformation",
         lob="Personal & Commercial Banking", pillar="Client First",
         impact_type="Cost Savings", impact_m=30,
         status="Delivered", stage="Scale",
         start=date(2023,1,1), end=date(2023,12,31),
         description="Fully digital account opening with AI identity verification; STP for 85% of retail account openings.",
         kpis="$30M savings | Onboarding: 8 days to 7 min | Drop-off rate -38%"),

    dict(id="ADT-011", name="Insurance Underwriting AI",
         lob="Insurance", pillar="Growth Mindset",
         impact_type="Revenue + Cost", impact_m=29,
         status="Planned", stage="Discovery",
         start=date(2025,4,1), end=date(2026,9,30),
         description="Predictive underwriting for home and auto; dynamic pricing using 200+ alternative data signals.",
         kpis="$29M impact target | Loss ratio improvement 3.2 pts | Quote time -65%"),

    dict(id="ADT-012", name="ITS Liquidity Intelligence Engine",
         lob="Investor & Treasury Services", pillar="Operational Excellence",
         impact_type="Cost Savings", impact_m=26,
         status="Planned", stage="Build",
         start=date(2025,1,1), end=date(2026,6,30),
         description="ML-driven intraday liquidity forecasting for RBC's $500B+ treasury operations.",
         kpis="$26M funding cost savings | Forecast accuracy +22% | Intraday buffer -$1.2B"),
])

PILLARS = pd.DataFrame([
    dict(pillar="Client First",           initiatives=4, value_m=262, color="#3B82F6"),
    dict(pillar="Do What's Right",        initiatives=3, value_m=131, color="#22C55E"),
    dict(pillar="Growth Mindset",         initiatives=3, value_m=122, color="#8B5CF6"),
    dict(pillar="Operational Excellence", initiatives=3, value_m=102, color="#F59E0B"),
])

# Product Roadmap phases (this platform's own evolution)
PHASES = [
    {
        "phase": "Foundation",
        "label": "Phase 1  LIVE",
        "period": "Q2 FY25 — Ongoing",
        "color": "#22C55E",
        "live": True,
        "features": [
            "Core KPI dashboard with portfolio-level metrics",
            "Initiative portfolio management (12 ADT initiatives)",
            "Multi-year Gantt timeline with status tracking",
            "Strategic pillar alignment mapping",
            "Market intelligence and competitive landscape",
            "Filterable initiative cards by LOB, status, impact",
        ],
    },
    {
        "phase": "Data Connectivity",
        "label": "Phase 2",
        "period": "Q3 FY25 — Q1 FY26",
        "color": "#3B82F6",
        "live": False,
        "features": [
            "JIRA / Azure DevOps live project status sync",
            "SharePoint and Teams content integration",
            "Automated financial impact refresh from Finance systems",
            "SSO via Azure Active Directory / RBC IAM",
            "Role-based access control (LOB lead, Exec, PMO)",
            "Export to PowerPoint and PDF for ExCo reviews",
        ],
    },
    {
        "phase": "Intelligence Layer",
        "label": "Phase 3",
        "period": "Q2 FY26 — Q3 FY26",
        "color": "#A855F7",
        "live": False,
        "features": [
            "Natural language query interface (ask your portfolio)",
            "AI-generated initiative risk and success scoring",
            "Automated stakeholder update narratives (Word / PPT)",
            "Portfolio anomaly detection with Slack / Teams alerts",
            "Predictive financial impact modeling (Monte Carlo)",
            "Cross-initiative dependency graph visualization",
        ],
    },
    {
        "phase": "Enterprise Scale",
        "label": "Phase 4",
        "period": "Q4 FY26+",
        "color": "#F59E0B",
        "live": False,
        "features": [
            "Full LOB self-service intake and prioritization portal",
            "API-first architecture for enterprise system integrations",
            "Real-time competitive intelligence data feeds",
            "Mobile-responsive executive dashboard (iOS / Android)",
            "Bilingual support (English / French)",
            "AI-powered capital allocation scenario modeler",
        ],
    },
]

# Competitive landscape — illustrative estimates from public disclosures
COMPETITORS = [
    {
        "bank": "RBC",
        "tag": "US",
        "color": RBC_BLUE,
        "highlight": True,
        "tech_spend": "~$5.1B annual",
        "ai_maturity": 4.5, "digital": 4.6, "cx": 4.4, "innovation": 4.3, "reusability": 4.6,
        "program": "AI & Digital Transformation (ADT)",
        "initiatives": [
            "ADT portfolio: $517M+ financial impact",
            "Client Intelligence Platform — 17M clients",
            "Fraud AI — sub-50ms real-time decisioning",
            "Capital Markets AI Analytics Suite",
            "Reusable AI platform: 12 cross-LOB initiatives",
        ],
    },
    {
        "bank": "TD Bank",
        "tag": "CA",
        "color": "#00A651",
        "highlight": False,
        "tech_spend": "~$6.2B annual",
        "ai_maturity": 4.1, "digital": 4.3, "cx": 4.2, "innovation": 4.0, "reusability": 3.8,
        "program": "TD Digital Strategy 2025",
        "initiatives": [
            "TD Clari — retail virtual assistant",
            "AI-powered credit fraud prevention",
            "Open Banking API platform rollout",
            "Aeroplan credit AI decisioning engine",
        ],
    },
    {
        "bank": "BMO",
        "tag": "CA",
        "color": "#0079C2",
        "highlight": False,
        "tech_spend": "~$3.2B annual",
        "ai_maturity": 3.7, "digital": 4.0, "cx": 3.8, "innovation": 3.9, "reusability": 3.5,
        "program": "BMO Digital First",
        "initiatives": [
            "Project Keystone — AI and Cloud migration",
            "BMO Digital Cash Management for SMB",
            "AML AI monitoring and alert triage",
            "Mortgage AI decisioning pilot",
        ],
    },
    {
        "bank": "Scotiabank",
        "tag": "CA",
        "color": "#C8102E",
        "highlight": False,
        "tech_spend": "~$3.8B annual",
        "ai_maturity": 3.8, "digital": 4.1, "cx": 3.9, "innovation": 4.0, "reusability": 3.6,
        "program": "Scotiabank Digital Transformation",
        "initiatives": [
            "Digital Factory AI Labs — 400-person team",
            "AI-powered personalized financial advice",
            "Open Banking via Scotia Connect",
            "Real-time fraud ML engine deployment",
        ],
    },
    {
        "bank": "CIBC",
        "tag": "CA",
        "color": "#C41F3E",
        "highlight": False,
        "tech_spend": "~$2.9B annual",
        "ai_maturity": 3.4, "digital": 3.8, "cx": 3.7, "innovation": 3.5, "reusability": 3.2,
        "program": "CIBC Digital Ambition",
        "initiatives": [
            "CIBC Virtual Assistant — retail and business",
            "GoalPlanner AI for advisor-led wealth planning",
            "Intelligent Banking Platform modernization",
            "AI credit underwriting for SMB",
        ],
    },
    {
        "bank": "JPMorgan Chase",
        "tag": "US",
        "color": "#1C2E4A",
        "highlight": False,
        "tech_spend": "~$15B annual",
        "ai_maturity": 4.8, "digital": 4.9, "cx": 4.5, "innovation": 4.7, "reusability": 4.5,
        "program": "JPM AI & Data Science Strategy",
        "initiatives": [
            "LLM Suite deployed to 50,000+ employees",
            "COIN — legal document AI (360K hrs/yr saved)",
            "IndexGPT — thematic investment AI",
            "Chase AI Advisor for retail clients",
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def kpi(label, value, delta=""):
    dh = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {dh}
    </div>""", unsafe_allow_html=True)

def badge(text, color):
    return f'<span class="badge" style="background:{color}">{text}</span>'

def initiative_card(row):
    sc = STATUS_CLR.get(row.status, "#6B7280")
    lc = LOB_CLR.get(row.lob, "#6B7280")
    st.markdown(f"""
    <div class="init-card" style="border-left-color:{sc}">
      <div class="init-title">{row["name"]}
        <span style="float:right;font-size:.78rem;font-weight:700;
               background:linear-gradient(135deg,{RBC_BLUE},{sc});
               -webkit-background-clip:text;-webkit-text-fill-color:transparent">
          ${row.impact_m}M
        </span>
      </div>
      <div class="init-meta">
        {badge(row.status, sc)}
        {badge(row.lob, lc)}
        {badge(row.pillar, RBC_BLUE)}
        {badge(row.stage, "#6B7280")}
      </div>
      <div class="init-desc">{row.description}</div>
      <div class="init-kpi">&#128200; {row.kpis}</div>
    </div>""", unsafe_allow_html=True)

def phase_card(p):
    c = p["color"]
    live_html = '<span class="phase-live">&#9679; LIVE</span>' if p["live"] else ""
    features_html = "".join(
        f'<div class="feat-row">'
        f'<span class="feat-dot" style="background:{c}"></span>'
        f'<span>{f}</span></div>'
        for f in p["features"]
    )
    st.markdown(f"""
    <div class="phase-card" style="border-top-color:{c}">
      <div>
        <span class="phase-label" style="background:{c}">{p["label"]}</span>
        {live_html}
      </div>
      <div class="phase-title">{p["phase"]}</div>
      <div class="phase-period">&#128197; {p["period"]}</div>
      {features_html}
    </div>""", unsafe_allow_html=True)

def comp_card(c):
    border = c["color"]
    star = " &#11088;" if c["highlight"] else ""
    items_html = "".join(
        f'<div class="comp-item">&#8250; {i}</div>' for i in c["initiatives"]
    )
    st.markdown(f"""
    <div class="comp-card" style="border-left-color:{border}">
      <div class="comp-name" style="color:{border}">{c["bank"]}{star}</div>
      <div class="comp-spend">&#128181; {c["tech_spend"]} tech investment</div>
      <div style="margin-bottom:.45rem">
        {badge(c["program"], border)}
      </div>
      {items_html}
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
  <h1>&#127970; &nbsp;RBC AI Group &mdash; ADT Product Strategy</h1>
  <p>Director, Product Management &amp; Strategy &nbsp;&middot;&nbsp;
     AI &amp; Digital Transformation Portfolio &nbsp;&middot;&nbsp;
     $25M+ Impact Threshold</p>
  <div class="header-badges">
    <span class="header-badge">&#128200; $517M Portfolio</span>
    <span class="header-badge">&#9989; 5 Delivered</span>
    <span class="header-badge">&#128101; 17M+ Clients Impacted</span>
    <span class="header-badge">&#127775; 12 ADT Initiatives</span>
    <span class="header-badge">&#127760; 5 Lines of Business</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "&#128202;  Executive Dashboard",
    "&#128200;  ADT Initiatives",
    "&#128203;  Initiative Portfolio",
    "&#129517;  Strategic Alignment",
    "&#128506;  Product Roadmap",
    "&#127758;  Market Intelligence",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1  EXECUTIVE DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tabs[0]:
    total_v    = INITIATIVES.impact_m.sum()
    delivered_v = INITIATIVES[INITIATIVES.status == "Delivered"].impact_m.sum()
    inprog_v   = INITIATIVES[INITIATIVES.status == "In Progress"].impact_m.sum()
    n_del      = int((INITIATIVES.status == "Delivered").sum())
    n_total    = len(INITIATIVES)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total Portfolio Value",    f"${total_v}M",        f"Across {n_total} ADT initiatives")
    with c2: kpi("Value Delivered",          f"${delivered_v}M",    f"{n_del} initiatives at Scale")
    with c3: kpi("In-Flight Value",          f"${inprog_v}M",       "4 active build / pilot programs")
    with c4: kpi("Avg Impact per Initiative",f"${round(total_v/n_total)}M", "All above $25M threshold")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.markdown('<div class="section-title">Portfolio Value by Line of Business</div>', unsafe_allow_html=True)
        lob_df = INITIATIVES.groupby("lob", as_index=False).agg(value=("impact_m","sum"), count=("id","count"))
        fig = px.bar(lob_df.sort_values("value"), x="value", y="lob", orientation="h",
                     text="value", color="lob", color_discrete_map=LOB_CLR,
                     labels={"value":"Financial Impact ($M)","lob":""}, height=320)
        fig.update_traces(texttemplate="$%{text}M", textposition="outside")
        fig.update_layout(showlegend=False, margin=dict(l=0,r=20,t=10,b=10),
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                          yaxis=dict(tickfont=dict(size=11)))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Portfolio Status Mix</div>', unsafe_allow_html=True)
        status_df = INITIATIVES.groupby("status", as_index=False).agg(value=("impact_m","sum"))
        fig2 = go.Figure(go.Pie(
            labels=status_df.status, values=status_df.value,
            hole=.56, textinfo="label+percent",
            marker=dict(colors=[STATUS_CLR.get(s,"#ccc") for s in status_df.status]),
        ))
        fig2.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10),
                           height=290, paper_bgcolor="white",
                           annotations=[dict(text=f"${total_v}M<br>total",
                                             x=.5, y=.5, font_size=15, showarrow=False)])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">Impact Type Breakdown</div>', unsafe_allow_html=True)
    imp_df = INITIATIVES.groupby("impact_type", as_index=False).impact_m.sum().sort_values("impact_m", ascending=False)
    clrs = [RBC_BLUE, "#00509E", RBC_GOLD, "#005DAA", "#4A90D9"]
    fig3 = px.bar(imp_df, x="impact_type", y="impact_m", text="impact_m",
                  color="impact_type",
                  color_discrete_sequence=clrs,
                  labels={"impact_m":"$M","impact_type":""}, height=240)
    fig3.update_traces(texttemplate="$%{text}M", textposition="outside")
    fig3.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                       margin=dict(l=0,r=0,t=10,b=10),
                       yaxis=dict(showgrid=True, gridcolor="#F0F0F0"))
    st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2  ADT INITIATIVES (multi-year Gantt)
# ─────────────────────────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="section-title">Multi-Year ADT Initiative Timeline</div>', unsafe_allow_html=True)

    leg_cols = st.columns(len(STATUS_CLR))
    for i, (s, c) in enumerate(STATUS_CLR.items()):
        with leg_cols[i]:
            st.markdown(badge(s, c), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    df_r = INITIATIVES.copy()
    df_r["start_dt"] = pd.to_datetime(df_r["start"])
    df_r["end_dt"]   = pd.to_datetime(df_r["end"])
    df_r["label"]    = df_r["name"] + "  ·  $" + df_r["impact_m"].astype(str) + "M"

    fig_g = px.timeline(
        df_r.sort_values("start_dt"),
        x_start="start_dt", x_end="end_dt", y="label",
        color="status", color_discrete_map=STATUS_CLR,
        hover_data={"lob":True,"pillar":True,"impact_m":True,
                    "stage":True,"start_dt":False,"end_dt":False},
        labels={"label":"","status":"Status"},
        height=580,
    )
    fig_g.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False,                        # pills above the chart already show this
        margin=dict(l=0, r=20, t=28, b=55),     # extra bottom room for legend row
        xaxis=dict(showgrid=True, gridcolor="#F0F0F0",
                   tickformat="%b '%y", dtick="M3",
                   tickfont=dict(size=10, color="#6B7280")),
        yaxis=dict(tickfont=dict(size=10.5)),
        font=dict(family="Inter"),
    )
    # RBC fiscal-quarter divider lines only — no annotations at the top
    for yr in [2023, 2024, 2025, 2026, 2027]:
        for m in [2, 5, 8, 11]:               # Feb=Q2, May=Q3, Aug=Q4, Nov=Q1
            fig_g.add_vline(
                x=f"{yr}-{m:02d}-01", line_dash="dot",
                line_color="#D1D5DB", line_width=1,
            )
    st.plotly_chart(fig_g, use_container_width=True)

    # Status legend + FY key — one clean bar below the chart
    status_chips = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:.3rem;margin-right:.9rem">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{c};flex-shrink:0"></span>'
        f'<span>{s}</span></span>'
        for s, c in STATUS_CLR.items()
    )
    st.markdown(
        f'<div style="background:white;border-radius:10px;padding:.6rem 1.2rem;'
        f'box-shadow:0 1px 5px rgba(0,0,0,.06);font-size:.8rem;color:#6B7280;'
        f'display:flex;align-items:center;gap:0;margin-top:.4rem;flex-wrap:wrap;'
        f'justify-content:space-between">'
        f'<span style="display:flex;align-items:center;flex-wrap:wrap">{status_chips}</span>'
        f'<span style="display:flex;align-items:center;gap:.7rem;flex-wrap:wrap">'
        f'&#128197;&nbsp;<strong style="color:#003168">RBC FY&nbsp;Nov&ndash;Oct</strong>'
        f'&nbsp;&nbsp;'
        f'<span><strong style="color:#003168">Q1</strong>&nbsp;Nov&ndash;Jan</span>'
        f'<span><strong style="color:#003168">Q2</strong>&nbsp;Feb&ndash;Apr</span>'
        f'<span><strong style="color:#003168">Q3</strong>&nbsp;May&ndash;Jul</span>'
        f'<span><strong style="color:#003168">Q4</strong>&nbsp;Aug&ndash;Oct</span>'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    STAGE_META = [
        ("Discovery",      "#94A3B8", "Early intake"),
        ("Build",          "#3B82F6", "In development"),
        ("Pilot",          "#8B5CF6", "Limited rollout"),
        ("Pilot to Scale", "#F59E0B", "Expanding"),
        ("Scale",          "#22C55E", "Live at scale"),
    ]
    stage_counts = INITIATIVES.groupby("stage")["id"].count().to_dict()

    nodes_html = ""
    for i, (stage, color, sub) in enumerate(STAGE_META):
        n = stage_counts.get(stage, 0)
        label = f"{n}" if n else "0"
        noun = "initiative" if n == 1 else "initiatives"
        nodes_html += f"""
        <div class="stage-node">
          <div class="stage-dot" style="background:{color}">{label}</div>
          <div class="stage-label">{stage}</div>
          <div class="stage-sub">{n} {noun}</div>
        </div>"""
        if i < len(STAGE_META) - 1:
            nc = STAGE_META[i + 1][1]
            nodes_html += (
                f'<div class="stage-line" '
                f'style="background:linear-gradient(90deg,{color},{nc})"></div>'
            )
    st.markdown(f'<div class="stage-stepper">{nodes_html}</div>',
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3  INITIATIVE PORTFOLIO
# ─────────────────────────────────────────────────────────────────────────────
with tabs[2]:
    col_f1, col_f2, col_f3 = st.columns([1.3, 1.3, 1])
    with col_f1:
        sel_lob    = st.multiselect("Line of Business", INITIATIVES.lob.unique(), placeholder="All LOBs")
    with col_f2:
        sel_status = st.multiselect("Status", INITIATIVES.status.unique(), placeholder="All Statuses")
    with col_f3:
        min_impact = st.slider("Min Impact ($M)", 25, 85, 25, step=5)

    filtered = INITIATIVES.copy()
    if sel_lob:    filtered = filtered[filtered.lob.isin(sel_lob)]
    if sel_status: filtered = filtered[filtered.status.isin(sel_status)]
    filtered = filtered[filtered.impact_m >= min_impact].sort_values("impact_m", ascending=False)

    st.markdown(f"**{len(filtered)} initiatives** &nbsp;·&nbsp; Total: **${filtered.impact_m.sum()}M**",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    rows = filtered.iterrows()
    try:
        while True:
            _, r1 = next(rows)
            with col_a:
                initiative_card(r1)
            _, r2 = next(rows)
            with col_b:
                initiative_card(r2)
    except StopIteration:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4  STRATEGIC ALIGNMENT
# ─────────────────────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-title">ADT Portfolio — RBC Strategic Pillars</div>', unsafe_allow_html=True)

    icons = {"Client First":"🤝","Do What's Right":"🛡️","Growth Mindset":"🚀","Operational Excellence":"⚙️"}
    p_cols = st.columns(4)
    for i, row in PILLARS.iterrows():
        with p_cols[i]:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{row.color}; min-height:130px">
              <div class="kpi-label">{icons.get(row.pillar,"")} {row.pillar}</div>
              <div class="kpi-value" style="font-size:1.55rem">${row.value_m}M</div>
              <div class="kpi-delta" style="color:{RBC_MUTED}">{row.initiatives} initiatives</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cl, cr = st.columns([1, 1.15])

    with cl:
        st.markdown('<div class="section-title">Value by Strategic Pillar</div>', unsafe_allow_html=True)
        fig_p = px.bar(PILLARS, x="pillar", y="value_m", text="value_m",
                       color="pillar",
                       color_discrete_map={r.pillar: r.color for _, r in PILLARS.iterrows()},
                       labels={"value_m":"$M","pillar":""}, height=300)
        fig_p.update_traces(texttemplate="$%{text}M", textposition="outside")
        fig_p.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(l=0,r=0,t=10,b=10), xaxis_tickangle=-12,
                            yaxis=dict(showgrid=True, gridcolor="#F0F0F0"))
        st.plotly_chart(fig_p, use_container_width=True)

    with cr:
        st.markdown('<div class="section-title">Initiative × Pillar Bubble Map</div>', unsafe_allow_html=True)
        map_df = INITIATIVES[["name","pillar","impact_m","status"]].copy()
        map_df["short"] = map_df["name"].str[:30] + "..."
        fig_s = px.scatter(map_df, x="pillar", y="short",
                           size="impact_m", color="status",
                           color_discrete_map=STATUS_CLR,
                           size_max=30, height=390,
                           labels={"short":"","pillar":"Strategic Pillar","impact_m":"Impact $M"})
        fig_s.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(l=0,r=0,t=10,b=10),
                            legend=dict(orientation="h", y=1.05),
                            xaxis_tickangle=-10,
                            yaxis=dict(tickfont=dict(size=9.5)),
                            xaxis=dict(tickfont=dict(size=10.5)))
        st.plotly_chart(fig_s, use_container_width=True)

    st.markdown('<div class="section-title">ADT Prioritization Criteria</div>', unsafe_allow_html=True)
    crit_cols = st.columns(3)
    criteria = [
        ("&#128176;", "Financial Impact >= $25M",
         "Hard threshold. Evaluated across cost savings, revenue uplift, risk avoidance, and productivity gains."),
        ("&#9851;",   "Reusability & Platform Scale",
         "Solutions scored on cross-LOB applicability. Platform-grade assets prioritized over point solutions."),
        ("&#129517;", "Strategic Pillar Fit",
         "Alignment to ADT program pillars and RBC 3-year enterprise strategy weighted in intake scoring."),
        ("&#9889;",   "Time-to-Value",
         "Preference for MVP within 12 months. Phased delivery over multi-year waterfall."),
        ("&#128279;", "Dependency & Risk Profile",
         "Sequencing factored against platform readiness, data availability, and regulatory constraints."),
        ("&#128101;", "Client & Advisor Impact",
         "NPS, adoption rate, and experience improvement tracked alongside financial metrics."),
    ]
    for i, (icon, title, desc) in enumerate(criteria):
        with crit_cols[i % 3]:
            st.markdown(f"""
            <div class="init-card" style="border-left-color:{RBC_GOLD}">
              <div class="init-title">{icon} {title}</div>
              <div class="init-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5  PRODUCT ROADMAP  (this platform's own evolution)
# ─────────────────────────────────────────────────────────────────────────────
with tabs[4]:
    # Step bar
    step_html = '<div class="rm-stepper">'
    for p in PHASES:
        live_tag = ' &#9679; LIVE' if p["live"] else ""
        step_html += f"""
        <div class="rm-step" style="border-top:4px solid {p['color']}">
          <div class="rm-step-label" style="color:{p['color']}">{p['label']}{live_tag}</div>
          <div class="rm-step-title">{p['phase']}</div>
          <div class="rm-step-period">{p['period']}</div>
        </div>"""
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Platform Capability Roadmap</div>', unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size:.85rem;color:#6B7280;margin-bottom:1.2rem'>"
        "This platform evolves alongside the ADT program &mdash; from a portfolio dashboard today "
        "to a fully connected, AI-powered intelligence layer for the RBC AI Group."
        "</p>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        phase_card(PHASES[0])
        st.markdown("<br>", unsafe_allow_html=True)
        phase_card(PHASES[2])
    with col2:
        phase_card(PHASES[1])
        st.markdown("<br>", unsafe_allow_html=True)
        phase_card(PHASES[3])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">North Star Vision</div>', unsafe_allow_html=True)

    ns_cols = st.columns(3)
    ns_items = [
        ("&#127775;", RBC_BLUE,  "Single Source of Truth",
         "One platform that gives the RBC AI Group and senior leadership real-time visibility "
         "into every ADT initiative — status, value, risk, and strategic fit."),
        ("&#129504;", "#A855F7", "AI-Augmented Decisions",
         "From manual slide decks to natural language queries. Directors and VPs ask questions; "
         "the platform answers with data, not PowerPoints."),
        ("&#128279;", "#3B82F6", "Enterprise-Connected",
         "Seamlessly integrated with JIRA, Finance, SharePoint, and LOB systems — "
         "so the portfolio always reflects ground truth, not last week's spreadsheet."),
    ]
    for i, (icon, color, title, desc) in enumerate(ns_items):
        with ns_cols[i]:
            st.markdown(f"""
            <div class="phase-card" style="border-top-color:{color}; text-align:center; padding:1.6rem 1.2rem">
              <div style="font-size:2rem;margin-bottom:.6rem">{icon}</div>
              <div class="phase-title" style="color:{color}">{title}</div>
              <div class="phase-period" style="margin-bottom:0;font-size:.83rem;color:#374151;line-height:1.55">
                {desc}
              </div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6  MARKET INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown(
        '<div class="disclaimer">&#8505; Illustrative estimates based on publicly available information, '
        'earnings disclosures, analyst reports, and industry research. '
        'Not reflective of internal competitive data.</div>',
        unsafe_allow_html=True,
    )

    # Radar chart
    dims = ["AI Maturity", "Digital Investment", "Client Experience", "Innovation Speed", "Platform Reusability"]
    dim_keys = ["ai_maturity", "digital", "cx", "innovation", "reusability"]

    fig_r = go.Figure()
    for c in COMPETITORS:
        vals = [c[k] for k in dim_keys] + [c[dim_keys[0]]]
        cats = dims + [dims[0]]
        fig_r.add_trace(go.Scatterpolar(
            r=vals, theta=cats, fill="toself",
            name=c["bank"],
            line=dict(color=c["color"], width=3 if c["highlight"] else 1.5),
            fillcolor=hex_rgba(c["color"], 0.22 if c["highlight"] else 0.07),
            opacity=1 if c["highlight"] else 0.7,
        ))

    fig_r.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,5], tickfont=dict(size=9),
                            gridcolor="#E5E7EB"),
            angularaxis=dict(tickfont=dict(size=11, color=RBC_TEXT)),
            bgcolor="white",
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=.5, xanchor="center",
                    font=dict(size=11)),
        margin=dict(l=50,r=50,t=30,b=60),
        height=420,
        paper_bgcolor="white",
        font=dict(family="Inter"),
    )

    st.markdown('<div class="section-title">Digital & AI Competitive Radar — Big 5 + JPMorgan</div>',
                unsafe_allow_html=True)
    st.plotly_chart(fig_r, use_container_width=True)

    # Tech spend bar
    st.markdown('<div class="section-title">Annual Technology Investment Comparison</div>',
                unsafe_allow_html=True)
    spend_df = pd.DataFrame([
        {"bank": c["bank"], "spend": float(c["tech_spend"].replace("~$","").replace("B annual",""))}
        for c in COMPETITORS
    ]).sort_values("spend")
    fig_sp = px.bar(spend_df, x="spend", y="bank", orientation="h",
                    text="spend",
                    color="bank",
                    color_discrete_map={c["bank"]: c["color"] for c in COMPETITORS},
                    labels={"spend":"Annual Tech Spend ($B)","bank":""},
                    height=280)
    fig_sp.update_traces(texttemplate="$%{text}B", textposition="outside")
    fig_sp.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                         margin=dict(l=0,r=40,t=10,b=10),
                         xaxis=dict(showgrid=True, gridcolor="#F0F0F0"),
                         yaxis=dict(tickfont=dict(size=11)))
    st.plotly_chart(fig_sp, use_container_width=True)

    # Competitor cards
    st.markdown('<div class="section-title">Key Competitor AI Programs</div>',
                unsafe_allow_html=True)
    col_cards = st.columns(3)
    for i, c in enumerate(COMPETITORS):
        with col_cards[i % 3]:
            comp_card(c)
            st.markdown("<br>", unsafe_allow_html=True)

    # Fintech disruptors note
    st.markdown('<div class="section-title">Fintech & Disruptor Landscape</div>',
                unsafe_allow_html=True)
    disruptors = [
        ("Wealthsimple",  "#FF6B35", "Canada's leading digital wealth platform — 4M+ users. "
         "Frictionless UX raises the bar for client experience that RBC's ADT initiatives must match or exceed."),
        ("Mogo",          "#7B2D8B", "Digital financial platform targeting underserved segments. "
         "AI-powered credit and identity products challenging traditional credit decisioning timelines."),
        ("Clearco",       "#1A73E8", "AI-driven SMB revenue-based financing — disrupting traditional "
         "commercial credit with instant underwriting and sub-24h funding decisions."),
        ("Nuvei / Stripe","#635BFF", "Next-gen payment infrastructure. Speed and API-first design "
         "pressuring banks to accelerate digital payment modernization."),
        ("Cohere / OpenAI","#10B981","Foundation model providers enabling any competitor to build "
         "enterprise AI rapidly. RBC's reusable ADT platform strategy is the right defence."),
        ("Plaid / Flinks", "#F59E0B","Open banking data aggregators. Accelerating the move to open "
         "banking — creating both threats and partnership opportunities for RBC's ADT data layer."),
    ]
    dis_cols = st.columns(3)
    for i, (name, color, desc) in enumerate(disruptors):
        with dis_cols[i % 3]:
            st.markdown(f"""
            <div class="comp-card" style="border-left-color:{color}; margin-bottom:.8rem">
              <div class="comp-name" style="color:{color}">{name}</div>
              <div class="comp-item">{desc}</div>
            </div>""", unsafe_allow_html=True)

# ── Footer (appears on every tab) ─────────────────────────────────────────────
st.markdown("""
<div class="custom-footer">
  Made with <span class="heart">&#10084;&#65039;</span> by <strong>Mahesh Kumar</strong>
  &nbsp;&middot;&nbsp; RBC ADT Product Strategy Prototype &nbsp;&middot;&nbsp; 2026
</div>
""", unsafe_allow_html=True)
