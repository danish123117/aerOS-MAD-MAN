from flask import Flask, render_template, request, jsonify
import requests
from waitress import serve
import os
from datetime import datetime, timezone
from ngsiOperations.ngsildOperations.ngsildCrudOperations import *
from ngsiOperations.ngsildOperations.ngsildEntityCreator import *
import requests
import json
from datetime import datetime, timezone
import logging
from orionClient.orion_client import *



logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
app = Flask(__name__)

global in_process_list
in_process_list = []


ORION_LD_URL = os.getenv("ORION_LD_URL", "localhost")
ORION_LD_PORT = os.getenv("ORION_LD_PORT", 1026)
ORION_QUEUE_ENTITY = os.getenv("ORION_QUEUE_ENTITY", "urn:ngsi-ld:queue:queue001")
CONTEXT_URL = os.getenv("CONTEXT_URL", "context")
CONTEXT_PORT = os.getenv("CONTEXT_PORT", 5051)

WMS_ORDER_INFO_URL = os.getenv("WMS_ORDER_INFO_URL","https://made.logistics.reply.com/external/made/made-resources/auxiliary/ProductionOrder")# update correct one
WMS_USERNAME = os.getenv("WMS_USERNAME","made")
WMS_PASSWORD = os.getenv("WMS_PASSWORD")
WMS_POST_URL = os.getenv("WMS_POST_URL","https://made.logistics.reply.com/external/made/import/createOrders")

NOTIFY_URL = os.getenv("NOTIFY_URL", "localhost")
NOTIFY_PORT = os.getenv("NOTIFY_PORT", 3040)

auth_token = None

def orderQuantity(order_list):
    order_qty = 0
    for order in order_list:
        qty = order.get("orderQuantity")
        if isinstance(qty, (int, float)):
            order_qty += qty
        else:
            logger.warning(f"Order {order.get('id')} is missing 'requestQty' or it is not a number.")
            continue
    return order_qty


def wms_get_order_info(order_number=None):
    url = WMS_ORDER_INFO_URL
    if order_number:
        url += f"?orderNumber={order_number}"
    response = requests.get(url, auth=(WMS_USERNAME, WMS_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
def complete_production(data): 
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-2]
    
    # Initialize completedOrderList if it doesn't exist
    if "completedOrderList" not in data:
        data["completedOrderList"] = {"type": "Property", "value": []}
    elif not isinstance(data["completedOrderList"], dict):
        data["completedOrderList"] = {"type": "Property", "value": []}
    elif "value" not in data["completedOrderList"]:
        data["completedOrderList"]["value"] = []
    
    # Get processing orders
    processing_orders = data.get("processingOrderList", {}).get("value", [])
    
    # Add timestamp and move to completed orders
    for order in processing_orders:
        # Make sure order is a list
        if not isinstance(order, list):
            order = [order]
        
        # Make a copy to avoid modifying the original
        order_copy = order.copy()
        order_copy.append(timestamp)  # Add completion timestamp
        
        # Add the completed order to the completed list
        data["completedOrderList"]["value"].append(order_copy)

    # Clear processing order list
    data["processingOrderList"]["value"] = []
    
    return data
# Function to post order to factory
def post_order_to_factory(order_qty):
    payload = json.dumps([
        {
            "item": {"itemNumber": "VALVOLA"},
            "bom": {"bomId": "DEMO"},
            "requestQty": order_qty,
        }
    ])
    response = requests.post(WMS_POST_URL, data=payload, auth=(WMS_USERNAME, WMS_PASSWORD))
    return 1 if response.status_code == 200 else {"error": response.text}



@app.route("/")
def home():
    incomplete_orders, processing_orders, completed_orders = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    return render_template("index.html", incomplete_orders=incomplete_orders, processing_orders=processing_orders, completed_orders=completed_orders)

@app.route("/start_production", methods=["POST"])
def start_production():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "Baseline")
    #mode ="Baseline"
    if mode == "Baseline": 
        n=2
    else: 
        n=6

    incomplete_orders, _, _ = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    print(f"Number of incomplete orders: {len(incomplete_orders)}")
    if len(incomplete_orders) != 0:
        for i in range(n):
            if orderQuantity(incomplete_orders[:i+1]) <= n: 
                print(f"Processing order {i+1} with quantity {orderQuantity(incomplete_orders[:i+1])}")
                continue
            else:
                break
        in_process_list = incomplete_orders[:i]
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-2]
        response_patch =update_processing_order_list(in_process_list, ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT,timestamp)
        # response_factory = post_order_to_factory(orderQuantity(in_process_list))
        # if response_patch and response_factory:
        #     return jsonify({"success": True})
        # else:
        #     return jsonify({"success": False})
        if response_patch:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    else:
        return jsonify({"Status": "No orders to process"})



@app.route("/complete_production", methods=["POST"])
def complete_production():
    _, in_process_list, _ = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    if in_process_list:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-2]
        response = update_complete_order_list(in_process_list, ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT,timestamp)
        if response:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    else:
        return jsonify({"Status": "No orders to complete"})
  

@app.route('/get_orders', methods=['GET'])# Done
def get_order():
    incomplete_orders, processing_orders, comleted_orders = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    return jsonify({"incomplete_orders": incomplete_orders, "processing_orders": processing_orders, "completed_orders": comleted_orders})

@app.route('/get_completed_orders', methods=['GET']) # Done
def get_order_info():
    _, _, comleted_orders = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    return jsonify({"completed_orders": comleted_orders})

@app.route('/history', methods=['GET'])#
def history():
    _, _, comleted_orders = extract_entity_data(ORION_LD_URL, ORION_LD_PORT, CONTEXT_URL, CONTEXT_PORT, ENTITY_TYPE="Order")
    return render_template("history.html", completed_orders=comleted_orders)

@app.route('/setup')
def setup():
    notify_endpoint_update = f"http://{NOTIFY_URL}:{NOTIFY_PORT}/update"
    notify_endpoint_create = f"http://{NOTIFY_URL}:{NOTIFY_PORT}/create"
    update_status = ngsi_subscribe_status_update(ORION_LD_URL,ORION_LD_PORT,CONTEXT_URL,CONTEXT_PORT,notify_endpoint=notify_endpoint_update)
    subscribe_status = ngsi_subscribe_creation(ORION_LD_URL,ORION_LD_PORT,CONTEXT_URL,CONTEXT_PORT,notify_endpoint=notify_endpoint_create)
       
    if update_status is None or subscribe_status is None:
        return "An error occurred while setting up.", 500  # Return a 500 error with a message

    else: 
        return "ok", 204
    # optional now

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3040,debug=True)
    #serve(app, host="0.0.0.0", port=3040)