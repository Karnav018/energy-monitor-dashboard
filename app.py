import streamlit as st
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import requests  # NEW: Required for fetching IoT data

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

    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #111 0%, #000 80%);
        color: #e0e0e0;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 95% !important;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    h1, h2, h3 { font-family: 'Orbitron', sans-serif; letter-spacing: 2px; }
    p, div, span { font-family: 'Rajdhani', sans-serif; }

    /* HUD CARD */
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
        font-family: 'Orbitron', sans-serif; font-size: 0.7rem; color: #888;
        text-transform: uppercase; letter-spacing: 1.5px;
    }
    .metric-value {
        font-family: 'Orbitron', sans-serif; font-size: 2.0rem; font-weight: 700;
        color: #fff; text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
    }
    .metric-unit { font-size: 1rem; color: #666; margin-left: 5px; }

    /* CONSOLE BOX */
    .console-box {
        background-color: #0a0a0a; border: 1px solid #333; border-radius: 4px;
        padding: 15px; font-family: 'Courier New', monospace; font-size: 0.8rem;
        color: #0f0; height: 220px; overflow-y: hidden;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    .console-line {
        border-bottom: 1px solid #1a1a1a; padding: 3px 0;
        display: flex; justify-content: space-between; opacity: 0.9;
    }
    .live-dot {
        height: 12px; width: 12px; background-color: #0f0; border-radius: 50%;
        display: inline-block; box-shadow: 0 0 8px #0f0; margin-right: 10px;
    }
    
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'energy' not in st.session_state:
    st.session_state.energy = 0.0
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=['Time', 'Power'])

# --- 4. SIDEBAR CONFIG ---
with st.sidebar:
    st.markdown("<h3 style='font-family:Orbitron; color:#fff;'>SYSTEM CONTROL</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # NEW: Connection Mode Selection
    data_source = st.radio("Data Source", ["Simulation", "Live Device"], index=0)
    
    if data_source == "Live Device":
        device_ip = st.text_input("ESP32 IP Address", "192.168.1.100")
        api_endpoint = f"http://{device_ip}/metrics"
        st.caption(f"Fetching from: {api_endpoint}")
    
    tariff = st.number_input("Tariff Rate (₹/kWh)", value=7.50, step=0.25)
    refresh_rate = st.slider("Polling Rate (s)", 0.5, 5.0, 1.0)
    
    if data_source == "Live Device":
        st.success("MODE: LIVE IOT")
    else:
        st.info("MODE: DEMO SIMULATION")

# --- 5. HELPER FUNCTIONS ---
def get_data():
    """
    Fetches data either from the random simulator OR the real ESP32 API.
    """
    # CASE A: SIMULATION
    if data_source == "Simulation":
        voltage = 230 + np.random.normal(0, 5)
        current = 5 + np.random.normal(0, 2)
        voltage = max(180, voltage) 
        current = max(0.1, current)
        power = voltage * current * 0.92 # Assuming PF 0.92
        
        # Manually increment energy for simulation
        kwh_increment = (power / 1000) * (refresh_rate / 3600)
        st.session_state.energy += kwh_increment
        
        return {
            "voltage": voltage, "current": current, "power": power, 
            "energy": st.session_state.energy, "freq": 50.0, "pf": 0.92,
            "status": "SIMULATED"
        }

    # CASE B: LIVE IOT DEVICE
    else:
        try:
            # We expect the ESP32 to return JSON: 
            # {"voltage": 230.5, "current": 4.2, "power": 960, "energy": 120.5, "frequency": 50.0, "pf": 0.95}
            response = requests.get(api_endpoint, timeout=2)
            if response.status_code == 200:
                data = response.json()
                # Update session energy to match meter reading
                st.session_state.energy = data.get('energy', 0)
                return {
                    "voltage": float(data.get('voltage', 0)),
                    "current": float(data.get('current', 0)),
                    "power": float(data.get('power', 0)),
                    "energy": float(data.get('energy', 0)),
                    "freq": float(data.get('frequency', 50.0)),
                    "pf": float(data.get('pf', 0.9)),
                    "status": "ONLINE"
                }
            else:
                return None
        except Exception as e:
            return None

def get_hud_card_html(label, value, unit, is_cost=False):
    card_class = "hud-card cost" if is_cost else "hud-card"
    return f"""
        <div class="{card_class}">
            <div class="metric-label">{label}</div>
            <div style="display:flex; align-items:baseline;">
                <span class="metric-value">{value}</span>
                <span class="metric-unit">{unit}</span>
            </div>
        </div>
    """

def create_gauge(value, title, min_v, max_v, color_hex="#00d4ff"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
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
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#888", 'family': "Rajdhani"},
                      margin=dict(l=30, r=30, t=40, b=20), height=200)
    return fig

def create_chart(history_df):
    df = history_df.copy()
    today_str = datetime.now().strftime('%Y-%m-%d')
    try:
        df['Datetime'] = pd.to_datetime(today_str + ' ' + df['Time'])
    except:
        df['Datetime'] = df['Time']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Datetime'], y=df['Power'], mode='lines',
        line=dict(color='#00d4ff', width=3, shape='spline', smoothing=1.0),
        fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.15)',
        hovertemplate='<b>%{y:.0f} W</b><extra></extra>' 
    ))

    if not df.empty:
        y_max = df['Power'].max()
        padding = y_max * 0.2 if y_max > 0 else 100
        range_y = [0, y_max + padding]
    else:
        range_y = [0, 500]

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=0, t=10, b=20), height=250,
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#666'), tickformat='%H:%M:%S'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', tickfont=dict(color='#666'), range=range_y),
        showlegend=False, hovermode="x unified",
        hoverlabel=dict(bgcolor="#111", font_size=12, font_family="Orbitron")
    )
    return fig

