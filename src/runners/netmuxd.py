import plistlib
import struct
import asyncio
import requests
import os

SERVICE_NAME = "apple-mobdev2"
SERVICE_PROTOCOL = "tcp"
USBMUXD_ADDRESS = os.getenv("USBMUXD_SOCKET_ADDRESS", "/var/run/usbmuxd")


async def connect():
    if USBMUXD_ADDRESS.startswith("/"):  # Likely a Unix socket
        reader, writer = await asyncio.open_unix_connection(USBMUXD_ADDRESS)
    else:  # Assume it's a TCP address in the form "host:port"
        host, port = USBMUXD_ADDRESS.rsplit(":", 1)
        reader, writer = await asyncio.open_connection(host, int(port))

    return reader, writer


class RawPacket:
    def __init__(self, plist, version, message, tag):
        self.plist = plist
        self.version = version
        self.message = message
        self.tag = tag
        self.size = 16 + len(self.plist_to_bytes())

    def plist_to_bytes(self):
        """Converts the plist dictionary to XML bytes."""
        return plistlib.dumps(self.plist)

    def to_bytes(self):
        """Converts the RawPacket to bytes."""
        packet = bytearray()
        packet.extend(struct.pack("<I", self.size))  # size (little-endian)
        packet.extend(struct.pack("<I", self.version))  # version (little-endian)
        packet.extend(struct.pack("<I", self.message))  # message (little-endian)
        packet.extend(struct.pack("<I", self.tag))  # tag (little-endian)
        packet.extend(self.plist_to_bytes())  # plist bytes
        return bytes(packet)

    @staticmethod
    def from_bytes(data):
        """Parses bytes into a RawPacket."""
        if len(data) < 16:
            raise ValueError("Incomplete packet header")

        size, version, message, tag = struct.unpack("<IIII", data[:16])
        plist_bytes = data[16:size]
        plist = plistlib.loads(plist_bytes)

        return RawPacket(plist, version, message, tag)


async def remove_device(udid):
    try:
        reader, writer = await connect()
    except Exception as e:
        print(f"[ERROR] Failed to connect to netmuxd: {str(e)}")
        return

    # Create the plist dictionary for the request
    request = {
        "MessageType": "RemoveDevice",
        "DeviceID": udid,
    }

    # Create the RawPacket with the specified fields
    raw_packet = RawPacket(request, version=69, message=69, tag=69)
    request_bytes = raw_packet.to_bytes()

    try:
        writer.write(request_bytes)
        await writer.drain()
    except Exception as e:
        print(f"[ERROR] Failed to send remove device request: {str(e)}")
    finally:
        writer.close()
        await writer.wait_closed()


async def add_device(ip, udid):
    try:
        reader, writer = await connect()
    except Exception as e:
        print("Could not connect to netmuxd socket, is it running? Error: %s", e)
        return False

    # Create the plist dictionary for the request
    request = {
        "MessageType": "AddDevice",
        "ConnectionType": "Network",
        "ServiceName": f"_{SERVICE_NAME}._{SERVICE_PROTOCOL}.local",
        "IPAddress": str(ip),
        "DeviceID": udid,
    }

    # Create the RawPacket with the specified fields
    raw_packet = RawPacket(request, version=69, message=69, tag=69)
    request_bytes = raw_packet.to_bytes()

    try:
        # Send the request
        writer.write(request_bytes)
        await writer.drain()

        # Read the response
        buffer = await reader.read()  # Reads all available data
        if len(buffer) < 16:
            print("Incomplete response header")
            return False

        # Handle cases where the header indicates additional data
        packet_size = struct.unpack("<I", buffer[:4])[0]
        if len(buffer) < packet_size:
            extra_data = await reader.read(packet_size - len(buffer))
            buffer += extra_data

        # Parse the response as a RawPacket
        response_packet = RawPacket.from_bytes(buffer)
        result = response_packet.plist.get("Result")
        return isinstance(result, int) and result == 1
    except Exception as e:
        print("Error during communication with netmuxd: %s", e)
        return False
    finally:
        writer.close()
        await writer.wait_closed()


async def start_tunneld(udid) -> bool:
    # Send a GET request to http://localhost:49151/start-tunnel?udid={udid}
    response = requests.get(f"http://localhost:49151/start-tunnel?udid={udid}")
    if response.status_code == 200:
        print(f"Successfully started tunneld for UDID: {udid}")
        return True
    else:
        print(
            f"Failed to start tunneld for UDID: {udid}, Status Code: {response.status_code}"
        )
        return False
