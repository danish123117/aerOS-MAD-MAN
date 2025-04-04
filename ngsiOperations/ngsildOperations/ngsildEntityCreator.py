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
    "incompleteOrderList": {"type": "Property","value": []},
    "processingOrderList": {"type": "Property","value": []},
    "completedOrderList": {"type": "Property","value": []},
    "incompleteOrderListOutsource": {"type": "Property","value": []},
    "completedOrderList": {"type": "Property","value": []}

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


#Done