def makeMap(pcap: sc.PacketList, IP: str, port:int) -> dict:
    pcapData = { 
        "sentTime": {},
        "receivedTime": {},
        "sentIP": {},
        "receivedIP": {},
        "sentSize": {},
    }
    startTime = datetime.fromtimestamp(float(pcap[0].time))

    for packet in pcap:
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

            packetNumberSentTimesMap = pcapData["sentTime"]
            packetIPsSentToMap = pcapData["sentIP"]
            packetSizeSentMap = pcapData["sentSize"]

            packetNumberSentTimesMap[relativeTimeSeconds] = packetNumberSentTimesMap.get(relativeTimeSeconds, 0) + 1

            packetIPsSentToMap[destIP] = packetIPsSentToMap.get(destIP, 0) + 1

            packetSizeSentMap[relativeTimeSeconds] = packetSizeSentMap.get(relativeTimeSeconds, 0) + len(packet.payload)

        if receivingPacketChecker.isPacketValid():
            currTime = datetime.fromtimestamp(float(packet.time))
            relativeTime = currTime - startTime
            relativeTimeSeconds = relativeTime.seconds

            srcIP = packet[sc.IP].src
            try:
                srcIP = socket.gethostbyaddr(srcIP)[0]
            except:
                srcIP = srcIP

            packetNumberReceivedMap = pcapData["receivedTime"]
            packetIPsReceivedFromMap = pcapData["receivedIP"]

            packetNumberReceivedMap[relativeTimeSeconds] = packetNumberReceivedMap.get(relativeTimeSeconds, 0) + 1

            packetIPsReceivedFromMap[srcIP] = packetIPsReceivedFromMap.get(srcIP, 0) + 1
            
    return pcapData

def getSentTimes(pcap: sc.PacketList, IP: str, port:int) -> dict:
    startTime = datetime.fromtimestamp(float(pcap[0].time))
    packetSentTimes = {}

    for packet in pcap:
        packetChecker = PacketChecker(IP, port, packet, "sending")
        if packetChecker.isPacketValid():
            currTime = datetime.fromtimestamp(float(packet.time))
            relativeTime = currTime - startTime
            relativeTimeSeconds = relativeTime.seconds

            packetSentTimes[relativeTimeSeconds] = packetSentTimes.get(relativeTimeSeconds, 0) + 1

    return packetSentTimes

def getReceivedTimes(pcap: sc.PacketList, IP: str, port: int) -> dict:
    startTime = datetime.fromtimestamp(float(pcap[0].time))
    packetReceivedTimes = {}

    for packet in pcap:
        packetChecker = PacketChecker(IP, port, packet, "receiving")
        if packetChecker.isPacketValid():
            currTime = datetime.fromtimestamp(float(packet.time))
            relativeTime = currTime - startTime
            relativeTimeSeconds = relativeTime.seconds

            packetReceivedTimes[relativeTimeSeconds] = packetReceivedTimes.get(relativeTimeSeconds, 0) + 1

    return packetReceivedTimes

def getSentIPs(pcap: sc.PacketList, IP: str, port: int) -> dict:
    sentIPCounts = {}

    for packet in pcap:
        packetChecker = PacketChecker(IP, port, packet, "sending")
        if packetChecker.isPacketValid():
            destIP = packet[sc.IP].dst
            try:
                destIP = socket.gethostbyaddr(destIP)[0]
            except:
                pass
            sentIPCounts[destIP] = sentIPCounts.get(destIP, 0) + 1

    return sentIPCounts

def getReceivedIPs(pcap: sc.PacketList, IP: str, port: int) -> dict:
    receivedIPCounts = {}

    for packet in pcap:
        packetChecker = PacketChecker(IP, port, packet, "receiving")
        if packetChecker.isPacketValid():
            srcIP = packet[sc.IP].src
            try:
                srcIP = socket.gethostbyaddr(srcIP)[0]
            except:
                pass
            receivedIPCounts[srcIP] = receivedIPCounts.get(srcIP, 0) + 1

    return receivedIPCounts

def getTimeVSPacketSizeSent(pcap: sc.PacketList, IP: str, port: int) -> dict:
    startTime = datetime.fromtimestamp(float(pcap[0].time))
    time_vs_packetSizeMap = {}

    for packet in pcap:
        packetChecker = PacketChecker(IP, port, packet, "sending")
        if packetChecker.isPacketValid():
            currTime = datetime.fromtimestamp(float(packet.time))
            relativeTime = currTime - startTime
            relativeTimeSeconds = relativeTime.seconds

            time_vs_packetSizeMap[relativeTimeSeconds] = time_vs_packetSizeMap.get(relativeTimeSeconds, 0) + len(packet.payload)

    return time_vs_packetSizeMap