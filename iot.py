import gradio as gr
import paho.mqtt.client as mqtt
import threading
import time

# Global state
latest_distance = "Waiting..."
latest_zone = "Waiting..."
log_history = []

zone_emojis = {
    "Safe": "✅",
    "Caution": "⚠️",
    "Warning": "🚨",
    "Danger": "🛑"
}

# MQTT Callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ MQTT Connected")
    client.subscribe("iot/distance")
    client.subscribe("iot/zone")

def on_message(client, userdata, msg):
    global latest_distance, latest_zone, log_history
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "iot/distance":
        try:
            distance = float(payload)
            latest_distance = f"{distance:.2f} cm"
        except:
            latest_distance = "Invalid"
    elif topic == "iot/zone":
        latest_zone = payload

    # Log
    emoji = zone_emojis.get(latest_zone, "❓")
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {latest_distance} → {emoji} {latest_zone}"
    log_history.append(entry)
    if len(log_history) > 40:
        log_history.pop(0)

# MQTT Background Thread
def mqtt_thread():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# Update function
def update_ui():
    emoji = zone_emojis.get(latest_zone, "❓")
    return (
        gr.Textbox.update(value=latest_distance),
        gr.Textbox.update(value=f"{emoji} {latest_zone}"),
        gr.TextArea.update(value="\n".join(log_history))
    )

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("## 📡 Distance & Zone Monitor")

    with gr.Row():
        dist_display = gr.Textbox(label="📏 Distance", interactive=False)
        zone_display = gr.Textbox(label="🚦 Zone", interactive=False)

    log_box = gr.TextArea(label="📋 Last 40 Readings", lines=20, interactive=False)

    timer = gr.Timer(interval=2.0, mode="continuous")
    timer.output(update_ui, inputs=None, outputs=[dist_display, zone_display, log_box])

demo.launch()
