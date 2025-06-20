import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time

# Global variables
latest_distance = "Waiting..."
latest_zone = "Waiting..."

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ Connected to MQTT")
    client.subscribe("iot/distance")
    client.subscribe("iot/zone")

def on_message(client, userdata, msg):
    global latest_distance, latest_zone
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "iot/distance":
        latest_distance = f"{float(payload):.2f} cm"
    elif topic == "iot/zone":
        latest_zone = payload

# MQTT Thread
def mqtt_thread():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

# Start MQTT background thread
threading.Thread(target=mqtt_thread, daemon=True).start()

# Streamlit UI Setup
st.set_page_config(page_title="Distance Monitor", layout="centered")
st.title("📡 Real-Time Distance & Zone Monitor")

col1, col2 = st.columns(2)
dist_box = col1.empty()
zone_box = col2.empty()

# Color mapping
zone_colors = {
    "Safe": "#28a745",      # Green
    "Caution": "#ffc107",   # Orange
    "Warning": "#dc3545",   # Red
    "Danger": "#6f0000"     # Dark red
}

zone_emojis = {
    "Safe": "✅",
    "Caution": "⚠️",
    "Warning": "🚨",
    "Danger": "🛑"
}

# Live update loop
while True:
    dist_box.metric("📏 Distance", latest_distance)

    zone_color = zone_colors.get(latest_zone, "#6c757d")  # Gray fallback
    emoji = zone_emojis.get(latest_zone, "❓")

    zone_box.markdown(f"""
        <div style='padding:1.5rem;background-color:{zone_color};
                     border-radius:12px;text-align:center;color:white;
                     font-size:1.8rem;font-weight:bold'>
            {emoji} {latest_zone}
        </div>
    """, unsafe_allow_html=True)

    time.sleep(2)
