import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="Commercial Rebate Simulator",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Commercial Rebate Strategy Simulator")
st.markdown("""
This tool compares two distinct incentive structures:
1.  **Standard Volume Rebate (Retroactive):** Pays a % on *all* volume once a target is reached.
2.  **Growth Rebate (Marginal):** Pays a higher % only on volume *exceeding* a benchmark.
""")

st.markdown("---")

# --- Sidebar: User Inputs ---
st.sidebar.header("⚙️ Deal Parameters")

# 1. General Settings
st.sidebar.subheader("1. Volume Settings")
benchmark_vol = st.sidebar.number_input(
    "Benchmark Volume (e.g., Last Year)", 
    value=100000, 
    step=1000,
    help="The baseline volume used to calculate growth."
)
max_view_vol = st.sidebar.slider(
    "Chart Max Range", 
    min_value=benchmark_vol, 
    max_value=int(benchmark_vol*2.5), 
    value=int(benchmark_vol*1.5)
)

# 2. Tiered Rebate Settings
st.sidebar.subheader("2. Tiered Structure (Retroactive)")
st.sidebar.info("Pays % on ALL volume once tier is hit.")

tier1_vol = st.sidebar.number_input("Tier 1 Threshold", value=100000, step=1000)
tier1_pct = st.sidebar.slider("Tier 1 Rebate %", 0.0, 15.0, 2.0, 0.1, key="t1") / 100

tier2_vol = st.sidebar.number_input("Tier 2 Threshold", value=120000, step=1000)
tier2_pct = st.sidebar.slider("Tier 2 Rebate %", 0.0, 15.0, 3.0, 0.1, key="t2") / 100

# 3. Growth Rebate Settings
st.sidebar.subheader("3. Growth Structure (Marginal)")
st.sidebar.warning("Pays % ONLY on volume > Benchmark.")
growth_pct = st.sidebar.slider("Growth Rebate %", 0.0, 30.0, 15.0, 0.5, key="g1") / 100

# --- Calculation Logic ---
# Create a range of volumes from 80% of benchmark to Max View
start_vol = int(benchmark_vol * 0.8)
volumes = np.linspace(start_vol, max_view_vol, 300)

data = []

for v in volumes:
    # Tiered Logic (Retroactive)
    if v >= tier2_vol:
        tier_payout = v * tier2_pct
    elif v >= tier1_vol:
        tier_payout = v * tier1_pct
    else:
        tier_payout = 0
        
    # Growth Logic (Marginal)
    if v > benchmark_vol:
        growth_payout = (v - benchmark_vol) * growth_pct
    else:
        growth_payout = 0
        
    data.append({
        "Volume": v,
        "Tiered Payout": tier_payout,
        "Growth Payout": growth_payout,
        "Difference": growth_payout - tier_payout
    })

df = pd.DataFrame(data)

# Find Crossover Point
crossover_df = df[(df["Volume"] > benchmark_vol) & (df["Difference"] > 0)]
if not crossover_df.empty:
    crossover_vol = crossover_df.iloc[0]["Volume"]
    crossover_msg = f"🚀 The Growth Deal becomes more profitable for the buyer at **{crossover_vol:,.0f} units**."
    crossover_color = "green"
    crossover_found = True
else:
    crossover_msg = "⚠️ The Growth Deal never beats the Tiered Deal in this volume range."
    crossover_color = "red"
    crossover_found = False

# --- Visualization (Plotly) ---
fig = go.Figure()

# Tiered Line
fig.add_trace(go.Scatter(
    x=df["Volume"], 
    y=df["Tiered Payout"],
    mode='lines',
    name=f'Tiered ({tier1_pct*100:.1f}% / {tier2_pct*100:.1f}%)',
    line=dict(color='#1f77b4', width=3),
    hovertemplate='Vol: %{x:,.0f}<br>Pay: $%{y:,.0f}'
))

# Growth Line
fig.add_trace(go.Scatter(
    x=df["Volume"], 
    y=df["Growth Payout"],
    mode='lines',
    name=f'Growth ({growth_pct*100:.1f}% > {benchmark_vol/1000:.0f}k)',
    line=dict(color='#ff7f0e', width=3, dash='dash'),
    hovertemplate='Vol: %{x:,.0f}<br>Pay: $%{y:,.0f}'
))

# Crossover Marker
if crossover_found:
    crossover_y = crossover_df.iloc[0]["Growth Payout"]
    fig.add_trace(go.Scatter(
        x=[crossover_vol],
        y=[crossover_y],
        mode='markers',
        name='Crossover Point',
        marker=dict(color='red', size=12, symbol='x')
    ))

# Formatting
fig.update_layout(
    xaxis_title="Total Volume Purchased",
    yaxis_title="Total Rebate Paid ($)",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    height=550,
    margin=dict(l=20, r=20, t=40, b=20)
)

# --- Layout Output ---
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Analysis")
    st.markdown(f":{crossover_color}[{crossover_msg}]")
    
    st.markdown("---")
    st.markdown("### 🔍 Scenario Check")
    check_vol = st.number_input("Test a specific volume:", value=int(benchmark_vol*1.25), step=1000)
    
    # Calculate for single point
    if check_vol >= tier2_vol: t_pay = check_vol * tier2_pct
    elif check_vol >= tier1_vol: t_pay = check_vol * tier1_pct
    else: t_pay = 0
    
    if check_vol > benchmark_vol: g_pay = (check_vol - benchmark_vol) * growth_pct
    else: g_pay = 0
    
    diff = g_pay - t_pay
    
    st.metric("Tiered Payout", f"${t_pay:,.0f}")
    st.metric(
        "Growth Payout", 
        f"${g_pay:,.0f}", 
        delta=f"{diff:,.0f}", 
        delta_color="normal"
    )
    
    if diff > 0:
        st.success("Growth deal is better.")
    elif diff < 0:
        st.info("Tiered deal is better.")
    else:
        st.warning("Payouts are equal.")

# Data Table
with st.expander("📋 View Calculation Table"):
    st.dataframe(
        df.style.format({
            "Volume": "{:,.0f}", 
            "Tiered Payout": "${:,.2f}", 
            "Growth Payout": "${:,.2f}", 
            "Difference": "${:,.2f}"
        })
    )
