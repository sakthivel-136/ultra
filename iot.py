import streamlit as st
from streamlit_autorefresh import st_autorefresh
import paho.mqtt.client as mqtt
import threading
import joblib
import numpy as np

# ========== Load model and encoder ==========
model = joblib.load("distance_model.pkl")
le = joblib.load("label_encoder.pkl")

# ========== Global values ==========
if "latest_distance" not in st.session_state:
    st.session_state.latest_distance = "Waiting..."
if "latest_status" not in st.session_state:
    st.session_state.latest_status = "Waiting..."

# ========== MQTT callbacks ==========
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ MQTT Connected")
    client.subscribe("iot/distance")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        distance = float(payload)
        st.session_state.latest_distance = f"{distance:.2f} cm"
        pred = model.predict([[distance]])
        status = le.inverse_transform(pred)[0]
        st.session_state.latest_status = status
        print(f"📡 {distance:.2f} → {status}")
    except Exception as e:
        print("[ERROR]", e)
        st.session_state.latest_distance = "Error"
        st.session_state.latest_status = "⚠️ Invalid"

# ========== Start MQTT in background only once ==========
if "mqtt_started" not in st.session_state:
    def mqtt_thread():
        client = mqtt.Client(client_id="streamlit_ui", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("broker.hivemq.com", 1883, 60)
        client.loop_forever()
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_started = True

# ========== Auto-refresh every 10 seconds ==========
st_autorefresh(interval=10000, key="refresh")

# ========== Streamlit UI ==========
st.set_page_config(page_title="Distance Monitor", layout="centered")
st.markdown("""
    <style>
    .card {
        background-color: #1e1e1e;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 0 12px rgba(0, 255, 255, 0.3);
        text-align: center;
        margin: 10px 0;
    }
    .title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #00e0ff;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🤖 Real-Time ML Distance Monitor</div>', unsafe_allow_html=True)

# UI layout
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
        <div class="card">
            <h3>📏 Distance</h3>
            <h1 style='color:#00ffcc'>{st.session_state.latest_distance}</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    emoji = "✅" if "safe" in st.session_state.latest_status.lower() else "⚠️"
    st.markdown(f"""
        <div class="card">
            <h3>🧠 Predicted Status</h3>
            <h1 style='color:#00ffcc'>{emoji} {st.session_state.latest_status}</h1>
        </div>
    """, unsafe_allow_html=True)
