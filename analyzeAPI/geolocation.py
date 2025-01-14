import ipaddress
import socket
import geoip2.webservice
import folium
import io
import requests

MAX_NUMBER_OF_API_REQUESTS = 20

# MaxMind documentation for api key
# https://dev.maxmind.com/geoip/geolocate-an-ip/web-services/

MaxMind_license_key = '<Your_license_key>'
MaxMind_account_id = 1234567
MaxMind_client = geoip2.webservice.Client(MaxMind_account_id, MaxMind_license_key, host='geolite.info')

# Does requests one by one but can be optimized to do them all at once
# Ripe atlas documentation: https://ipmap.ripe.net/  https://ipmap.ripe.net/docs/02.api-reference/#locate 
def geolocate_IP_RipeAtlas(ip):
    print("Using RipeAtlas with hostname", ip)
    try:
        ip = socket.gethostbyname(ip)
        print("ip address =", ip)
        res = requests.get(f"https://ipmap-api.ripe.net/v1/locate/{ip}/best")
        js = res.json()
        location = js.get("location")
        return {
                "city": location.get("cityName"),
                "country": location.get("countryName"),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude")
            }
    except:
        return {"city": "Unknown", "country": "Unknown", "latitude": None, "longitude": None}

def geolocate_IP_MaxMind(ip):
        try:
            # First check if the IP is a valid IPv4 or IPv6 address
            ipaddress.ip_address(ip)
            response = MaxMind_client.city(ip)
            return {
                "city": response.city.name,
                "country": response.country.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude
            }
        except ValueError:
            # If it's not a valid IP address, try to resolve it as a hostname
            try:
                resolved_ip = socket.gethostbyname(ip)
                response = MaxMind_client.city(resolved_ip)
                return {
                    "city": response.city.name,
                    "country": response.country.name,
                    "latitude": response.location.latitude,
                    "longitude": response.location.longitude
                }
            except (socket.gaierror, geoip2.errors.AddressNotFoundError):
                return {"city": "Unknown", "country": "Unknown", "latitude": None, "longitude": None}
        except geoip2.errors.AddressNotFoundError:
            return {"city": "Unknown", "country": "Unknown", "latitude": None, "longitude": None}

def getSentIpLocations(map_data, api):
    # Geolocate sent IPs
    seen_ips = set()
    location_counts = {}
    for ip in map_data["sentIP"]:
        # Only geolocate the first 20 ips before breaking to not get API throttled
        # Get 1000 requests a day so this lets you run program 50 times at minimum
        if len(seen_ips) > MAX_NUMBER_OF_API_REQUESTS: break 
        seen_ips.add(ip)
        location = None
        if api == "MaxMind":
            location = geolocate_IP_MaxMind(ip)
        elif api == "RipeAtlas":
            location = geolocate_IP_RipeAtlas(ip)
        else:
            print("Error, unknown api given")
            break
        if location["latitude"] and location["longitude"]:
            loc_key = (location["latitude"], location["longitude"])
            if loc_key in location_counts:
                location_counts[loc_key]["count"] += 1
                location_counts[loc_key]["ips"].add(ip)  # Add IP to the set
            else:
                location_counts[loc_key] = {
                    "count": 1,
                    "city": location["city"],
                    "country": location["country"],
                    "ips": {ip}  # Initialize set with the current IP
                }
    return location_counts

def getReceivedIpLocations(map_data):
    # Geolocate received IPs
    location_counts = {}
    for ip in map_data["receivedIP"]:
        location = geolocate_IP_MaxMind(ip)
        if location["latitude"] and location["longitude"]:
            loc_key = (location["latitude"], location["longitude"])
            if loc_key in location_counts:
                location_counts[loc_key]["count"] += 1
                location_counts[loc_key]["ips"].add(ip)  # Add IP to the set
            else:
                location_counts[loc_key] = {
                    "count": 1,
                    "city": location["city"],
                    "country": location["country"],
                    "ips": {ip}  # Initialize set with the current IP
                }
    return location_counts

def generateMap(location_counts):
    # Generate map visualization for geolocated IPs
    m = folium.Map(location=[0, 0], zoom_start=2)

    for loc_key, info in location_counts.items():
        latitude, longitude = loc_key

        # Convert the set of IPs to a comma-separated
        totalIPs = "<ul>"
        for currIp in info["ips"]:
            totalIPs += f"<li>{currIp}</li>"
        totalIPs += "</ul>"

        popup_text = (f"City: {info['city']}<br>"
                      f"Country: {info['country']}<br>"
                      f"Number of different IPs in this location: {info['count']} IPs<br>"
                      f"IPs: {totalIPs}")
        folium.Marker(
            location=[latitude, longitude],
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Save the map
    map_output = io.BytesIO()
    m.save(map_output, close_file=False)
    map_output.seek(0)
    return map_output