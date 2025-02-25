import requests
import json

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

def ngsi_get_current(entity, orion,orion_port,context_url,context_port): # this should be ok
    url = f"http://{orion}:{orion_port}/ngsi-ld/v1/entities/{entity}/?options=keyValues"

    payload = {}
    headers = {
  'Link': f'<http://{context_url}:{context_port}/ngsi-context.jsonld>; rel="http://www.w3.org/ns/json-ld#context"; type="application/ld+json"',
  'Accept': 'application/json'
}

    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()




