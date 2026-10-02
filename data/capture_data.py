# data/capture_data.py — test captures with sample summaries, attached to a user in seed.py.

from models.capture import CaptureModel


def create_test_captures(user):
    return [
        CaptureModel(
            filename="office-traffic.pcap",
            packet_count=1284,
            duration=42.6,
            summary={
                "packet_count": 1284,
                "duration": 42.6,
                "total_bytes": 2200000,
                "protocols": {"tcp": 796, "udp": 360, "icmp": 128},
                "top_sources": [["10.0.0.4", 820], ["10.0.0.7", 260]],
                "top_destinations": [["142.250.72.14", 540], ["8.8.8.8", 300]],
            },
            user=user,
        ),
        CaptureModel(
            filename="dns-lookups.pcap",
            packet_count=642,
            duration=18.2,
            summary={
                "packet_count": 642,
                "duration": 18.2,
                "total_bytes": 410000,
                "protocols": {"udp": 600, "tcp": 42},
                "top_sources": [["10.0.0.2", 600]],
                "top_destinations": [["1.1.1.1", 600]],
            },
            user=user,
        ),
    ]