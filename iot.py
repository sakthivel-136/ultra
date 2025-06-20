import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time

latest_distance = "Waiting..."
latest_zone = "Waiting..."

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
    print(f"{topic}: {payload}")

def mqtt_thread():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# Streamlit UI
st.set_page_config(page_title="Live Distance Monitor", layout="centered")

st.title("📡 Live Ultrasonic Monitor")
col1, col2 = st.columns(2)

with col1:
    dist_box = st.empty()
with col2:
    zone_box = st.empty()

while True:
    dist_box.metric("📏 Distance", latest_distance)
    color = {
        "Safe": "green",
        "Caution": "orange",
        "Warning": "red",
        "Danger": "darkred"
    }.get(latest_zone, "gray")
    
    zone_box.markdown(f"""
        <div style='padding:2rem;background-color:{color};color:white;
                    text-align:center;font-size:2rem;border-radius:10px'>
            🚨 {latest_zone}
        </div>
    """, unsafe_allow_html=True)

    time.sleep(2)
