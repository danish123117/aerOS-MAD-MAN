# Order Generator

## Function
This application generates orders with constant standard deviations and mean values and sends them to the Orion-LD context broker.

## Default Port
`3020`

## Environment Variables
The application requires the following environment variables:

- `ORION_LD_HOST` (default: `localhost`)
- `ORION_LD_PORT` (default: `1026`)
- `CONTEXT_HOST` (default: `localhost`)
- `CONTEXT_PORT` (default: `5051`)
- `NOTIFY_HOST` (default: `localhost`)
- `NOTIFY_PORT` (default: `3030`)

## Application Screenshot
![screenshot](Application Images/App Screenshot.png)

## Functionality
- Creates an entity for the generated order: `urn:ngsi-ld:extOrder:order001`
- Subscribes to this entity to notify the persistor about changes in its values.
- Every time a new order is generated, a notification is sent to the persistor component, which updates the relevant entity in Orion-LD.

## First Run Setup
Before using the application, run the setup method:
`localhost:3020/setup`

## Usage
To start, pull the repo from GitHub and run the following commands:

```sh
$ py -m venv .venv
$ pip install -r requirements.txt
$ py app.py
```
## Access to app
To start type the following in any browser
`localhost:3020`

## Running from docker images
Use following command with the necessary changes to the environment variables as per actual deployment scenario

```sh
$ docker run -p 3020:3020 -e ORION_LD_HOST=<host> -e ORION_LD_PORT=<port> -e CONTEXT_HOST=<host> -e CONTEXT_PORT=<port> -e NOTIFY_HOST=<host> -e NOTIFY_PORT=<port> danny0117/aeros-dog:1.0.0
```