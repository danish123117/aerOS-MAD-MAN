# Order Generator

## Function
This application is the main frontend for order management At MADE CC

## Default Port
`3040`

## Environment Variables
The application requires the following environment variables:

- `ORION_LD_HOST` (default: `localhost`)
- `ORION_LD_PORT` (default: `1026`)
- `CONTEXT_HOST` (default: `localhost`)
- `CONTEXT_PORT` (default: `5051`)
- `ORION_ORDER_ENTITY` (default: `"urn:ngsi-ld:queue:queue001"`)
- `WMS_ORDER_INFO_URL` (default: <wms_login_url>)
- `WMS_USERNAME` (default: <wms_username>)
- `WMS_PASSWORD` (default: <wms_password>)
- `MS_POST_URL` (default: <wms_post_url>)


## Application Screenshot
![screenshot](App_Screenshot.png)

## First Run Setup
Before using the application, run the setup method:
`localhost:3040/setup`

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