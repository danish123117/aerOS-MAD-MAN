import requests
import json
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def ngsi_patch(data,entity,orion,orion_port,context, context_port): # this is fine
    """
    The function update the value on an NGSI-ld entity using patch to orion context broker
    """
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity}/attrs"
    headers = {
        'Content-Type':"application/json",
        "Link": f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
     }
    response = requests.request("PATCH", url, headers=headers, data=data)
    return response

def ngsi_get_current(ORION_HOST, ORION_PORT, ENTITY_ID, context, context_port):
    """Fetch the current state of the queue entity from Orion-LD."""
    url = f"http://{ORION_HOST}:{ORION_PORT}/ngsi-ld/v1/entities/{ENTITY_ID}?options=keyValues"
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Accept': 'application/json'
}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        #logger.info("Successfully fetched entity data.")
        return response.json()
    except requests.exceptions.RequestException as e:
        #logger.error(f"Failed to fetch entity: {e}")
        return None
    
def update_incomplete_order_list(updated_incomplete_list,updated_proc_list, ORION_HOST, ORION_PORT, ENTITY_ID, context, context_port):
    """Update the incompleteOrderList attribute in Orion-LD."""
    url = f"http://{ORION_HOST}:{ORION_PORT}/ngsi-ld/v1/entities/{ENTITY_ID}/attrs"
    headers = {
        'Content-Type':"application/json",
        "Link": f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"'
     }

    update_payload = {
        "incompleteOrderList": {
            "type": "Property",
            "value": updated_incomplete_list
        },
        "processingOrderList": {
            "type": "Property",
            "value": updated_proc_list
        }
    }

    try:
        response = requests.patch(url, json=update_payload, headers=headers)
        response.raise_for_status()
        logger.info("Successfully updated incompleteOrderList.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update entity: {e}")

