from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import base64
import scapy.all as sc
import magic
from analyzeIPs import getPcapData
from validator import isValidIPAddr, isValidMacAddr, normalizeMacAddr, macAddrToIPAddr
from createGraph import GraphBuilder, makeGraphObject
from geolocation import getSentIpLocations, generateMap 
import geoip2.webservice

app = Flask(__name__)
CORS(app)

app.config ['MAX_CONTENT_LENGTH'] = 100*1024*1024 #100 MB

def createErrorResponse(errorMsg: str):
    response = {}
    response["error"] = errorMsg
    response = jsonify(response)

    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")

    return response

def validate_mime_type(file):
    mime = magic.Magic(mime = True)
    mime_type = mime.from_buffer(file.stream.read(1024)) # Read first 1024 Bytes
    file.stream.seek(0)
    return mime_type in ['application/vnd.tcpdump.pcap', 'application/octet-stream']

def validate_magic_number(file):
    magic_number = file.read(4)
    file.seek(0)
    return magic_number in [b'\xa1\xb2\xc3\xd4', b'\x0a\x0d\x0d\x0a']


@app.route("/", methods=["OPTIONS"])
def options():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    return response

@app.route("/", methods=["POST"])
def analyze_pcap():
    # Get IP and file from form data
    ip = request.form.get("ip")
    file = request.files.get("file")

    if not file:
        errorResponse = createErrorResponse("No file received")
        return errorResponse, 410
        
    if not (file.filename.endswith('.pcap') or file.filename.endswith('.pcapng')):
        errorResponse = createErrorResponse("Not a .pcap or .pcapng file")
        return errorResponse, 411
    
    if not validate_magic_number(file.stream):
        errorResponse = createErrorResponse("Something is wrong with the .pcap file, perhaps the extension of another file type was changed")
        return errorResponse, 412
    
    try:
        # Parse the PCAP file with Scapy (convert file to scapy.PacketList)
        pcap = sc.rdpcap(file)
    except Exception as e:
        errorResponse = createErrorResponse("Error with pcap scripts")
        return errorResponse, 413
    
    print("ip = ", ip)
    print("valid IP = ", isValidIPAddr(ip))
    print("valid mac = ", isValidMacAddr(ip))
    if (not isValidIPAddr(ip)):
        if (not isValidMacAddr(ip)):
            errorResponse = createErrorResponse("invalid IP or MAC address given")
            return errorResponse, 414
        else:
            mac = normalizeMacAddr(ip) # In this case the user gave us a mac addr, not IP
            ip = macAddrToIPAddr(pcap, mac)

    # Analyze the PCAP file
    pcapData = getPcapData(pcap, ip, 443)  # Example with HTTPS port

    encodedGeographicMaps = None
    mapError = None
    try:
        geographicMaps = generateMap(getSentIpLocations(pcapData))
        encodedGeographicMaps = base64.b64encode(geographicMaps.getvalue()).decode('utf-8')
    except geoip2.errors.AuthenticationError:
        print("Authentication for the geoip2 service has failed. Please check your account ID and license key.")
        mapError = "Authentication for the geoip2 service has failed. Please check your account ID and license key."
    except Exception as e:
        print(f"Unexpected error during GeoIP client connection: {e}")
        mapError = f"Unexpected error during GeoIP client connection: {e}"

    # Below code was used to create matplotlib graphs, became unnecessary when we switched to generating graphs with D3
    # Left this as a template in case people who are better with matplotlib than us do want to use it

    # IPGraphImages = []
    # for key in pcapData:
    #     print("\nInformation for new graph")
    #     print("\nThis is the key " + key)
    #     if key == "sentTime":
    #         img = GraphBuilder(data=pcapData[key]).withTitle("Sent Packet Times").withXTitle("Time").withYTitle("Number of Packets").build()

    # Convert the image to a base64 string
    # img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    # graph_images.append(img_base64)

    graphObjects = []
    for key in pcapData:
        if key == "sentTime":
            builder = GraphBuilder(data=pcapData[key]).withTitle("Sent Packet Times").withXTitle("Time").withYTitle("Number of Packets")
        elif key == "receivedTime":
            builder = GraphBuilder(data=pcapData[key]).withTitle("Received Packet Times").withXTitle("Time").withYTitle("Number of Packets")
        elif key == "sentIP":
            builder = GraphBuilder(data=pcapData[key]).withTitle("IPs / Hostnames Traffic was Sent To").withXTitle("IPs / Hostnames").withYTitle("Number of Packets")
        elif key == "receivedIP":
            builder = GraphBuilder(data=pcapData[key]).withTitle("IPs / Hostnames Traffic was Received From").withXTitle("IPs / Hostnames").withYTitle("Number of Packets")
        elif key == "sentSize":
            builder = GraphBuilder(data=pcapData[key]).withTitle("Average Size in Bytes of Packets Sent Over Time").withXTitle("Time").withYTitle("Packet Sizes (bytes)")
        
        if builder:
            graphObjects.append(makeGraphObject(builder))

    # Create the response
    if mapError is None:
        response = jsonify({
            "graphObjects": graphObjects,
            "map": encodedGeographicMaps,
        })
    else:
        response = jsonify({
            "graphObjects": graphObjects,
            "mapError": mapError,
        })
    
    # Set CORS headers
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")


    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5432, debug=True)
