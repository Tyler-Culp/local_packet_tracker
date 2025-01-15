import collections
import threading
import scapy.all as sc
from datetime import datetime
import socket
from concurrent.futures import ThreadPoolExecutor

class PacketChecker:
    def __init__(self, IP: str, port: int, packet: sc.Packet, direction: str):
        self.IP = IP
        self.port = port
        self.packet = packet
        self.direction = direction
    
    def withDirecton(self, direction):
        self.direction = direction
    
    def isPacketValid(self) -> bool:
        topLevelCheck = (sc.IP in self.packet) and (sc.TCP in self.packet) and (self.packet.dport == self.port or self.packet.sport == self.port)
        if not topLevelCheck: return False
        match self.direction:
            case "sending":
                return topLevelCheck and (self.packet[sc.IP].src == self.IP)
            case "receiving":
                return topLevelCheck and (self.packet[sc.IP].dst == self.IP)

def processPacket(packet, pcapData: dict, IP: str, port: int, startTime: datetime):
    sendingPacketChecker = PacketChecker(IP, port, packet, "sending")
    receivingPacketChecker = PacketChecker(IP, port, packet, "receiving")

    if sendingPacketChecker.isPacketValid():
        currTime = datetime.fromtimestamp(float(packet.time))
        relativeTime = currTime - startTime
        relativeTimeSeconds = relativeTime.seconds

        destIP = packet[sc.IP].dst
        try:
            destIP = socket.gethostbyaddr(destIP)[0]
        except:
            destIP = destIP

        with threading.Lock():  # Ensure thread-safety when updating shared data
            pcapData["sentTime"][relativeTimeSeconds] += 1
            pcapData["sentIP"][destIP] += 1
            pcapData["sentSize"][relativeTimeSeconds] += len(packet.payload)

    elif receivingPacketChecker.isPacketValid():
        currTime = datetime.fromtimestamp(float(packet.time))
        relativeTime = currTime - startTime
        relativeTimeSeconds = relativeTime.seconds

        srcIP = packet[sc.IP].src
        try:
            srcIP = socket.gethostbyaddr(srcIP)[0]
        except:
            srcIP = srcIP

        with threading.Lock():  # Ensure thread-safety when updating shared data
            pcapData["receivedTime"][relativeTimeSeconds] += 1
            pcapData["receivedIP"][srcIP] += 1


def getPcapData(pcap: sc.PacketList, IP: str, port: int) -> dict:
    pcapData = {
        "sentTime": collections.defaultdict(int),
        "receivedTime": collections.defaultdict(int),
        "sentIP": collections.defaultdict(int),
        "receivedIP": collections.defaultdict(int),
        "sentSize": collections.defaultdict(int),
    }
    startTime = datetime.fromtimestamp(float(pcap[0].time))

    with ThreadPoolExecutor() as executor:
        for packet in pcap:
            executor.submit(processPacket, packet, pcapData, IP, port, startTime)

    return pcapData
            