# --- 6. LAYOUT SKELETON ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown("""
        <div style="display: flex; align-items: center;">
            <div class="live-dot"></div>
            <span style="font-family:'Orbitron'; font-size: 1.5rem; font-weight:700;">ENERGY<span style="color:#00d4ff">OS</span> / DASHBOARD</span>
        </div>
    """, unsafe_allow_html=True)
with header_col2:
    time_placeholder = st.empty()

st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
p_volts, p_amps, p_watts, p_cost = m1.empty(), m2.empty(), m3.empty(), m4.empty()

# Visuals Row
c_left, c_mid, c_right = st.columns([1.5, 1.5, 2])
with c_left: gauge_v_placeholder = st.empty()
with c_mid: gauge_c_placeholder = st.empty()
with c_right: console_placeholder = st.empty()

st.markdown("<h5 style='margin-top:10px; color:#666;'>REAL-TIME POWER CONSUMPTION</h5>", unsafe_allow_html=True)
chart_placeholder = st.empty()

# --- 7. MAIN LOOP ---
while True:
    data = get_data()
    now_str = datetime.now().strftime("%H:%M:%S")

    # Handle connection errors gracefully
    if data is None:
        console_placeholder.markdown(f"""
            <div class="console-box" style="border: 1px solid red;">
                <div style="color: red; font-weight: bold;">>> CONNECTION ERROR</div>
                <div class="console-line">Target: {device_ip}</div>
                <div class="console-line">Status: UNREACHABLE</div>
                <br><span>Check ESP32 IP or WiFi...</span>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        continue

    # Process Data
    cost = data['energy'] * tariff
    
    # Update History
    new_row = pd.DataFrame({'Time': [now_str], 'Power': [data['power']]})
    st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True).tail(50)

    # Render UI
    time_placeholder.markdown(f"<div style='text-align:right; font-family:Orbitron; color:#888; font-size:1.2rem;'>{now_str}</div>", unsafe_allow_html=True)
    
    p_volts.markdown(get_hud_card_html("GRID VOLTAGE", f"{data['voltage']:.1f}", "V"), unsafe_allow_html=True)
    p_amps.markdown(get_hud_card_html("CURRENT DRAW", f"{data['current']:.2f}", "A"), unsafe_allow_html=True)
    p_watts.markdown(get_hud_card_html("ACTIVE POWER", f"{int(data['power'])}", "W"), unsafe_allow_html=True)
    p_cost.markdown(get_hud_card_html("EST. COST", f"{cost:.2f}", "₹", is_cost=True), unsafe_allow_html=True)

    gauge_v_placeholder.plotly_chart(create_gauge(data['voltage'], "VOLTAGE (V)", 0, 300, "#00d4ff"), use_container_width=True, config={'displayModeBar': False})
    gauge_c_placeholder.plotly_chart(create_gauge(data['current'], "CURRENT (A)", 0, 30, "#ff0055"), use_container_width=True, config={'displayModeBar': False})

    # Diagnostic Logic
    v_status = "STABLE" if 200 < data['voltage'] < 250 else "WARN"
    v_col = "#0f0" if v_status == "STABLE" else "#fa0"
    
    console_placeholder.markdown(f"""
        <div class="console-box">
            <div style="border-bottom: 1px solid #333; margin-bottom: 10px; color: #fff;">>> IOT_DIAGNOSTICS_LIVE</div>
            <div class="console-line"><span>> SOURCE</span><span>{data.get('status', 'IOT')}</span></div>
            <div class="console-line"><span>> GRID_FREQ</span><span>{data.get('freq', 50.0):.1f} Hz</span></div>
            <div class="console-line"><span>> POWER_FACTOR</span><span>{data.get('pf', 0.9):.2f}</span></div>
            <div class="console-line"><span>> VOLTAGE_STATUS</span><span style="color:{v_col}">[{v_status}]</span></div>
            <div style="color:#666; font-size:0.7rem; margin-top:10px;">> PACKET_RX: {now_str}</div>
        </div>
    """, unsafe_allow_html=True)

    chart_placeholder.plotly_chart(create_chart(st.session_state.history), use_container_width=True, config={'displayModeBar': False})
    
    time.sleep(refresh_rate)