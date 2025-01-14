import ipaddress
import socket
import geoip2.webservice
import folium
import io

# MaxMind documentation for api key
# https://dev.maxmind.com/geoip/geolocate-an-ip/web-services/

license_key = '<Your_license_key>'
account_id = 1234567
client = geoip2.webservice.Client(account_id, license_key, host='geolite.info')

def geolocate_IP_RipeAtlas(ip):
    try:
        # First check if the IP is a valid IPv4 or IPv6 address
        ipaddress.ip_address(ip)
        response = client.city(ip)
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
            response = client.city(resolved_ip)
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

def geolocate_IP_MaxMind(ip):
        try:
            # First check if the IP is a valid IPv4 or IPv6 address
            ipaddress.ip_address(ip)
            response = client.city(ip)
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
                response = client.city(resolved_ip)
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

def getSentIpLocations(map_data):
    # Geolocate sent IPs
    seen_ips = set()
    location_counts = {}
    for ip in map_data["sentIP"]:
        # Only geolocate the first 20 ips before breaking to not get API throttled
        # Get 1000 requests a day so this lets you run program 50 times at minimum
        if len(seen_ips) > 20: break 
        seen_ips.add(ip)
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