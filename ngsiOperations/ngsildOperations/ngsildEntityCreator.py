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


#Done