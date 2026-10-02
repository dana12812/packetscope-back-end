# lib/pcap_parser.py — reads a .pcap with Scapy and returns a traffic summary.

from collections import Counter
from scapy.all import rdpcap, IP, IPv6, TCP, UDP, ICMP, ARP

# Well-known ports → friendly service names (extend this anytime)
PORT_SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 67: "dhcp", 68: "dhcp", 80: "http", 110: "pop3",
    123: "ntp", 143: "imap", 443: "https", 445: "smb",
    3306: "mysql", 3389: "rdp", 5432: "postgres", 8080: "http-alt",
}


def _protocol_of(pkt):
    if pkt.haslayer(ARP):
        return "arp"
    if pkt.haslayer(TCP):
        return "tcp"
    if pkt.haslayer(UDP):
        return "udp"
    if pkt.haslayer(ICMP):
        return "icmp"
    return "other"


def _service_name(port):
    return PORT_SERVICES.get(port, str(port))


def parse_pcap(path, top=5):
    packets = rdpcap(path)

    protocols = Counter()
    services = Counter()
    sources = Counter()
    destinations = Counter()
    total_bytes = 0
    sizes = []
    timestamps = []

    for pkt in packets:
        protocols[_protocol_of(pkt)] += 1
        size = len(pkt)
        total_bytes += size
        sizes.append(size)
        timestamps.append(float(pkt.time))

        if pkt.haslayer(IP):
            sources[pkt[IP].src] += 1
            destinations[pkt[IP].dst] += 1
        elif pkt.haslayer(IPv6):
            sources[pkt[IPv6].src] += 1
            destinations[pkt[IPv6].dst] += 1

        # Note the destination service/port for TCP and UDP traffic
        if pkt.haslayer(TCP):
            services[_service_name(pkt[TCP].dport)] += 1
        elif pkt.haslayer(UDP):
            services[_service_name(pkt[UDP].dport)] += 1

    duration = (max(timestamps) - min(timestamps)) if timestamps else 0.0

    packet_sizes = {
        "min": min(sizes) if sizes else 0,
        "max": max(sizes) if sizes else 0,
        "avg": round(sum(sizes) / len(sizes), 1) if sizes else 0,
    }

    return {
        "packet_count": len(packets),
        "duration": round(duration, 3),
        "total_bytes": total_bytes,
        "packet_sizes": packet_sizes,
        "protocols": dict(protocols),
        "top_services": services.most_common(top),
        "top_sources": sources.most_common(top),
        "top_destinations": destinations.most_common(top),
    }