import requests
import json
def ngsi_create_entity(d,orion,orion_port,context,context_port):#updates latest values
    url = f'http://{orion}:{orion_port}/ngsi-ld/v1/entities/'
    #url = 'http://localhost:1026/ngsi-ld/v1/entityOperations/create'
    headers = {
  'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Content-Type': 'application/json'
}
    payload = json.dumps(d)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response

def ngsi_setup_MAD_MAN(orion,orion_port,context,context_port):
    data =   {
    "id": "urn:ngsi-ld:queue:queue001",
    "type": "queue",
    "incompleteOrderList": [],
    "processingOrderList":[],
    "processingOrderListOutsource":[],
    "completedOrderList":[]

    }
    payload = data
    resp= ngsi_create_entity(payload,orion,orion_port,context,context_port)
    return resp


def ngsi_setup_DOG(orion,orion_port,context,context_port):
    data = {
    "id": "urn:ngsi-ld:extOrder:order001",
    "type": "extOrder",
    "timestamp": "2024-01-16T17:50:07.5870Z",
    "orderId": "test",
    "orderQuantity":0 } 

    payload = data
    resp= ngsi_create_entity(payload,orion,orion_port,context,context_port)
    return resp

def ngsi_subscribe_DOG(orion,orion_port,context,context_port):
    url = f'http://{orion}:{orion_port}/ngsi-ld/v1/subscriptions/'
    headers = {}
    return 0

def ngsi_subscribe_DOG(orion, orion_port, context, context_port, notify_endpoint):
    url = f'http://{orion}:{orion_port}/ngsi-ld/v1/subscriptions/'

    headers = {
        'Link': f'<http://{context}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
        'Content-Type': 'application/json'
    }

    subscription = {
        "id": "urn:ngsi-ld:Subscription:extOrderAllAttributesFull",
        "type": "Subscription",
        "entities": [
            {
                "id": "urn:ngsi-ld:extOrder:order001",
                "type": "extOrder"
            }
        ],
        "notification": {
            "attributes": ["orderId", "orderQuantity", "timestamp"],  # Ensures all attributes are included
            "endpoint": {
                "uri": notify_endpoint,
                "accept": "application/json"
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(subscription))
    return response


#Done