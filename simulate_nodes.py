#!/usr/bin/env python3
"""
Multi-Node ESP32 Telemetry Simulator for Secure IoT-DeFi Oracle Project
-----------------------------------------------------------------------
Simulates 3 ESP32 Microcontrollers publishing JSON telemetry messages to Mosquitto MQTT broker.
Supports dynamic toggle for injecting a 500°C malicious attack payload on ESP32_Node_3.

Usage:
  python simulate_nodes.py          # Standard execution (Press ENTER to toggle attack)
  python simulate_nodes.py --attack # Launch with Node 3 attack pre-enabled
"""

import sys
import json
import time
import random
import threading
import paho.mqtt.client as mqtt

MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/sensors"

# Global Flag for Malicious Injection on Node 3
IS_ATTACK_ACTIVE = False

def simulate_node(node_id: str, base_temp: float):
    global IS_ATTACK_ACTIVE
    client = mqtt.Client(client_id=f"Simulated_{node_id}")
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        print(f"[{node_id}] Simulator started & connected to MQTT broker.")
    except Exception as e:
        print(f"[{node_id}] Notice: MQTT broker connection notice: {e}")

    while True:
        if node_id == "ESP32_Node_3" and IS_ATTACK_ACTIVE:
            current_temp = 500.0 # Extreme malicious injection payload
            status = "ATTACKED"
        else:
            # Normal thermal noise fluctuation
            noise = random.uniform(-0.5, 0.5)
            current_temp = round(base_temp + noise, 2)
            status = "HEALTHY"

        payload = {
            "node_id": node_id,
            "temperature": current_temp,
            "humidity": round(52.0 + random.uniform(-1.5, 1.5), 1),
            "status": status,
            "timestamp": int(time.time())
        }

        json_payload = json.dumps(payload)
        
        try:
            client.publish(MQTT_TOPIC, json_payload)
            status_tag = "🚨 [ATTACK PAYLOAD]" if status == "ATTACKED" else "✅ [NORMAL]"
            print(f"[{node_id}] {status_tag} Published: Temp={current_temp:.1f}°C")
        except Exception:
            pass

        time.sleep(3.0)

def keyboard_listener():
    global IS_ATTACK_ACTIVE
    print("\n" + "="*65)
    print("      PRESS [ENTER] AT ANY TIME TO TOGGLE 500°C ATTACK ON NODE 3")
    print("="*65 + "\n")
    
    while True:
        input()
        IS_ATTACK_ACTIVE = not IS_ATTACK_ACTIVE
        status_str = "ENABLED 🚨 (Node 3 Sending 500°C Malicious Payload)" if IS_ATTACK_ACTIVE else "DISABLED ✅ (Node 3 Sending Normal Telemetry)"
        print(f"\n>>>> [ATTACK SIMULATOR TOGGLE] Attack on Node 3 is now: {status_str} <<<<\n")

def main():
    global IS_ATTACK_ACTIVE
    if "--attack" in sys.argv:
        IS_ATTACK_ACTIVE = True
        print("\n>>> Launching with Malicious Attack pre-enabled on Node 3 <<<\n")

    # Spawn 3 simulated ESP32 node threads
    t1 = threading.Thread(target=simulate_node, args=("ESP32_Node_1", 25.1), daemon=True)
    t2 = threading.Thread(target=simulate_node, args=("ESP32_Node_2", 25.4), daemon=True)
    t3 = threading.Thread(target=simulate_node, args=("ESP32_Node_3", 24.8), daemon=True)

    t1.start()
    t2.start()
    t3.start()

    # Keyboard listener thread for live attack injection
    k_thread = threading.Thread(target=keyboard_listener, daemon=True)
    k_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping ESP32 Telemetry Node Simulator.")

if __name__ == "__main__":
    main()
