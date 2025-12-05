import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Eagle Chemicals Rebate Simulator", layout="wide")

st.title("🦅 Eagle Chemicals: Customer Rebate Simulator")
st.markdown("### Interactive Value Calculator")
st.markdown("---")

# --- SIDEBAR: REBATE SELECTOR ---
st.sidebar.header("Configuration")
rebate_type = st.sidebar.selectbox(
    "Select Rebate Structure",
    ("Tiered Volume (Annual)", "Growth (Over Benchmark)", "Tiered (Quarterly + Annual)")
)

# Global Input: Price
avg_price = st.sidebar.number_input("Average Price per Tonne (EGP)", value=50000, step=1000)

# ==========================================
# 1. TIERED VOLUME (ANNUAL)
# ==========================================
if rebate_type == "Tiered Volume (Annual)":
    st.sidebar.subheader("Define Annual Tiers")
    t1_vol = st.sidebar.number_input("Tier 1 Volume (Tons)", value=48)
    t1_pct = st.sidebar.number_input("Tier 1 Rebate (%)", value=0.75, step=0.1) / 100
    
    t2_vol = st.sidebar.number_input("Tier 2 Volume (Tons)", value=72)
    t2_pct = st.sidebar.number_input("Tier 2 Rebate (%)", value=1.00, step=0.1) / 100
    
    t3_vol = st.sidebar.number_input("Tier 3 Volume (Tons)", value=96)
    t3_pct = st.sidebar.number_input("Tier 3 Rebate (%)", value=1.50, step=0.1) / 100

    st.subheader("📊 Annual Volume Scenario")
    
    # Simulation Input
    sim_vol = st.slider("Simulate Total Annual Volume (Tons)", 0, int(t3_vol * 1.5), int(t1_vol - 5))

    # Calculation Logic
    current_rate = 0.0
    if sim_vol >= t3_vol: current_rate = t3_pct
    elif sim_vol >= t2_vol: current_rate = t2_pct
    elif sim_vol >= t1_vol: current_rate = t1_pct
    
    total_rebate = sim_vol * avg_price * current_rate
    effective_discount = current_rate * 100

    # Metrics Row
    c1, c2, c3 = st.columns(3)
    c1.metric("Projected Total Rebate", f"{total_rebate:,.0f} EGP", delta_color="normal")
    c2.metric("Effective Discount", f"{effective_discount:.2f}%")
    
    # Distance to next tier
    if sim_vol < t1_vol:
        dist = t1_vol - sim_vol
        c3.info(f"⚠ Buy **{dist} more tons** to unlock Tier 1!")
    elif sim_vol < t2_vol:
        dist = t2_vol - sim_vol
        c3.info(f"🚀 Buy **{dist} more tons** to jump to Tier 2!")
    elif sim_vol < t3_vol:
        dist = t3_vol - sim_vol
        c3.info(f"🔥 Buy **{dist} more tons** to hit MAX Tier!")
    else:
        c3.success("🏆 Maximum Tier Achieved!")

    # Visualization: The "Cliff" Chart
    x_vals = list(range(0, int(t3_vol * 1.3)))
    y_vals = []
    for x in x_vals:
        r = 0
        if x >= t3_vol: r = t3_pct
        elif x >= t2_vol: r = t2_pct
        elif x >= t1_vol: r = t1_pct
        y_vals.append(x * avg_price * r)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Rebate Value', line=dict(color='#2E86C1', width=3)))
    fig.add_trace(go.Scatter(x=[sim_vol], y=[total_rebate], mode='markers', name='You Are Here', marker=dict(color='red', size=12)))
    
    # Add Tier Lines
    fig.add_vline(x=t1_vol, line_dash="dash", annotation_text="Tier 1")
    fig.add_vline(x=t2_vol, line_dash="dash", annotation_text="Tier 2")
    fig.add_vline(x=t3_vol, line_dash="dash", annotation_text="Tier 3")

    fig.update_layout(title="Potential Earnings (The 'Cliff' Effect)", xaxis_title="Annual Volume (Tons)", yaxis_title="Rebate Value (EGP)")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 2. GROWTH REBATE
