# Goal
The goal of this project is to give people the ability to look deeper in pcaps and explore the captured traffic. Our tool gives people the ability to upload a pcap and an ip of interest and view metrics like the amount of traffic sent by the device and where it was sent to.

## General Notes
When using the project you have the choice between using the MaxMind or RipeAtlas api for geolocation. In general we found RipeAtlas to not give quite as many results as MaxMind (i.e. MaxMind will give some locations where RipeAtlas gives nothing). This is offset by the fact that the MaxMind api requires a license key however, and limits users to 1000 requests per day at the free tier

On that note we have limited the number of IPs that are geolocated in your pcap to 20. This is to prevent throttling either API. If you would like to increase that value you can change the contstant variable `MAX_NUMBER_OF_API_REQUESTS` in geolocation.py.

Other things to note is that the RipeAtlas api seems to take a bit longer than MaxMind. Using a MAC address instead of an IP address will also cause the scripts to take a bit more time as we must first translate that MAC address into its corresponding IP in the given PCAP first.

## MaxMind api
Our project uses the MaxMind API to help with geolocation of the ip addresses. This API requires a free account with MaxMind to use (you need a license key and account ID to use it)

[Here is the documentation](https://dev.maxmind.com/geoip/geolocate-an-ip/web-services/) on the api we used. Edit the file in: `./analyzeAPI/geolocation.py` to use your own license key for the geolocation (there should be a link to create an account and get a free passkey in step 2).

## Using Docker
This is the simplest way to get up and running locally with our application. 

**IMPORTANT: Ensure you have added your own MaxMind license key and account ID in geolocation.py before following any of the next steps if you want to use the MaxMind API.**

First ensure you have docker installed, can use [this](https://docs.docker.com/engine/install/) link to find an installation for your machine.

Once the docker engine is running, run the following from the command line:

1. `docker build --tag '<image_name>' .`

2. `docker run --name '<container_name>' --detach -p 5432:5432 '<image_name>'`

If you are on Mac or something with Docker Desktop make sure the application is running before doing this. You may also need to run the image from the application for it to work.

After getting the image running all you need to do is open index.html in a web browser (or through VS Code's live server functionality). Everything should work the same from there.

## Setting up python venv
**NOTE: THIS IS UNNECESSARY IF YOU ARE USING THE DOCKER CONTAINER**

[Documentation](https://docs.python.org/3/library/venv.html)
1. `python3 -m venv /path/to/new/virtual/environment`

2. `source <venv>/bin/activate`

3. `pip install -r requirements.txt`
  - Need to uncomment the magic-bin line in requirements.txt in running on Mac or Windows
  - For Linux instead run `RUN pip install git+https://github.com/julian-r/python-magic.git`

4. `python3 app.py`

5. (Optional - if you are trying to use in production environment) Run gunicorn as a daemon (running as daemon not necessary) with this command: `gunicorn --config gunicornConfig.py wsgi:app --daemon`
    * If you run as a daemon you must use `ps aux | grep gunicorn` to find the daemon pid and kill it manually
    - Note that this is a linux command and gunicorn is configured to work in Linux enviorenments (tested on Ubuntu)

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
