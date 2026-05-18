# dashboard.py
# SwiftShip — Futuristic AI Logistics Command Center

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import copy
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from order      import Order
from dataset    import generate_orders, SAMPLE_8
from merge_sort import merge_sort, benchmark
from scheduler  import fcfs, sjf, hybrid_scheduler, station_breakdown
from report     import compute_metrics

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SwiftShip · AI Logistics OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
def inject_css(dark_mode: bool):
    if dark_mode:
        bg       = "#050a14"
        surface  = "rgba(10,20,40,0.7)"
        surface2 = "rgba(15,30,55,0.6)"
        border   = "rgba(0,220,255,0.18)"
        text     = "#e8f4ff"
        muted    = "#6b8cad"
        accent   = "#00dcff"
        accent2  = "#7f5af0"
        accent3  = "#2cb67d"
        warn     = "#ff6b6b"
        glow     = "0 0 30px rgba(0,220,255,0.25)"
        card_bg  = "rgba(8,18,35,0.85)"
    else:
        bg       = "#f0f4ff"
        surface  = "rgba(255,255,255,0.75)"
        surface2 = "rgba(240,245,255,0.8)"
        border   = "rgba(100,160,255,0.25)"
        text     = "#0d1b2e"
        muted    = "#5a7fa8"
        accent   = "#0066cc"
        accent2  = "#6030d0"
        accent3  = "#1a8f5a"
        warn     = "#cc3333"
        glow     = "0 4px 24px rgba(0,100,255,0.15)"
        card_bg  = "rgba(255,255,255,0.9)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600&display=swap');

    :root {{
        --bg:      {bg};
        --surface: {surface};
        --surface2:{surface2};
        --border:  {border};
        --text:    {text};
        --muted:   {muted};
        --accent:  {accent};
        --accent2: {accent2};
        --accent3: {accent3};
        --warn:    {warn};
        --glow:    {glow};
        --card-bg: {card_bg};
        --radius:  14px;
        --font-display: 'Orbitron', monospace;
        --font-body:    'Rajdhani', sans-serif;
        --font-mono:    'JetBrains Mono', monospace;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: var(--font-body) !important;
    }}
    [data-testid="stAppViewContainer"] {{ background: var(--bg) !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; backdrop-filter: blur(20px); }}
    section[data-testid="stSidebar"] {{
        background: var(--surface) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid var(--border) !important;
    }}
    section[data-testid="stSidebar"] > div {{ background: transparent !important; }}
    .block-container {{ padding: 1.5rem 2rem 3rem !important; max-width: 1600px !important; }}

    ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: var(--accent); border-radius: 2px; }}

    .hero-container {{
        position: relative;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg,
            rgba(0,80,160,0.18) 0%,
            rgba(80,0,200,0.15) 50%,
            rgba(0,200,180,0.12) 100%);
        border: 1px solid var(--border);
        backdrop-filter: blur(30px);
        overflow: hidden;
    }}
    .hero-container::before {{
        content: '';
        position: absolute;
        top: -50%; left: -20%;
        width: 60%; height: 200%;
        background: conic-gradient(from 180deg,
            transparent 60%,
            rgba(0,220,255,0.06) 70%,
            transparent 80%);
        animation: sweep 8s linear infinite;
    }}
    @keyframes sweep {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    .hero-title {{
        font-family: var(--font-display) !important;
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 900;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 60%, var(--accent3) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.05em;
        margin: 0;
        line-height: 1.1;
    }}
    .hero-sub {{
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--muted);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 0.5rem;
    }}
    .status-dot {{
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: var(--accent3);
        box-shadow: 0 0 10px var(--accent3);
        animation: pulse 2s ease-in-out infinite;
        margin-right: 6px;
    }}
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%       {{ opacity: 0.5; transform: scale(1.4); }}
    }}

    .metric-card {{
        background: var(--card-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        cursor: default;
        margin-bottom: 0.5rem;
    }}
    .metric-card:hover {{ transform: translateY(-4px); box-shadow: var(--glow); }}
    .metric-card::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent), var(--accent2));
    }}
    .metric-label {{
        font-family: var(--font-mono);
        font-size: 0.68rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 0.4rem;
    }}
    .metric-value {{
        font-family: var(--font-display);
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--accent);
        line-height: 1;
    }}
    .metric-value.green  {{ color: var(--accent3); }}
    .metric-value.purple {{ color: var(--accent2); }}
    .metric-value.warn   {{ color: var(--warn); }}
    .metric-delta {{
        font-family: var(--font-mono);
        font-size: 0.72rem;
        color: var(--accent3);
        margin-top: 0.3rem;
    }}
    .metric-icon {{ position: absolute; top: 1rem; right: 1rem; font-size: 1.4rem; opacity: 0.25; }}

    .section-header {{
        font-family: var(--font-display);
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: var(--accent);
        border-left: 3px solid var(--accent);
        padding-left: 0.8rem;
        margin: 2rem 0 1rem;
    }}

    .glass-panel {{
        background: var(--surface);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}

    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .badge-express  {{ background: rgba(255,107,107,0.15); color: #ff6b6b; border: 1px solid rgba(255,107,107,0.3); }}
    .badge-standard {{ background: rgba(44,182,125,0.12); color: #2cb67d; border: 1px solid rgba(44,182,125,0.25); }}
    .badge-fcfs     {{ background: rgba(0,220,255,0.12); color: var(--accent); border: 1px solid rgba(0,220,255,0.25); }}
    .badge-sjf      {{ background: rgba(127,90,240,0.12); color: var(--accent2); border: 1px solid rgba(127,90,240,0.25); }}
    .badge-hybrid   {{ background: rgba(44,182,125,0.12); color: var(--accent3); border: 1px solid rgba(44,182,125,0.25); }}

    .insight-card {{
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        border-left: 3px solid var(--accent2);
        font-family: var(--font-body);
        font-size: 1rem;
        color: var(--text);
    }}
    .insight-card.green {{ border-left-color: var(--accent3); }}
    .insight-card.warn  {{ border-left-color: var(--warn); }}
    .insight-icon {{ margin-right: 0.5rem; }}

    .sidebar-brand {{
        font-family: var(--font-display);
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--accent);
        letter-spacing: 0.1em;
        padding: 0.5rem 0 1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.2rem;
    }}

    .breakdown-alert {{
        background: rgba(255,107,107,0.08);
        border: 1px solid rgba(255,107,107,0.35);
        border-radius: var(--radius);
        padding: 1rem 1.4rem;
        margin: 1rem 0;
        animation: alertPulse 2s ease-in-out infinite;
    }}
    @keyframes alertPulse {{
        0%, 100% {{ box-shadow: 0 0 0 rgba(255,107,107,0); }}
        50%       {{ box-shadow: 0 0 20px rgba(255,107,107,0.2); }}
    }}
    .breakdown-title {{
        font-family: var(--font-display);
        font-size: 0.85rem;
        color: var(--warn);
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }}

    .future-card {{
        background: var(--surface2);
        border: 1px dashed var(--border);
        border-radius: var(--radius);
        padding: 1.2rem;
        text-align: center;
        opacity: 0.65;
        transition: opacity 0.2s;
        margin-bottom: 0.5rem;
    }}
    .future-card:hover {{ opacity: 0.9; }}
    .future-title {{ font-family: var(--font-display); font-size: 0.75rem; color: var(--accent2); letter-spacing: 0.1em; margin-bottom: 0.3rem; }}
    .future-desc  {{ font-size: 0.82rem; color: var(--muted); font-family: var(--font-mono); }}
    .future-tag   {{
        display: inline-block; margin-top: 0.5rem; padding: 2px 8px;
        background: rgba(127,90,240,0.1); border: 1px solid rgba(127,90,240,0.2);
        border-radius: 20px; font-size: 0.65rem; color: var(--accent2); font-family: var(--font-mono);
    }}

    .stSlider > div > div > div > div {{ background: var(--accent) !important; }}
    div[data-testid="stSelectbox"] > div > div {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 8px !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-family: var(--font-display) !important; font-size: 0.8rem !important;
        letter-spacing: 0.12em !important; padding: 0.6rem 1.5rem !important;
        width: 100% !important; cursor: pointer !important;
        transition: opacity 0.2s, transform 0.15s !important; text-transform: uppercase !important;
    }}
    .stButton > button:hover {{ opacity: 0.88 !important; transform: translateY(-1px) !important; }}
    div[data-testid="stTabs"] button {{
        font-family: var(--font-display) !important; font-size: 0.72rem !important; letter-spacing: 0.1em !important; color: var(--muted) !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important;
    }}
    .stDataFrame {{ border-radius: var(--radius) !important; }}
    label, .stRadio label, .stCheckbox label {{ font-family: var(--font-body) !important; color: var(--text) !important; }}
    div[data-testid="stExpander"] {{
        background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  PLOTLY THEME
# ═══════════════════════════════════════════════════════════════
def plotly_theme(dark: bool) -> dict:
    if dark:
        return dict(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,10,20,0.5)",
            font_color="#e8f4ff", gridcolor="rgba(0,220,255,0.08)",
            accent="#00dcff", accent2="#7f5af0", accent3="#2cb67d", warn="#ff6b6b"
        )
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(240,245,255,0.4)",
        font_color="#0d1b2e", gridcolor="rgba(0,80,160,0.08)",
        accent="#0066cc", accent2="#6030d0", accent3="#1a8f5a", warn="#cc3333"
    )


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def stations_to_df(stations):
    rows = []
    for s in stations:
        for o in s.orders:
            wt = o.waiting_time()
            tt = o.turnaround_time()
            rows.append({
                "order_id"    : o.order_id,
                "station"     : f"Station {s.station_id}",
                "station_id"  : s.station_id,
                "type"        : o.delivery_type,
                "weight"      : o.weight,
                "burst_time"  : o.burst_time,
                "arrival_time": o.arrival_time,
                "start_time"  : o.start_time   if o.start_time  is not None else 0,
                "finish_time" : o.finish_time  if o.finish_time is not None else 0,
                "waiting_time": wt             if wt            is not None else 0,
                "turnaround"  : tt             if tt            is not None else 0,
                "is_active"   : s.is_active,
            })
    return pd.DataFrame(rows)


def metric_card(label, value, color="", delta="", icon=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        {'<div class="metric-delta">'+delta+'</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def insight_card(text, variant="", icon="▸"):
    st.markdown(f"""
    <div class="insight-card {variant}">
        <span class="insight-icon">{icon}</span>{text}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  GANTT CHART
# ═══════════════════════════════════════════════════════════════
def render_gantt(stations, title, theme):
    df = stations_to_df(stations)
    if df.empty:
        st.warning("No data to display.")
        return

    colors = {
        ("express",  True ): theme["accent"],
        ("express",  False): theme["warn"],
        ("standard", True ): theme["accent3"],
        ("standard", False): "#888",
    }

    fig = go.Figure()
    for _, row in df.iterrows():
        color    = colors.get((row["type"], row["is_active"]), "#888")
        duration = max(row["finish_time"] - row["start_time"], 0.1)
        fig.add_trace(go.Bar(
            x=[duration],
            y=[row["station"]],
            base=[row["start_time"]],
            orientation="h",
            marker=dict(color=color, opacity=0.82, line=dict(color="rgba(255,255,255,0.15)", width=1)),
            name=row["order_id"],
            showlegend=False,
            hovertemplate=(
                f"<b>{row['order_id']}</b><br>"
                f"Type: {row['type'].upper()}<br>"
                f"Start: t={row['start_time']:.1f}min<br>"
                f"End: t={row['finish_time']:.1f}min<br>"
                f"Wait: {row['waiting_time']:.1f}min<br>"
                f"Turnaround: {row['turnaround']:.1f}min"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=title, font=dict(family="Orbitron", size=13, color=theme["accent"])),
        barmode="overlay",
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        xaxis=dict(title="Time (minutes)", gridcolor=theme["gridcolor"], zeroline=False),
        yaxis=dict(title="", gridcolor=theme["gridcolor"]),
        height=max(200, len(df["station"].unique()) * 60 + 100),
        margin=dict(l=10, r=10, t=40, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  RADAR CHART
# ═══════════════════════════════════════════════════════════════
def render_radar(metrics_dict, theme):
    algos  = list(metrics_dict.keys())
    cats   = ["Throughput", "Low Wait", "Low Turnaround", "Express Speed", "Efficiency"]
    colors = [theme["accent"], theme["accent2"], theme["accent3"]]

    def normalize(val, lo, hi, invert=False):
        if hi == lo:
            return 50
        n = (val - lo) / (hi - lo) * 100
        return 100 - n if invert else n

    wait_vals = [metrics_dict[a]["avg_waiting"]    for a in algos]
    turn_vals = [metrics_dict[a]["avg_turnaround"] for a in algos]
    expr_vals = [metrics_dict[a].get("first_express_out") or 999 for a in algos]
    thru_vals = [metrics_dict[a]["throughput"]     for a in algos]
    make_vals = [metrics_dict[a]["makespan"]       for a in algos]

    fig = go.Figure()
    for i, algo in enumerate(algos):
        scores = [
            normalize(thru_vals[i], min(thru_vals), max(thru_vals)),
            normalize(wait_vals[i], min(wait_vals), max(wait_vals), invert=True),
            normalize(turn_vals[i], min(turn_vals), max(turn_vals), invert=True),
            normalize(expr_vals[i], min(expr_vals), max(expr_vals), invert=True),
            normalize(make_vals[i], min(make_vals), max(make_vals), invert=True),
        ]
        fig.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=cats + [cats[0]],
            fill="toself",
            name=algo,
            line=dict(color=colors[i % len(colors)], width=2),
            opacity=0.85,
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=theme["plot_bgcolor"],
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=theme["gridcolor"],
                            tickfont=dict(size=8, color=theme["font_color"])),
            angularaxis=dict(gridcolor=theme["gridcolor"],
                             tickfont=dict(size=9, color=theme["font_color"])),
        ),
        paper_bgcolor=theme["paper_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        legend=dict(font=dict(family="Orbitron", size=9)),
        title=dict(text="Algorithm Performance Radar", font=dict(family="Orbitron", size=12, color=theme["accent"])),
        height=360,
        margin=dict(l=40, r=40, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  HEATMAP
# ═══════════════════════════════════════════════════════════════
def render_heatmap(metrics_dict, theme):
    algos       = list(metrics_dict.keys())
    station_ids = sorted(set(
        sid for a in algos for sid in metrics_dict[a]["station_loads"]
    ))

    if not station_ids:
        st.info("No station load data available.")
        return

    z = [[metrics_dict[a]["station_loads"].get(sid, 0) for sid in station_ids] for a in algos]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"Station {s}" for s in station_ids],
        y=algos,
        colorscale="Turbo",
        hovertemplate="Algorithm: %{y}<br>%{x}: %{z:.1f} min load<extra></extra>",
        showscale=True,
    ))
    fig.update_layout(
        title=dict(text="Station Load Heatmap (minutes)", font=dict(family="Orbitron", size=12, color=theme["accent"])),
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        height=280,
        margin=dict(l=10, r=10, t=45, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  COMPARISON BARS
# ═══════════════════════════════════════════════════════════════
def render_comparison_bars(metrics_dict, theme):
    algos = list(metrics_dict.keys())
    cols  = [theme["accent"], theme["accent2"], theme["accent3"]]

    fig = make_subplots(rows=1, cols=3,
                        subplot_titles=["Avg Waiting Time (min)", "Avg Turnaround (min)", "Throughput (orders/hr)"])

    for col_i, (key, higher_is_better) in enumerate(
        [("avg_waiting", False), ("avg_turnaround", False), ("throughput", True)], start=1
    ):
        vals = [metrics_dict[a][key] for a in algos]
        best = max(vals) if higher_is_better else min(vals)
        bar_colors = [theme["accent3"] if v == best else cols[i % len(cols)] for i, v in enumerate(vals)]
        fig.add_trace(
            go.Bar(x=algos, y=vals, marker_color=bar_colors,
                   text=[f"{v:.1f}" for v in vals], textposition="outside",
                   textfont=dict(family="Orbitron", size=9),
                   showlegend=False,
                   hovertemplate="%{x}: %{y:.2f}<extra></extra>"),
            row=1, col=col_i
        )

    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        height=300,
        margin=dict(l=10, r=10, t=50, b=20),
    )
    fig.update_xaxes(gridcolor=theme["gridcolor"], showgrid=False)
    fig.update_yaxes(gridcolor=theme["gridcolor"])
    for annotation in fig.layout.annotations:
        annotation.font.family = "Orbitron"
        annotation.font.size   = 10
        annotation.font.color  = theme["accent"]
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  WORKLOAD DISTRIBUTION
# ═══════════════════════════════════════════════════════════════
def render_workload_distribution(df_all, theme):
    if df_all.empty:
        return
    fig = px.box(
        df_all, x="algorithm", y="turnaround", color="type",
        color_discrete_map={"express": theme["accent"], "standard": theme["accent3"]},
        labels={"algorithm": "Algorithm", "turnaround": "Turnaround (min)", "type": "Type"},
        title="Turnaround Distribution by Algorithm & Delivery Type",
    )
    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        title_font=dict(family="Orbitron", size=12, color=theme["accent"]),
        height=320, margin=dict(l=10, r=10, t=50, b=20),
    )
    fig.update_xaxes(gridcolor=theme["gridcolor"])
    fig.update_yaxes(gridcolor=theme["gridcolor"])
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  ORDER FLOW SCATTER
# ═══════════════════════════════════════════════════════════════
def render_order_flow(df_all, algo, theme):
    df = df_all[df_all["algorithm"] == algo].copy()
    if df.empty:
        st.info("No data for selected algorithm.")
        return
    fig = px.scatter(
        df, x="arrival_time", y="finish_time",
        color="type", size="weight",
        color_discrete_map={"express": theme["accent"], "standard": theme["accent3"]},
        hover_data=["order_id", "waiting_time", "turnaround"],
        labels={"arrival_time": "Arrival Time (min)", "finish_time": "Finish Time (min)"},
        title=f"Order Flow Map — {algo}",
    )
    mx = df["finish_time"].max()
    fig.add_trace(go.Scatter(
        x=[0, mx], y=[0, mx], mode="lines",
        line=dict(color=theme["warn"], dash="dot", width=1),
        name="Ideal (no wait)", showlegend=True,
    ))
    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
        font=dict(color=theme["font_color"], family="Rajdhani"),
        title_font=dict(family="Orbitron", size=12, color=theme["accent"]),
        height=340, margin=dict(l=10, r=10, t=50, b=20),
    )
    fig.update_xaxes(gridcolor=theme["gridcolor"])
    fig.update_yaxes(gridcolor=theme["gridcolor"])
    st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  MERGE SORT TRACE VISUALIZATION
# ═══════════════════════════════════════════════════════════════
def render_trace_visualization(orders, theme):
    steps = []

    def ms_trace(lst, depth=0):
        if len(lst) <= 1:
            return lst
        mid   = len(lst) // 2
        left  = lst[:mid]
        right = lst[mid:]
        steps.append({"depth": depth, "action": "DIVIDE",
                       "left": [o.order_id for o in left],
                       "right": [o.order_id for o in right]})
        sl     = ms_trace(left,  depth + 1)
        sr     = ms_trace(right, depth + 1)
        merged = sorted(sl + sr, key=lambda o: o.priority_key())
        steps.append({"depth": depth, "action": "MERGE",
                       "result": [o.order_id for o in merged]})
        return merged

    ms_trace(copy.deepcopy(orders))

    rows = []
    for i, s in enumerate(steps):
        if s["action"] == "DIVIDE":
            rows.append({"Step": i+1, "Action": "DIVIDE", "Depth": s["depth"],
                         "Left": str(s["left"]), "Right": str(s["right"]), "Result": ""})
        else:
            rows.append({"Step": i+1, "Action": "MERGE ", "Depth": s["depth"],
                         "Left": "", "Right": "", "Result": str(s["result"])})
    df = pd.DataFrame(rows)

    action_colors = df["Action"].map({"DIVIDE": theme["accent2"], "MERGE ": theme["accent3"]}).tolist()

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Step", "Action", "Depth", "Left Partition", "Right Partition", "Merged Result"],
            font=dict(family="Orbitron", size=10, color="#fff"),
            fill_color=theme["accent"],
            align="center", height=32,
        ),
        cells=dict(
            values=[df[c] for c in df.columns],
            font=dict(family="JetBrains Mono", size=9, color=theme["font_color"]),
            fill_color=[
                [theme["plot_bgcolor"]] * len(df),
                action_colors,
                [theme["plot_bgcolor"]] * len(df),
                [theme["plot_bgcolor"]] * len(df),
                [theme["plot_bgcolor"]] * len(df),
                [theme["plot_bgcolor"]] * len(df),
            ],
            align="center", height=26,
        ),
    )])
    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"],
        font=dict(color=theme["font_color"]),
        title=dict(text="Merge Sort — Step-by-Step Trace", font=dict(family="Orbitron", size=12, color=theme["accent"])),
        height=420, margin=dict(l=0, r=0, t=45, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    divide_df = df[df["Action"] == "DIVIDE"]
    if not divide_df.empty:
        fig2 = px.histogram(divide_df, x="Depth", nbins=8,
                            color_discrete_sequence=[theme["accent2"]],
                            title="Divide Operations by Recursion Depth")
        fig2.update_layout(
            paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
            font=dict(color=theme["font_color"], family="Rajdhani"),
            title_font=dict(family="Orbitron", size=11, color=theme["accent"]),
            height=240, margin=dict(l=10, r=10, t=45, b=20),
        )
        fig2.update_xaxes(gridcolor=theme["gridcolor"])
        fig2.update_yaxes(gridcolor=theme["gridcolor"])
        st.plotly_chart(fig2, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
#  BREAKDOWN VISUALIZATION
# ═══════════════════════════════════════════════════════════════
def render_breakdown(bd_stations, rescued_orders, fail_station, fail_at, theme):
    df = stations_to_df(bd_stations)
    if df.empty:
        st.warning("No breakdown data to display.")
        return

    st.markdown(f"""
    <div class="breakdown-alert">
        <div class="breakdown-title">⚠ CRITICAL SYSTEM EVENT — STATION {fail_station} FAILURE AT t={fail_at}min</div>
        <span style="font-family:var(--font-mono);font-size:0.82rem;color:var(--text)">
            {len(rescued_orders)} orders rescued · Redistributed via SJF to active stations
        </span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure()
        for _, row in df.iterrows():
            c        = theme["warn"] if not row["is_active"] else (
                       theme["accent"] if row["type"] == "express" else theme["accent3"])
            duration = max(row["finish_time"] - row["start_time"], 0.1)
            fig.add_trace(go.Bar(
                x=[duration], y=[row["station"]], base=[row["start_time"]],
                orientation="h",
                marker=dict(color=c, opacity=0.8, line=dict(color="rgba(255,255,255,0.1)", width=0.5)),
                showlegend=False,
                hovertemplate=f"<b>{row['order_id']}</b><br>t={row['start_time']:.1f}–{row['finish_time']:.1f}<br>Type: {row['type']}<extra></extra>",
            ))
        fig.add_vline(x=fail_at, line_dash="dash", line_color=theme["warn"],
                      annotation_text=f"⚡ t={fail_at} FAILURE",
                      annotation_font=dict(color=theme["warn"], family="Orbitron", size=9))
        fig.update_layout(
            barmode="overlay",
            title=dict(text="Station Timeline — Breakdown Event", font=dict(family="Orbitron", size=12, color=theme["accent"])),
            paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
            font=dict(color=theme["font_color"], family="Rajdhani"),
            height=280, margin=dict(l=10, r=10, t=45, b=20),
        )
        fig.update_xaxes(title="Time (minutes)", gridcolor=theme["gridcolor"])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        station_loads = df.groupby("station")["burst_time"].sum().reset_index()
        fig2 = px.pie(station_loads, names="station", values="burst_time",
                      color_discrete_sequence=[theme["accent"], theme["accent2"], theme["warn"]],
                      hole=0.5, title="Load Distribution After Recovery")
        fig2.update_layout(
            paper_bgcolor=theme["paper_bgcolor"],
            font=dict(color=theme["font_color"], family="Rajdhani"),
            title_font=dict(family="Orbitron", size=10, color=theme["accent"]),
            height=280, margin=dict(l=0, r=0, t=45, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    section_header("Recovery Efficiency Analysis")
    total        = len(df)
    rescued_pct  = len(rescued_orders) / total * 100 if total else 0
    active_count = sum(1 for s in bd_stations if s.is_active)

    r1, r2, r3 = st.columns(3)
    with r1: metric_card("Orders Rescued",  str(len(rescued_orders)), "warn",   "Redistributed via SJF", "🚨")
    with r2: metric_card("Recovery Rate",   f"{rescued_pct:.1f}%",    "green",  "Successfully rescheduled", "✅")
    with r3: metric_card("Active Stations", f"{active_count}/{len(bd_stations)}", "purple", f"Station {fail_station} offline", "⚙️")


# ═══════════════════════════════════════════════════════════════
#  AI INSIGHTS
# ═══════════════════════════════════════════════════════════════
def generate_insights(metrics_dict, df_all):
    insights = []
    algos = list(metrics_dict.keys())

    if not algos or df_all.empty:
        return insights

    best_wait = min(algos, key=lambda a: metrics_dict[a]["avg_waiting"])
    best_turn = min(algos, key=lambda a: metrics_dict[a]["avg_turnaround"])
    best_thru = max(algos, key=lambda a: metrics_dict[a]["throughput"])
    best_expr = min(algos, key=lambda a: metrics_dict[a].get("first_express_out") or 9999)

    insights.append(("green", f"⚡ {best_wait} achieves the lowest average waiting time "
                     f"({metrics_dict[best_wait]['avg_waiting']:.1f} min) — ideal for high-volume throughput scenarios."))
    insights.append(("",      f"🏆 {best_turn} delivers the best average turnaround "
                     f"({metrics_dict[best_turn]['avg_turnaround']:.1f} min) — recommended for SLA-critical workloads."))
    insights.append(("green", f"🚀 {best_expr} processes the first express order earliest — optimal for premium delivery tiers."))
    insights.append(("",      f"📊 {best_thru} achieves the highest throughput of {metrics_dict[best_thru]['throughput']:.1f} orders/hr."))

    for algo in algos:
        df_algo = df_all[df_all["algorithm"] == algo]
        if not df_algo.empty:
            spread = df_algo["waiting_time"].std()
            if spread > 15:
                insights.append(("warn", f"⚠ {algo} shows high waiting time variance (σ={spread:.1f} min) — "
                                 "load balancing may be suboptimal."))

    expr_rows = df_all[df_all["type"] == "express"]["turnaround"]
    std_rows  = df_all[df_all["type"] == "standard"]["turnaround"]
    if not expr_rows.empty and not std_rows.empty:
        ratio = expr_rows.mean() / std_rows.mean() if std_rows.mean() > 0 else 1
        if ratio < 0.8:
            insights.append(("green", f"✅ Express orders process {(1-ratio)*100:.0f}% faster than standard — priority scheduling is working correctly."))
        else:
            insights.append(("warn",  f"⚠ Express orders are not significantly faster than standard (ratio={ratio:.2f}) — consider tuning priority weights."))

    if "Hybrid" in metrics_dict and "FCFS" in metrics_dict:
        hybrid_wait = metrics_dict["Hybrid"]["avg_waiting"]
        fcfs_wait   = metrics_dict["FCFS"]["avg_waiting"]
        if hybrid_wait < fcfs_wait:
            insights.append(("green", f"🔀 Hybrid scheduler reduces waiting time by {fcfs_wait - hybrid_wait:.1f} min vs FCFS — parallel lane strategy is effective."))

    for algo in algos:
        loads = list(metrics_dict[algo]["station_loads"].values())
        if loads and max(loads) > 0:
            max_load = max(loads)
            min_load = min(loads)
            if min_load > 0 and max_load > 1.5 * min_load:
                bottleneck = max(metrics_dict[algo]["station_loads"], key=metrics_dict[algo]["station_loads"].get)
                insights.append(("warn", f"🔴 {algo}: Station {bottleneck} is a bottleneck ({max_load:.0f} min vs min {min_load:.0f} min) — consider rebalancing."))

    return insights


# ═══════════════════════════════════════════════════════════════
#  ORDER TABLE
# ═══════════════════════════════════════════════════════════════
def render_order_table(df_all, theme):
    if df_all.empty:
        st.info("No order data to display.")
        return

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        algo_filter = st.selectbox("Algorithm", ["All"] + list(df_all["algorithm"].unique()), key="tbl_algo")
    with c2:
        type_filter = st.selectbox("Delivery Type", ["All", "express", "standard"], key="tbl_type")
    with c3:
        search = st.text_input("Search Order ID", placeholder="e.g. ORD042", key="tbl_search")

    filtered = df_all.copy()
    if algo_filter != "All":
        filtered = filtered[filtered["algorithm"] == algo_filter]
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]
    if search:
        filtered = filtered[filtered["order_id"].str.contains(search.upper())]

    filtered = filtered.sort_values("waiting_time", ascending=False)
    display_cols = ["order_id", "algorithm", "type", "weight", "burst_time",
                    "station", "arrival_time", "start_time", "finish_time", "waiting_time", "turnaround"]
    display = filtered[display_cols].copy()
    display.columns = ["Order", "Algorithm", "Type", "Weight(kg)", "Burst(min)",
                        "Station", "Arrival", "Start", "Finish", "Wait(min)", "TAT(min)"]

    st.dataframe(display.reset_index(drop=True), use_container_width=True, height=420)
    st.markdown(f'<div style="font-family:var(--font-mono);font-size:0.75rem;color:var(--muted);margin-top:0.3rem">'
                f'Showing {len(display)} / {len(df_all)} orders</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  FUTURE FEATURES
# ═══════════════════════════════════════════════════════════════
FUTURE_FEATURES = [
    ("🤖", "RL Scheduler",       "Reinforcement learning agent that optimizes dispatching policies in real-time.", "Q3 2026"),
    ("📈", "Demand Forecasting", "LSTM-powered demand prediction 7 days ahead using historical order patterns.",   "Q3 2026"),
    ("🛰",  "Live GPS Tracking",  "Real-time vehicle telemetry overlaid on interactive city map.",                  "Q4 2026"),
    ("🧬", "Digital Twin",       "Full warehouse simulation clone for what-if scenario planning.",                 "Q4 2026"),
    ("☁️", "Cloud Deployment",   "One-click deploy to AWS/GCP with auto-scaling worker stations.",                 "2027"),
    ("🗃",  "Database Integration","PostgreSQL + TimescaleDB for persistent order history and analytics.",          "2027"),
    ("🔮", "ML Optimizer",       "Gradient-boosted model recommending optimal station count & algorithm per shift.","2027"),
    ("🌍", "Multi-Warehouse",    "Cross-warehouse coordination with inter-depot transfer routing.",                 "2027"),
]

def render_future_features():
    cols = st.columns(4)
    for i, (icon, title, desc, eta) in enumerate(FUTURE_FEATURES):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="future-card">
                <div style="font-size:1.8rem;margin-bottom:0.4rem">{icon}</div>
                <div class="future-title">{title}</div>
                <div class="future-desc">{desc}</div>
                <span class="future-tag">ETA {eta}</span>
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    if "dark_mode"   not in st.session_state: st.session_state.dark_mode   = True
    if "sim_results" not in st.session_state: st.session_state.sim_results = None

    dark = st.session_state.dark_mode
    inject_css(dark)
    theme = plotly_theme(dark)

    # ── SIDEBAR ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">⚡ SWIFTSHIP OS</div>', unsafe_allow_html=True)

        dark_toggle = st.toggle("🌙 Dark Mode", value=dark)
        if dark_toggle != dark:
            st.session_state.dark_mode = dark_toggle
            st.rerun()

        st.markdown("---")
        st.markdown('<div style="font-family:Orbitron;font-size:0.7rem;color:var(--muted);letter-spacing:0.12em;margin-bottom:0.6rem">SIMULATION PARAMETERS</div>', unsafe_allow_html=True)

        n_orders   = st.slider("Orders",   10,   500, 100, 10)
        seed       = st.number_input("Random Seed", 0, 9999, 42)
        n_stations = st.slider("Stations",  2,     6,   3)

        st.markdown("---")
        st.markdown('<div style="font-family:Orbitron;font-size:0.7rem;color:var(--muted);letter-spacing:0.12em;margin-bottom:0.6rem">ALGORITHMS</div>', unsafe_allow_html=True)

        run_fcfs   = st.checkbox("FCFS",   value=True)
        run_sjf    = st.checkbox("SJF",    value=True)
        run_hybrid = st.checkbox("Hybrid", value=True)

        st.markdown("---")
        st.markdown('<div style="font-family:Orbitron;font-size:0.7rem;color:var(--muted);letter-spacing:0.12em;margin-bottom:0.6rem">FEATURES</div>', unsafe_allow_html=True)

        trace_mode     = st.toggle("AI Trace Mode",        value=False)
        breakdown_mode = st.toggle("Breakdown Simulation", value=False)
        benchmark_mode = st.toggle("Benchmark Mode",       value=False)

        # Breakdown params only appear when enabled
        fail_station = 2
        fail_at      = 30
        if breakdown_mode:
            fail_station = st.slider("Fail Station #", 1, n_stations, min(2, n_stations))
            fail_at      = st.slider("Fail at (min)",  10, 100, 30)

        st.markdown("---")
        run_btn = st.button("▶  RUN SIMULATION")

    # ── HERO ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-container">
        <p class="hero-sub"><span class="status-dot"></span>SYSTEM ONLINE · AI LOGISTICS OPERATING SYSTEM · v2.6.0</p>
        <h1 class="hero-title">SWIFTSHIP</h1>
        <p style="font-family:Rajdhani;font-size:1.15rem;color:var(--muted);margin-top:0.6rem;max-width:600px">
            Real-time order fulfilment simulation powered by OS scheduling algorithms —
            FCFS · SJF · Hybrid · Breakdown Recovery
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── RUN SIMULATION ───────────────────────────────────────────
    if run_btn:
        if not (run_fcfs or run_sjf or run_hybrid):
            st.warning("Please select at least one algorithm to run.")
        else:
            with st.spinner("Initializing simulation engine..."):
                orders        = generate_orders(n_orders, seed=int(seed))
                sorted_orders = merge_sort(orders)

                results = {}
                if run_fcfs:
                    results["FCFS"]   = fcfs(sorted_orders, n_stations)
                if run_sjf:
                    results["SJF"]    = sjf(sorted_orders, n_stations)
                if run_hybrid:
                    results["Hybrid"] = hybrid_scheduler(sorted_orders, n_stations)

                # Breakdown returns a TUPLE (stations, rescued)
                bd_stations, rescued = None, []
                if breakdown_mode:
                    bd_stations, rescued = station_breakdown(
                        sorted_orders, fail_station, fail_at, n_stations)

                # Benchmark returns a DICT
                bench_data = None
                if benchmark_mode:
                    bench_data = benchmark(n_orders)

                # Build combined dataframe
                dfs = []
                for algo, stations in results.items():
                    df = stations_to_df(stations)
                    df["algorithm"] = algo
                    dfs.append(df)
                df_all = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

                metrics_dict = {k: compute_metrics(v) for k, v in results.items()}

                st.session_state.sim_results = {
                    "results"      : results,
                    "metrics"      : metrics_dict,
                    "df_all"       : df_all,
                    "sorted_orders": sorted_orders,
                    "bd_stations"  : bd_stations,
                    "rescued"      : rescued,
                    "bench_data"   : bench_data,
                    "params": {
                        "n_orders"      : n_orders,
                        "seed"          : seed,
                        "n_stations"    : n_stations,
                        "trace_mode"    : trace_mode,
                        "breakdown_mode": breakdown_mode,
                        "fail_station"  : fail_station,
                        "fail_at"       : fail_at,
                    },
                }

    # ── DISPLAY ──────────────────────────────────────────────────
    data = st.session_state.sim_results
    if data is None:
        st.markdown("""
        <div class="glass-panel" style="text-align:center;padding:3rem">
            <div style="font-family:Orbitron;font-size:1.1rem;color:var(--muted);letter-spacing:0.1em">
                AWAITING SIMULATION INPUT
            </div>
            <div style="font-family:JetBrains Mono;font-size:0.8rem;color:var(--muted);margin-top:0.8rem">
                Configure parameters in the sidebar and press RUN SIMULATION
            </div>
        </div>
        """, unsafe_allow_html=True)
        render_future_features()
        return

    metrics_dict  = data["metrics"]
    df_all        = data["df_all"]
    results       = data["results"]
    sorted_orders = data["sorted_orders"]
    params        = data["params"]
    bd_stations   = data["bd_stations"]
    rescued       = data["rescued"]
    bench_data    = data["bench_data"]

    # Guard: if no metrics (all algos deselected edge case)
    if not metrics_dict:
        st.warning("No simulation data. Please select at least one algorithm and re-run.")
        return

    # ── KPI CARDS ────────────────────────────────────────────────
    section_header("LIVE ANALYTICS")

    n_express  = sum(1 for o in sorted_orders if o.delivery_type == "express")
    n_standard = len(sorted_orders) - n_express

    best_algo_wait = min(metrics_dict, key=lambda a: metrics_dict[a]["avg_waiting"])
    best_thru_val  = max(metrics_dict[a]["throughput"]    for a in metrics_dict)
    min_wait_val   = min(metrics_dict[a]["avg_waiting"]   for a in metrics_dict)
    max_turn_val   = max(metrics_dict[a]["avg_turnaround"] for a in metrics_dict)
    sys_eff        = round(100 - (min_wait_val / max_turn_val * 100), 1) if max_turn_val > 0 else 0

    cols = st.columns(5)
    with cols[0]: metric_card("Total Orders",      str(len(sorted_orders)), "",       f"{n_express} express · {n_standard} standard", "📦")
    with cols[1]: metric_card("Express Orders",    str(n_express),          "purple", f"{n_express/len(sorted_orders)*100:.0f}% of load", "⚡")
    with cols[2]: metric_card("Best Avg Wait",     f"{min_wait_val:.1f}m",  "green",  f"via {best_algo_wait}", "⏱")
    with cols[3]: metric_card("Best Throughput",   f"{best_thru_val:.1f}/hr","green", "orders per hour", "📈")
    with cols[4]: metric_card("System Efficiency", f"{sys_eff:.1f}%",       "",       "scheduling quality score", "🎯")

    cols2 = st.columns(5)
    all_makespans = [metrics_dict[a]["makespan"] for a in metrics_dict]
    with cols2[0]: metric_card("Algorithms Run",    str(len(metrics_dict)),  "purple", "concurrent comparison", "🔀")
    with cols2[1]: metric_card("Stations Active",   str(params["n_stations"]),"green", "parallel processing", "🏭")
    with cols2[2]: metric_card("Fastest Algorithm", best_algo_wait,           "green", "lowest latency", "🏆")
    with cols2[3]: metric_card("Best Makespan",     f"{min(all_makespans):.0f}m","",   "total completion time", "⌛")
    with cols2[4]: metric_card("Seed / Orders",     f"{params['seed']} / {params['n_orders']}", "", "simulation config", "🎲")

    # ── TABS ─────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊  ANALYSIS",
        "📅  GANTT CHARTS",
        "🧠  AI TRACE",
        "⚠   BREAKDOWN",
        "🔬  DEEP DIVE",
        "📋  ORDER TABLE",
        "🔮  FUTURE",
    ])

    # TAB 0 — ANALYSIS
    with tabs[0]:
        section_header("ALGORITHM PERFORMANCE COMPARISON")
        render_comparison_bars(metrics_dict, theme)

        c1, c2 = st.columns(2)
        with c1: render_radar(metrics_dict, theme)
        with c2: render_heatmap(metrics_dict, theme)

        section_header("WORKLOAD DISTRIBUTION")
        render_workload_distribution(df_all, theme)

        if bench_data:
            section_header("MERGE SORT BENCHMARK")
            b1, b2, b3 = st.columns(3)
            with b1: metric_card("Merge Sort Time",    f"{bench_data['merge_sort']:.4f}s",  "",       "custom implementation", "⚙️")
            with b2: metric_card("Python sort() Time", f"{bench_data['python_sort']:.4f}s", "green",  "built-in Timsort", "🐍")
            with b3: metric_card("Ratio",              f"{bench_data['ratio']:.1f}×",        "purple", "Python sort is faster (C-optimized)", "📐")

    # TAB 1 — GANTT
    with tabs[1]:
        section_header("STATION EXECUTION TIMELINE")
        for algo, stations in results.items():
            badge_cls = algo.lower()
            st.markdown(f'<span class="badge badge-{badge_cls}">{algo}</span>', unsafe_allow_html=True)
            render_gantt(stations, f"{algo} — Station Execution Timeline", theme)
            st.markdown("<br>", unsafe_allow_html=True)

    # TAB 2 — AI TRACE
    with tabs[2]:
        section_header("MERGE SORT — RECURSIVE TRACE")
        st.markdown("""
        <div class="glass-panel">
            <div style="font-family:Orbitron;font-size:0.8rem;color:var(--accent);margin-bottom:0.6rem">How it works</div>
            <div style="font-family:Rajdhani;font-size:1rem;color:var(--text)">
                The merge sort divides orders into halves recursively until single elements remain,
                then merges them back in sorted order — <b>express first</b>, then by ascending weight.
                Time complexity: <span style="font-family:JetBrains Mono;color:var(--accent2)">O(n log n)</span>.
                Space: <span style="font-family:JetBrains Mono;color:var(--accent2)">O(n)</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        trace_sample = SAMPLE_8[:8]
        render_trace_visualization(trace_sample, theme)

        section_header("PRIORITY KEY LOGIC")
        sorted_sample = merge_sort(copy.deepcopy(trace_sample))
        key_df = pd.DataFrame([{
            "Order"              : o.order_id,
            "Type"               : o.delivery_type,
            "Weight (kg)"        : o.weight,
            "Priority Key"       : str(o.priority_key()),
            "After Sort Position": i + 1,
        } for i, o in enumerate(sorted_sample)])
        st.dataframe(key_df, use_container_width=True, hide_index=True)

    # TAB 3 — BREAKDOWN
    with tabs[3]:
        section_header("STATION BREAKDOWN RECOVERY SIMULATION")
        if bd_stations is not None:
            render_breakdown(bd_stations, rescued,
                             params["fail_station"], params["fail_at"], theme)
        else:
            st.markdown("""
            <div class="glass-panel" style="text-align:center;padding:2.5rem">
                <div style="font-size:2rem;margin-bottom:0.5rem">⚠️</div>
                <div style="font-family:Orbitron;font-size:0.85rem;color:var(--muted);letter-spacing:0.1em">BREAKDOWN SIMULATION DISABLED</div>
                <div style="font-family:JetBrains Mono;font-size:0.75rem;color:var(--muted);margin-top:0.4rem">
                    Enable "Breakdown Simulation" in the sidebar and re-run
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 4 — DEEP DIVE
    with tabs[4]:
        section_header("ORDER FLOW ANALYSIS")
        if not df_all.empty:
            flow_algo = st.selectbox("Select Algorithm for Flow Map", list(metrics_dict.keys()), key="flow_algo")
            render_order_flow(df_all, flow_algo, theme)

        section_header("AI INSIGHTS & RECOMMENDATIONS")
        insights = generate_insights(metrics_dict, df_all)
        for variant, text in insights:
            insight_card(text, variant)

        if not df_all.empty:
            section_header("LATENCY ANALYSIS — WAITING TIME DISTRIBUTION")
            fig_lat = px.violin(df_all, x="algorithm", y="waiting_time", color="type",
                                color_discrete_map={"express": theme["accent"], "standard": theme["accent3"]},
                                box=True, points="outliers",
                                labels={"waiting_time": "Waiting Time (min)", "algorithm": "Algorithm"},
                                title="Waiting Time Distribution (Violin Plot)")
            fig_lat.update_layout(
                paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
                font=dict(color=theme["font_color"], family="Rajdhani"),
                title_font=dict(family="Orbitron", size=12, color=theme["accent"]),
                height=360, margin=dict(l=10, r=10, t=50, b=20),
            )
            fig_lat.update_xaxes(gridcolor=theme["gridcolor"])
            fig_lat.update_yaxes(gridcolor=theme["gridcolor"])
            st.plotly_chart(fig_lat, use_container_width=True)

            section_header("CUMULATIVE COMPLETION CURVE")
            colors_list = [theme["accent"], theme["accent2"], theme["accent3"]]
            fig_cum = go.Figure()
            for i, algo in enumerate(metrics_dict):
                df_algo = df_all[df_all["algorithm"] == algo].sort_values("finish_time").copy()
                df_algo["cumulative"] = range(1, len(df_algo) + 1)
                fig_cum.add_trace(go.Scatter(
                    x=df_algo["finish_time"], y=df_algo["cumulative"],
                    mode="lines", name=algo,
                    line=dict(color=colors_list[i % len(colors_list)], width=2.5),
                ))
            fig_cum.update_layout(
                title=dict(text="Cumulative Orders Completed Over Time",
                           font=dict(family="Orbitron", size=12, color=theme["accent"])),
                paper_bgcolor=theme["paper_bgcolor"], plot_bgcolor=theme["plot_bgcolor"],
                font=dict(color=theme["font_color"], family="Rajdhani"),
                xaxis=dict(title="Time (min)", gridcolor=theme["gridcolor"]),
                yaxis=dict(title="Orders Completed", gridcolor=theme["gridcolor"]),
                height=320, margin=dict(l=10, r=10, t=50, b=20),
            )
            st.plotly_chart(fig_cum, use_container_width=True)

    # TAB 5 — ORDER TABLE
    with tabs[5]:
        section_header("ORDER INTELLIGENCE TABLE")
        render_order_table(df_all, theme)

    # TAB 6 — FUTURE
    with tabs[6]:
        section_header("UPCOMING FEATURES — ROADMAP 2026–2027")
        render_future_features()

        st.markdown("<br>", unsafe_allow_html=True)
        section_header("TECHNOLOGY STACK — CURRENT")
        stack_items = [
            ("🐍", "Python 3.11",    "Core runtime"),
            ("🎈", "Streamlit",      "Dashboard framework"),
            ("📊", "Plotly",         "Interactive visualizations"),
            ("🐼", "Pandas",         "Data manipulation"),
            ("🔀", "Merge Sort",     "O(n log n) priority sorting"),
            ("⚙️", "FCFS / SJF",    "OS scheduling algorithms"),
            ("🔀", "Hybrid Sched",   "Parallel lane dispatch"),
            ("🚨", "Breakdown Sim",  "Fault tolerance & recovery"),
        ]
        s_cols = st.columns(4)
        for i, (icon, name, desc) in enumerate(stack_items):
            with s_cols[i % 4]:
                st.markdown(f"""
                <div class="future-card">
                    <div style="font-size:1.5rem;margin-bottom:0.3rem">{icon}</div>
                    <div class="future-title">{name}</div>
                    <div class="future-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()