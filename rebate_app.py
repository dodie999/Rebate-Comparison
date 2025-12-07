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
    ("Tiered Volume (Annual)", "Growth (Over Benchmark)", "Tiered Retention (Quarter & Annual)")
)

# Global Input: Price
avg_price = st.sidebar.number_input("Average Price per Tonne (EGP)", value=50000, min_value=0, step=1000)

# ==========================================
# 1. TIERED VOLUME (ANNUAL)
# ==========================================
if rebate_type == "Tiered Volume (Annual)":
    st.sidebar.subheader("Define Annual Tiers")
    t1_vol = st.sidebar.number_input("Tier 1 Volume (Tons)", value=48, min_value=0)
    t1_pct = st.sidebar.number_input("Tier 1 Rebate (%)", value=0.75, step=0.1) / 100
    
    t2_vol = st.sidebar.number_input("Tier 2 Volume (Tons)", value=72, min_value=0)
    t2_pct = st.sidebar.number_input("Tier 2 Rebate (%)", value=1.00, step=0.1) / 100
    
    t3_vol = st.sidebar.number_input("Tier 3 Volume (Tons)", value=96, min_value=0)
    t3_pct = st.sidebar.number_input("Tier 3 Rebate (%)", value=1.50, step=0.1) / 100

    st.subheader("📊 Annual Volume Scenario")
    
    max_sim = int(t3_vol * 1.5) if t3_vol > 0 else 200
    sim_vol = st.slider("Simulate Total Annual Volume (Tons)", 0, max_sim, int(t1_vol))

    # Calculation Logic
    current_rate = 0.0
    if sim_vol >= t3_vol and t3_vol > 0: current_rate = t3_pct
    elif sim_vol >= t2_vol and t2_vol > 0: current_rate = t2_pct
    elif sim_vol >= t1_vol and t1_vol > 0: current_rate = t1_pct
    
    total_rebate = sim_vol * avg_price * current_rate
    effective_discount = current_rate * 100

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Projected Total Rebate", f"{total_rebate:,.0f} EGP", delta_color="normal")
    c2.metric("Effective Discount", f"{effective_discount:.2f}%")
    
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

    # Visualization
    x_max_plot = int(t3_vol * 1.3) if t3_vol > 0 else 100
    x_vals = list(range(0, x_max_plot))
    y_vals = []
    
    for x in x_vals:
        r = 0
        if x >= t3_vol and t3_vol > 0: r = t3_pct
        elif x >= t2_vol and t2_vol > 0: r = t2_pct
        elif x >= t1_vol and t1_vol > 0: r = t1_pct
        y_vals.append(x * avg_price * r)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Rebate Value', line=dict(color='#2E86C1', width=3)))
    fig.add_trace(go.Scatter(x=[sim_vol], y=[total_rebate], mode='markers', name='You Are Here', marker=dict(color='red', size=12)))
    
    if t1_vol > 0: fig.add_vline(x=t1_vol, line_dash="dash", annotation_text="Tier 1")
    if t2_vol > 0: fig.add_vline(x=t2_vol, line_dash="dash", annotation_text="Tier 2")
    if t3_vol > 0: fig.add_vline(x=t3_vol, line_dash="dash", annotation_text="Tier 3")

    fig.update_layout(title="Potential Earnings (The 'Cliff' Effect)", xaxis_title="Annual Volume (Tons)", yaxis_title="Rebate Value (EGP)")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 2. GROWTH REBATE
# ==========================================
elif rebate_type == "Growth (Over Benchmark)":
    st.sidebar.subheader("Growth Settings")
    benchmark_vol = st.sidebar.number_input("Benchmark Volume (Last Year)", value=100, min_value=0)
    growth_rebate_pct = st.sidebar.number_input("Growth Rebate (%)", value=3.0, step=0.1) / 100
    
    st.subheader("🚀 Growth Accelerator")
    
    sim_vol_growth = st.slider("Simulate Total Volume", 0, int(benchmark_vol * 2) if benchmark_vol > 0 else 200, int(benchmark_vol))
    
    growth_vol = max(0, sim_vol_growth - benchmark_vol)
    growth_payout = growth_vol * avg_price * growth_rebate_pct
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Growth Volume", f"{growth_vol} Tons")
    c2.metric("Growth Payout", f"{growth_payout:,.0f} EGP")
    
    if growth_vol > 0:
        per_ton_value = growth_payout / growth_vol
        c3.metric("Extra Value per Growth Ton", f"{per_ton_value:,.0f} EGP/ton")
    else:
        c3.metric("Status", "Below Benchmark", delta_color="inverse")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Volume'], y=[min(sim_vol_growth, benchmark_vol)], 
        name='Benchmark (Standard)', marker_color='lightgrey'
    ))
    
    if growth_vol > 0:
        fig.add_trace(go.Bar(
            x=['Volume'], y=[growth_vol], 
            name='Growth (Rebate Active)', marker_color='#28B463',
            text=f"+{growth_payout:,.0f} EGP", textposition='auto'
        ))

    fig.update_layout(barmode='stack', title="Volume Split: Standard vs. Growth", yaxis_title="Tons")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. TIERED RETENTION (QUARTERLY + ANNUAL)
