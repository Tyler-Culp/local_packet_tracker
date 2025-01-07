# Goal
The goal of this project is to give people the ability to look deeper in pcaps and explore the captured traffic. Our tool gives people the ability to upload a pcap and an ip of interest and view metrics like the amount of traffic sent by the device and where it was sent to.

## MaxMind api
Our project uses the MaxMind API to help with geolocation of the ip addresses. This API requires a free account with MaxMind to use (you need a license key and account ID to use it)

[Here is the documentation](https://dev.maxmind.com/geoip/geolocate-an-ip/web-services/) on the api we used. Edit the file in: `./analyzeAPI/flaskServer/geolocation.py` to use your own license key for the geolocation (there should be a link to create an account and get a free passkey in step 2).

## Using Docker
This is the simplest way to get up and running locally with our application. Ensure you have added your own license key in geolocation.py first. 

First ensure you have docker installed, can use [this](https://docs.docker.com/engine/install/) link to find an installation for your machine.

Once the docker engine is running, run the following from the command line:

1. `docker build --tag '<image_name>' .`

2. `docker run --name '<container_name>' --detach -p 5432:5432 '<image_name>'`

If you are on Mac or something with Docker Desktop make sure the application is running before doing this. You may also need to run the image from the application for it to work.

After getting the image running all you need to do is open index.html in a web browser (or through VS Code's live server functionality). Everything should work the same from there.

## Using the precreated venv
**NOTE: THIS IS UNNECESSARY IF YOU ARE USING THE DOCKER CONTAINER**
1. `source analyzeAPI/flaskServer/venv/bin/activate`

2. `python3 analyzeAPI/flaskServer/app.py`

## Setting up python venv
**NOTE: THIS IS UNNECESSARY IF YOU ARE USING THE DOCKER CONTAINER**

[Documentation](https://docs.python.org/3/library/venv.html)
Note: May have to redo this occassionally, had issues when pulling new code from main

1. `python3 -m venv /path/to/new/virtual/environment`

2. `source <venv>/bin/activate`

3. `pip install -r requirements.txt`

4. `python3 app.py`

5. (Optional - if you are trying to use in production enviorenment) Run gunicorn as a daemon (running as daemon not necessary) with this command: `gunicorn --config gunicornConfig.py wsgi:app --daemon`
    * If you run as a daemon you must use `ps aux | grep gunicorn` to find the daemon pid and kill it manually, note that this is a linux command

## Gunicorn service file

1. sudo vim /etc/systemd/system/gunicorn.service

```
[Unit]
Description=Gunicorn instance to serve my app
After=network.target

[Service]
User=tyler
Group=www-data
WorkingDirectory=/var/www/pcapTracker
Environment="PATH=/var/www/pcapTracker/bin"
ExecStart=/var/www/pcapTracker/bin/gunicorn --config gunicornConfig.py wsgi:app

[Install]
WantedBy=multi-user.target
```