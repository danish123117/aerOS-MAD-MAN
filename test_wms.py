import requests

# Define the URL and credentials
url = "https://made.logistics.reply.com/external/made/made-resources/auxiliary/ProductionOrder?orderNumber=PRO18701"
username = "made"
password = "Welcome.01"

# Make the GET request with Basic Authentication
response = requests.get(url, auth=(username, password))

# Check the response
if response.status_code == 200:
    print(response.json())  # Assuming the response is JSON
else:
    print("Error:", response.status_code, response.text)