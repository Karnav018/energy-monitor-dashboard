import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IoT Energy Monitor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');

    /* --- RESET & LAYOUT --- */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #111 0%, #000 80%);
        color: #e0e0e0;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 95% !important;
    }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* --- TYPOGRAPHY --- */
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    p, div, span { font-family: 'Rajdhani', sans-serif; }

    /* --- HUD CARD --- */
    .hud-card {
        background: rgba(20, 20, 20, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 3px solid #00d4ff;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .hud-card.cost { border-left-color: #ffd700; }
    
    .metric-label {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    .metric-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.0rem;
        font-weight: 700;
        color: #fff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    
    .metric-unit {
        font-size: 1rem;
        color: #666;
        margin-left: 5px;
    }

    /* --- CONSOLE BOX --- */
    .console-box {
        background-color: #0a0a0a;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        color: #0f0;
        height: 220px;
        overflow-y: hidden;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .console-line {
        border-bottom: 1px solid #1a1a1a;
        padding: 3px 0;
        display: flex;
        justify-content: space-between;
        opacity: 0.9;
    }
    
    .live-dot {
        height: 12px;
        width: 12px;
        background-color: #0f0;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #0f0;
        margin-right: 10px;
    }
    
    [data-testid="stSidebar"] {
        background-color: #080808;
        border-right: 1px solid #222;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'energy' not in st.session_state:
    st.session_state.energy = 450.00
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Power'])

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='font-family:Orbitron; color:#fff;'>SYSTEM CONTROL</h3>", unsafe_allow_html=True)
    st.markdown("---")
    tariff = st.number_input("Tariff Rate (₹/kWh)", value=7.50, step=0.25)
    refresh_rate = st.slider("Polling Rate (s)", 0.1, 5.0, 1.0)
    enable_simulation = st.checkbox("Demo Mode", value=True)
    st.success("CONNECTED: ESP32-MAC-44")

# --- 5. HELPER FUNCTIONS ---
def get_data():
    if enable_simulation:
        voltage = 230 + np.random.normal(0, 5)
        current = 5 + np.random.normal(0, 2)
        voltage = max(180, voltage) 
        current = max(0.1, current)
        power = voltage * current * 0.92
        kwh_increment = (power / 1000) * (refresh_rate / 3600)
        st.session_state.energy += kwh_increment
        return {"voltage": voltage, "current": current, "power": power, "energy": st.session_state.energy}
    return {"voltage": 0, "current": 0, "power": 0, "energy": st.session_state.energy}

def render_hud_card(col, label, value, unit, is_cost=False):
    card_class = "hud-card cost" if is_cost else "hud-card"
    col.markdown(f"""
        <div class="{card_class}">
            <div class="metric-label">{label}</div>
            <div style="display:flex; align-items:baseline;">
                <span class="metric-value">{value}</span>
                <span class="metric-unit">{unit}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_gauge(value, title, min_v, max_v, color_hex="#00d4ff"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        # TITLE FIX: Added title dict here
        title={'text': title, 'font': {'size': 14, 'color': '#888', 'family': "Orbitron"}}, 
        number={'font': {'color': "white", 'family': "Orbitron", 'size': 30}},
        gauge={
            'axis': {'range': [min_v, max_v], 'tickwidth': 1, 'tickcolor': "#444"},
            'bar': {'color': color_hex, 'thickness': 0.15}, 
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 0,
            'steps': [{'range': [min_v, max_v], 'color': "#111"}],
            'threshold': {'line': {'color': "red", 'width': 2}, 'thickness': 0.75, 'value': max_v * 0.95}
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#888", 'family': "Rajdhani"},
        margin=dict(l=30, r=30, t=40, b=20),
        height=200
    )
    return fig

def create_chart(history_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['Time'],
        y=history_df['Power'],
        mode='lines',
        line=dict(color='#00d4ff', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=10),
        height=250,
        xaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(color='#555')),
        yaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(color='#555')),
        showlegend=False
    )
    return fig

# --- 6. MAIN LOOP ---
placeholder = st.empty()

while True:
    data = get_data()
    now_str = datetime.now().strftime("%H:%M:%S")
    
    new_row = pd.DataFrame({'Time': [now_str], 'Power': [data['power']]})
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True).tail(50)

    with placeholder.container():
        
        # --- HEADER ---
        title_col, time_col = st.columns([4, 1])
        with title_col:
            st.markdown("""
                <div style="display: flex; align-items: center;">
                    <div class="live-dot"></div>
                    <span style="font-family:'Orbitron'; font-size: 1.5rem; font-weight:700;">ENERGY<span style="color:#00d4ff">OS</span> / DASHBOARD</span>
                </div>
            """, unsafe_allow_html=True)
        with time_col:
             st.markdown(f"<div style='text-align:right; font-family:Orbitron; color:#888; font-size:1.2rem;'>{now_str}</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

        # --- ROW 1: METRICS ---
        k1, k2, k3, k4 = st.columns(4)
        cost = data['energy'] * tariff
        
        render_hud_card(k1, "GRID VOLTAGE", f"{data['voltage']:.1f}", "V")
        render_hud_card(k2, "CURRENT DRAW", f"{data['current']:.2f}", "A")
        render_hud_card(k3, "ACTIVE POWER", f"{int(data['power'])}", "W")
        render_hud_card(k4, "EST. COST", f"{cost:.2f}", "₹", is_cost=True)

        # --- ROW 2: VISUALS ---
        c_left, c_mid, c_right = st.columns([1.5, 1.5, 2])
        
        with c_left:
            # FIX: Added unique key="voltage_gauge"
            st.plotly_chart(create_gauge(data['voltage'], "GRID VOLTAGE (V)", 0, 300, "#00d4ff"), use_container_width=True, config={'displayModeBar': False}, key="voltage_gauge")
        with c_mid:
            # FIX: Added unique key="current_gauge"
            st.plotly_chart(create_gauge(data['current'], "LOAD CURRENT (A)", 0, 20, "#ff0055"), use_container_width=True, config={'displayModeBar': False}, key="current_gauge")
        with c_right:
            v_status = "STABLE" if 200 < data['voltage'] < 250 else "WARN"
            v_col = "#0f0" if v_status == "STABLE" else "#fa0"
            c_status = "NOMINAL" if data['current'] < 15 else "OVERLOAD"
            c_col = "#0f0" if c_status == "NOMINAL" else "#f00"
            
            st.markdown(f"""
                <div class="console-box">
                    <div style="border-bottom: 1px solid #333; margin-bottom: 10px; color: #fff;">>> SYSTEM_DIAGNOSTICS_V4.2</div>
                    <div class="console-line"><span>> GRID_FREQ</span><span>50.02 Hz</span></div>
                    <div class="console-line"><span>> POWER_FACTOR</span><span>0.92</span></div>
                    <div class="console-line"><span>> VOLTAGE_MONITOR</span><span style="color:{v_col}">[{v_status}]</span></div>
                    <div class="console-line"><span>> LOAD_MONITOR</span><span style="color:{c_col}">[{c_status}]</span></div>
                    <div class="console-line"><span>> TEMP_SENSORS</span><span>34°C</span></div>
                    <br>
                    <div style="color:#666; font-size:0.7rem;">> LAST_SYNC: {now_str} ...</div>
                </div>
            """, unsafe_allow_html=True)

        # --- ROW 3: CHART ---
        st.markdown("<h5 style='margin-top:10px; color:#666;'>REAL-TIME POWER CONSUMPTION</h5>", unsafe_allow_html=True)
        # FIX: Added unique key="history_chart"
        st.plotly_chart(create_chart(st.session_state.history), use_container_width=True, config={'displayModeBar': False}, key="history_chart")

    time.sleep(refresh_rate)