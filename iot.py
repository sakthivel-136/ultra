import streamlit as st
import paho.mqtt.client as mqtt
import threading

# --------- GLOBAL STATE SETUP ---------
if "distance" not in st.session_state:
    st.session_state.distance = "Waiting..."
if "mqtt_started" not in st.session_state:
    st.session_state.mqtt_started = False

# --------- MQTT CALLBACKS ---------
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ MQTT connected")
    client.subscribe("iot/distance")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print("📡 Received:", payload)
        st.session_state.distance = f"{float(payload):.2f} cm"
    except:
        st.session_state.distance = "⚠️ Invalid"

# --------- MQTT THREAD START ---------
def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

if not st.session_state.mqtt_started:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state.mqtt_started = True

# --------- STREAMLIT UI ---------
st.set_page_config(page_title="Live Distance", layout="centered")
st.title("📏 Real-Time Distance from MQTT")

st.markdown("### Latest Distance:")
st.info(st.session_state.distance)

# Refresh manually
st.button("🔄 Refresh")
