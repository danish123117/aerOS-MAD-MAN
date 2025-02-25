from flask import Flask, render_template, request, jsonify
import requests
from waitress import serve
import os
from datetime import datetime, timezone
from ngsiOperations import ngsi_patch, ngsi_get_current

app = Flask(__name__)

ORION_LD_URL = os.getenv("ORION_LD_URL", "localhost")
ORION_LD_PORT = os.getenv("ORION_LD_PORT", 1026)
ORION_ORDER_ENTITY = os.getenv("ORION_ORDER_ENTITY", "urn:ngsi-ld:order:order001")
CONTEXT_URL = os.getenv("CONTEXT_URL", "localhost")
CONTEXT_PORT = os.getenv("CONTEXT_PORT", 1028)
url = f"http://{ORION_LD_URL}:{ORION_LD_PORT}/v2/entities/{ORION_ORDER_ENTITY}"

def select_orders(data, mode):
    orders = data.get("incompleteOrderList", [])
    selected = []
    total_qty = 0

    if mode == "Baseline":
        selected.append(orders[0])
    else:  # Recommendation Mode
        for order in orders:
            if total_qty + order[2] <= 8:
                selected.append(order)
                total_qty += order[2]

    return selected

def start_production(data, selected_orders):
    timestamp = datetime.now(timezone.utc).isoformat()
    for order in selected_orders:
        order.append("I")
        order.append(timestamp)
        data["processingOrderList"].append(order)

    data["incompleteOrderList"] = [o for o in data["incompleteOrderList"] if o not in selected_orders]
    return data

def complete_production(data):
    timestamp = datetime.now(timezone.utc).isoformat()
    for order in data["processingOrderList"]:
        order.append(timestamp)
        data["completedOrderList"].append(order)

    data["processingOrderList"] = []
    return data

@app.route("/")
def home():
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    return render_template("index.html", data=data)

@app.route("/start_batch", methods=["POST"])
def start_batch():
    mode = request.json.get("mode")
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    selected_orders = select_orders(data, mode)
    updated_data = start_production(data, selected_orders)
    ngsi_patch(data=updated_data,entity=ORION_ORDER_ENTITY,orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context=CONTEXT_URL, context_port=CONTEXT_PORT)
    return jsonify({"message": "Batch started!"})

@app.route("/complete_batch", methods=["POST"])
def complete_batch():
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    updated_data = complete_production(data)
    ngsi_patch(data=updated_data,entity=ORION_ORDER_ENTITY,orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context=CONTEXT_URL, context_port=CONTEXT_PORT)
    return jsonify({"message": "Batch completed!"})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=3040)