# ==========================================
elif rebate_type == "Growth (Over Benchmark)":
    st.sidebar.subheader("Growth Settings")
    benchmark_vol = st.sidebar.number_input("Benchmark Volume (Last Year)", value=100)
    growth_rebate_pct = st.sidebar.number_input("Growth Rebate (%)", value=5.0) / 100
    
    st.subheader("🚀 Growth Accelerator")
    
    sim_vol_growth = st.slider("Simulate Total Volume", 0, int(benchmark_vol * 2), int(benchmark_vol))
    
    growth_vol = max(0, sim_vol_growth - benchmark_vol)
    growth_payout = growth_vol * avg_price * growth_rebate_pct
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Growth Volume", f"{growth_vol} Tons")
    c2.metric("Growth Payout", f"{growth_payout:,.0f} EGP")
    
    # Implied Margin Calc
    if growth_vol > 0:
        per_ton_value = growth_payout / growth_vol
        c3.metric("Extra Value per Growth Ton", f"{per_ton_value:,.0f} EGP/ton")
    else:
        c3.metric("Status", "Below Benchmark", delta_color="inverse")

    # Visualization: Waterfall / Area
    fig = go.Figure()
    
    # Base Bar
    fig.add_trace(go.Bar(
        x=['Volume'], 
        y=[min(sim_vol_growth, benchmark_vol)], 
        name='Benchmark (Standard)', 
        marker_color='lightgrey'
    ))
    
    # Growth Bar
    if growth_vol > 0:
        fig.add_trace(go.Bar(
            x=['Volume'], 
            y=[growth_vol], 
            name='Growth (Rebate Active)', 
            marker_color='#28B463',
            text=f"+{growth_payout:,.0f} EGP",
            textposition='auto'
        ))

    fig.update_layout(barmode='stack', title="Volume Split: Standard vs. Growth", yaxis_title="Tons")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. QUARTERLY + ANNUAL (COMPLEX)
# ==========================================
elif rebate_type == "Tiered (Quarterly + Annual)":
    
    # --- INPUTS ---
    with st.sidebar.expander("1. Annual Tiers (EOY Bonus)", expanded=False):
        at1_vol = st.number_input("Annual T1 Vol", 200); at1_pct = st.number_input("Annual T1 %", 0.5)/100
        at2_vol = st.number_input("Annual T2 Vol", 300); at2_pct = st.number_input("Annual T2 %", 1.0)/100
        at3_vol = st.number_input("Annual T3 Vol", 400); at3_pct = st.number_input("Annual T3 %", 1.5)/100

    with st.sidebar.expander("2. Quarterly Tiers (Recurring)", expanded=True):
        qt1_vol = st.number_input("Quarterly T1 Vol", 50); qt1_pct = st.number_input("Quarterly T1 %", 0.5)/100
        qt2_vol = st.number_input("Quarterly T2 Vol", 75); qt2_pct = st.number_input("Quarterly T2 %", 0.75)/100
        qt3_vol = st.number_input("Quarterly T3 Vol", 100); qt3_pct = st.number_input("Quarterly T3 %", 1.0)/100

    st.subheader("📅 Quarterly Progress & Annual Bonus")
    
    # Simulation Sliders for Quarters
    col1, col2, col3, col4 = st.columns(4)
    with col1: q1_v = st.number_input("Q1 Volume", value=60)
    with col2: q2_v = st.number_input("Q2 Volume", value=80)
    with col3: q3_v = st.number_input("Q3 Volume", value=40)
    with col4: q4_v = st.number_input("Q4 Volume", value=0) # Future

    # --- CALCULATIONS ---
    
    # Helper to get Q rate
    def get_q_rate(v):
        if v >= qt3_vol: return qt3_pct
        elif v >= qt2_vol: return qt2_pct
        elif v >= qt1_vol: return qt1_pct
        return 0.0

    q_volumes = [q1_v, q2_v, q3_v, q4_v]
    q_rebates = [v * avg_price * get_q_rate(v) for v in q_volumes]
    
    total_q_rebate = sum(q_rebates)
    total_year_vol = sum(q_volumes)

    # Annual Logic
    year_rate = 0.0
    if total_year_vol >= at3_vol: year_rate = at3_pct
    elif total_year_vol >= at2_vol: year_rate = at2_pct
    elif total_year_vol >= at1_vol: year_rate = at1_pct
    
    annual_bonus = total_year_vol * avg_price * year_rate
    grand_total = total_q_rebate + annual_bonus

    # --- METRICS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Quarterly Credit Notes", f"{total_q_rebate:,.0f} EGP")
    m2.metric("End of Year Bonus", f"{annual_bonus:,.0f} EGP")
    m3.metric("GRAND TOTAL VALUE", f"{grand_total:,.0f} EGP", delta="Total Cash Back")

    # --- VISUALIZATION: The Bank Builder ---
    quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'EOY Bonus']
    values = q_rebates + [annual_bonus]
    colors = ['#3498DB', '#3498DB', '#3498DB', '#3498DB', '#F1C40F'] # Blue for Qs, Gold for EOY

    fig = go.Figure(go.Bar(
        x=quarters,
        y=values,
        marker_color=colors,
        text=[f"{v:,.0f}" for v in values],
        textposition='auto'
    ))
    
    fig.update_layout(title="Your Rebate Stack (Quarterly Credits + EOY Check)", yaxis_title="Rebate Value (EGP)")
    st.plotly_chart(fig, use_container_width=True)

    # Status Message
    if annual_bonus == 0:
        st.warning(f"⚠ You are currently missing the Annual Bonus! Total Volume: {total_year_vol}. Need {at1_vol} to unlock.")
    else:
        st.success(f"🎉 You have unlocked the Annual Bonus Tier!")