# ==========================================
elif rebate_type == "Tiered Retention (Quarter & Annual)":
    
    # --- CONFIGURATION (SIDEBAR) ---
    with st.sidebar.expander("1. Annual Tiers (EOY Bonus)", expanded=False):
        at1_vol = st.number_input("Annual T1 Vol", value=200, min_value=0); at1_pct = st.number_input("Annual T1 %", value=0.5)/100
        at2_vol = st.number_input("Annual T2 Vol", value=300, min_value=0); at2_pct = st.number_input("Annual T2 %", value=0.75)/100
        at3_vol = st.number_input("Annual T3 Vol", value=400, min_value=0); at3_pct = st.number_input("Annual T3 %", value=1.0)/100

    with st.sidebar.expander("2. Quarterly Tiers (Recurring)", expanded=True):
        qt1_vol = st.number_input("Quarterly T1 Vol", value=50, min_value=0); qt1_pct = st.number_input("Quarterly T1 %", value=0.5)/100
        qt2_vol = st.number_input("Quarterly T2 Vol", value=75, min_value=0); qt2_pct = st.number_input("Quarterly T2 %", value=0.75)/100
        qt3_vol = st.number_input("Quarterly T3 Vol", value=100, min_value=0); qt3_pct = st.number_input("Quarterly T3 %", value=1.0)/100

    # --- TOP SUMMARY: THE RULES ---
    st.subheader("📋 Retention Plan Targets")
    
    # Create DataFrames for clean display
    q_data = {
        "Tier": ["Tier 1", "Tier 2", "Tier 3"],
        "Quarterly Target (Tons)": [qt1_vol, qt2_vol, qt3_vol],
        "Rebate %": [f"{qt1_pct*100}%", f"{qt2_pct*100}%", f"{qt3_pct*100}%"]
    }
    
    a_data = {
        "Tier": ["Tier 1", "Tier 2", "Tier 3"],
        "Annual Target (Tons)": [at1_vol, at2_vol, at3_vol],
        "Bonus %": [f"{at1_pct*100}%", f"{at2_pct*100}%", f"{at3_pct*100}%"]
    }

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Quarterly Targets (Credit Notes)**")
        st.dataframe(pd.DataFrame(q_data), hide_index=True, use_container_width=True)
    with c2:
        st.markdown("**Annual Targets (EOY Bonus)**")
        st.dataframe(pd.DataFrame(a_data), hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("📅 Performance Simulator")

    # Simulation Sliders
    col1, col2, col3, col4 = st.columns(4)
    with col1: q1_v = st.number_input("Q1 Volume", value=60, min_value=0)
    with col2: q2_v = st.number_input("Q2 Volume", value=80, min_value=0)
    with col3: q3_v = st.number_input("Q3 Volume", value=40, min_value=0)
    with col4: q4_v = st.number_input("Q4 Volume", value=0, min_value=0)

    # --- CALCULATIONS ---
    def get_q_rate(v):
        if v >= qt3_vol and qt3_vol > 0: return qt3_pct
        elif v >= qt2_vol and qt2_vol > 0: return qt2_pct
        elif v >= qt1_vol and qt1_vol > 0: return qt1_pct
        return 0.0

    q_volumes = [q1_v, q2_v, q3_v, q4_v]
    q_rates = [get_q_rate(v) for v in q_volumes]
    q_values = [v * avg_price * r for v, r in zip(q_volumes, q_rates)]
    
    total_q_rebate = sum(q_values)
    total_year_vol = sum(q_volumes)

    # Annual Logic
    year_rate = 0.0
    if total_year_vol >= at3_vol and at3_vol > 0: year_rate = at3_pct
    elif total_year_vol >= at2_vol and at2_vol > 0: year_rate = at2_pct
    elif total_year_vol >= at1_vol and at1_vol > 0: year_rate = at1_pct
    
    annual_bonus = total_year_vol * avg_price * year_rate
    grand_total = total_q_rebate + annual_bonus

    # --- METRICS ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Quarterly Credit Notes", f"{total_q_rebate:,.0f} EGP")
    m2.metric("End of Year Bonus", f"{annual_bonus:,.0f} EGP")
    m3.metric("GRAND TOTAL VALUE", f"{grand_total:,.0f} EGP", delta="Total Cash Back")

    # --- VISUALIZATION: % Achieved ---
    quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'EOY Bonus']
    
    # Y-Axis Data: Percentage Rates Achieved
    rates_pct = [r * 100 for r in q_rates] + [year_rate * 100]
    
    # Text Labels: Combining % and Cash Value
    # e.g. "0.75% (45,000)"
    text_labels = [f"{r:.2f}%<br>({v:,.0f} EGP)" for r, v in zip(rates_pct[:-1], q_values)]
    text_labels.append(f"{rates_pct[-1]:.2f}%<br>({annual_bonus:,.0f} EGP)")
    
    colors = ['#3498DB'] * 4 + ['#F1C40F'] # Blue for Qs, Gold for EOY

    fig = go.Figure(go.Bar(
        x=quarters,
        y=rates_pct,
        marker_color=colors,
        text=text_labels,
        textposition='auto',
        hovertemplate='%{y:.2f}% Achieved<br>Value: %{text}<extra></extra>'
    ))
    
    # Add a reference line for the MAX annual tier to show them what they are aiming for
    max_annual_target = at3_pct * 100
    fig.add_hline(y=max_annual_target, line_dash="dot", annotation_text="Max Annual Tier Target", annotation_position="top right")
    
    fig.update_layout(
        title="Retention Performance (% Achieved vs Target)", 
        yaxis_title="Rebate Percentage Earned (%)",
        yaxis_range=[0, max(max_annual_target * 1.2, 1.5)] # Scale graph nicely
    )
    st.plotly_chart(fig, use_container_width=True)

    if annual_bonus == 0:
        st.warning(f"⚠ You are currently missing the Annual Bonus! Total Volume: {total_year_vol}. Need {at1_vol} to unlock.")
    else:
        st.success(f"🎉 You have unlocked the Annual Bonus Tier!")
