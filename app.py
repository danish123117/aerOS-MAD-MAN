from flask import Flask, render_template, request, jsonify
import requests
from waitress import serve
import os
from datetime import datetime, timezone
from ngsiOperations.ngsildOperations import ngsi_patch, ngsi_get_current , ngsi_setup_MAD_MAN
import requests
import json
app = Flask(__name__)

ORION_LD_URL = os.getenv("ORION_LD_URL", "localhost")
ORION_LD_PORT = os.getenv("ORION_LD_PORT", 1026)
ORION_ORDER_ENTITY = os.getenv("ORION_ORDER_ENTITY", "urn:ngsi-ld:queue:queue001")
CONTEXT_URL = os.getenv("CONTEXT_URL", "localhost")
CONTEXT_PORT = os.getenv("CONTEXT_PORT", 5051)

WMS_ORDER_INFO_URL = os.getenv("WMS_ORDER_INFO_URL","https://made.logistics.reply.com/external/made/made-resources/auxiliary/ProductionOrder")# update correct one
WMS_USERNAME = os.getenv("WMS_USERNAME","made")
WMS_PASSWORD = os.getenv("WMS_PASSWORD")
WMS_POST_URL = os.getenv("MS_POST_URL","https://made.logistics.reply.com/external/made/import/createOrders")

auth_token = None

def wms_get_order_info(order_number=None):
    url = WMS_ORDER_INFO_URL
    if order_number:
        url += f"?orderNumber={order_number}"
    response = requests.get(url, auth=(WMS_USERNAME, WMS_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
def select_orders(data, mode):
    orders = data.get("incompleteOrderList", [])
    selected = []
    total_qty = 0

    if mode == "Baseline":
        selected.append(orders[0])
    else:  # Recommendation Mode  ## check if this is correct 
        for order in orders:
            if total_qty + order[2] <= 5:
                selected.append(order)
                total_qty += order[2]

    return selected , total_qty

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



def post_order_to_factory(order_qty):
    payload = json.dumps([
        {
            "item": {
            "itemNumber": "VALVOLA"
            },
            "bom": {
            "bomId": "DEMO"
            },
            "requestQty": order_qty,
        }
        ])
    response = requests.request("POST",WMS_POST_URL, data=payload, auth=(WMS_USERNAME, WMS_PASSWORD))
    if response.status_code == 200:
        return 1
    else:
        return {"error": response.text}

@app.route("/")
def home():
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    return render_template("index.html", data=data)

@app.route("/start_batch", methods=["POST"])
def start_batch():
    mode = request.json.get("mode")
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    selected_orders ,total_qty = select_orders(data, mode)
    updated_data = start_production(data, selected_orders)
    ngsi_patch(data=updated_data,entity=ORION_ORDER_ENTITY,orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context=CONTEXT_URL, context_port=CONTEXT_PORT)
    
    response = post_order_to_factory(total_qty) # logic about what to do if the post fails
    return jsonify({
        "incompleteOrderList": updated_data["incompleteOrderList"],
        "processingOrderList": updated_data["processingOrderList"],
        "completedOrderList": updated_data["completedOrderList"]
    })

@app.route("/complete_batch", methods=["POST"])
def complete_batch():
    data = ngsi_get_current(entity= ORION_ORDER_ENTITY, orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context_url=CONTEXT_URL,context_port=CONTEXT_PORT)
    updated_data = complete_production(data)
    ngsi_patch(data=updated_data,entity=ORION_ORDER_ENTITY,orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context=CONTEXT_URL, context_port=CONTEXT_PORT)
    return jsonify({
        "incompleteOrderList": updated_data["incompleteOrderList"],
        "processingOrderList": updated_data["processingOrderList"],
        "completedOrderList": updated_data["completedOrderList"]
    })

@app.route("/setup", methods=["POST"])
def setup():
    resp =ngsi_setup_MAD_MAN(orion=ORION_LD_URL,orion_port=ORION_LD_PORT,context=CONTEXT_URL,context_port=CONTEXT_PORT)
    if resp.status_code == 201:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed", "message": resp.text})

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=3040)
