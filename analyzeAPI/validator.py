from netaddr import EUI, AddrFormatError, IPAddress, mac_unix_expanded
import scapy.all as sc

MAC_ADDRESS_LENGTH = 17

def isValidIPAddr(ip: str) -> bool:
    try:
        ip_addr = IPAddress(ip)
        return ip_addr.version == 4 or ip_addr.version == 6
    except AddrFormatError:
        return False

def isValidMacAddr(mac: str) -> bool:
    if len(mac) != MAC_ADDRESS_LENGTH: # Mac addresses are all 17 characters long
        return False
    try:
        mac_addr = EUI(mac)
        print("mac addr in isValidMacAddr =", mac_addr)
        return True
    except:
        return False

def normalizeMacAddr(mac: str) -> str:
    try:
        mac_addr = EUI(mac)
        mac_addr.dialect = mac_unix_expanded
        return str(mac_addr)
    except AddrFormatError:
        return None

def macAddrToIPAddr(pcap: sc.PacketList, macAddr: str) -> str:
    for packet in pcap:
        if sc.ARP in packet:
            if packet[sc.ARP].hwsrc == macAddr:  # If the hardware source is equal to mac address
                return packet[sc.ARP].psrc  # Return the source IP address
            elif packet[sc.ARP].hwdst == macAddr:  
                return packet[sc.ARP].pdst  

        elif sc.Ether in packet and sc.IP in packet:
            if packet[sc.Ether].src == macAddr:  # If we found the hardware source in an Ethernet packet
                return packet[sc.IP].src  # Return the source IP address
            elif packet[sc.Ether].dst == macAddr:  # Same but check destination now
                return packet[sc.IP].dst

    return None 