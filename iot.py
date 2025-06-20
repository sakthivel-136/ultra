import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time
import joblib
import numpy as np

# Load ML model and label encoder
model = joblib.load("distance_model.pkl")
le = joblib.load("label_encoder.pkl")

# Globals to store data
latest_distance = "Waiting..."
latest_status = "Waiting..."

# MQTT callback functions
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ MQTT Connected")
    client.subscribe("iot/distance")

def on_message(client, userdata, msg):
    global latest_distance, latest_status
    try:
        distance = float(msg.payload.decode())
        latest_distance = f"{distance:.2f} cm"

        # Predict status using ML model
        pred = model.predict([[distance]])
        status = le.inverse_transform(pred)[0]
        latest_status = status

        # Publish prediction to ESP
        client.publish("iot/status", status)

        print(f"📡 Distance: {latest_distance} → Status: {latest_status}")
    except Exception as e:
        latest_distance = "Error"
        latest_status = "⚠️ Invalid"
        print(f"Error: {e}")

# Background MQTT thread
def mqtt_thread():
    client = mqtt.Client(client_id="streamlit_ui", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# Streamlit UI setup
st.set_page_config(page_title="Distance Monitor", layout="centered")

# Custom styling
st.markdown("""
    <style>
        body {
            background-color: #111;
            color: #fff;
        }
        .card {
            background-color: #1e1e1e;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 0 12px rgba(0, 255, 255, 0.2);
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

# Title
st.markdown('<div class="title">💡 Real-Time Distance Monitor</div>', unsafe_allow_html=True)

# Layout
col1, col2 = st.columns(2)
with col1:
    dist_box = st.empty()
with col2:
    stat_box = st.empty()

# UI loop
while True:
    with col1:
        dist_box.markdown(f"""
            <div class="card">
                <h3>📏 Distance</h3>
                <h1 style='color:#00ffcc'>{latest_distance}</h1>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        emoji = "✅" if "safe" in latest_status.lower() else "⚠️"
        stat_box.markdown(f"""
            <div class="card">
                <h3>🧠 ML Prediction</h3>
                <h1 style='color:#00ffcc'>{emoji} {latest_status}</h1>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(5)
