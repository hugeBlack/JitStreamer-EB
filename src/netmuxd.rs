// Jackson Coxson

use std::net::IpAddr;

use log::error;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::UnixStream,
};

use crate::raw_packet;

const NETMUXD_SOCKET: &str = "/var/run/usbmuxd";
const SERVICE_NAME: &str = "apple-mobdev2";
const SERVICE_PROTOCOL: &str = "tcp";

/// Connects to the unix socket and adds the device
pub async fn add_device(ip: IpAddr, udid: &str) -> bool {
    let mut stream = UnixStream::connect(NETMUXD_SOCKET)
        .await
        .expect("Could not connect to netmuxd socket, is it running?");

    let mut request = plist::Dictionary::new();
    request.insert("MessageType".into(), "AddDevice".into());
    request.insert("ConnectionType".into(), "Network".into());
    request.insert(
        "ServiceName".into(),
        format!("_{}._{}.local", SERVICE_NAME, SERVICE_PROTOCOL).into(),
    );
    request.insert("IPAddress".into(), ip.to_string().into());
    request.insert("DeviceID".into(), udid.into());

    let request = raw_packet::RawPacket::new(request, 69, 69, 69);
    let request: Vec<u8> = request.into();

    stream.write_all(&request).await.unwrap();

    let mut buf = Vec::new();
    let size = stream.read_to_end(&mut buf).await.unwrap();

    let buffer = &mut buf[0..size].to_vec();
    if size == 16 {
        let packet_size = &buffer[0..4];
        let packet_size = u32::from_le_bytes(packet_size.try_into().unwrap());
        // Pull the rest of the packet
        let mut packet = vec![0; packet_size as usize];
        let _ = stream.read(&mut packet).await.unwrap();
        // Append the packet to the buffer
        buffer.append(&mut packet);
    }

    let parsed: raw_packet::RawPacket = match buffer.try_into() {
        Ok(p) => p,
        Err(_) => {
            log::error!("Failed to parse response as usbmuxd packet!!");
            return false;
        }
    };
    match parsed.plist.get("Result") {
        Some(plist::Value::Integer(r)) => r.as_unsigned().unwrap() == 1,
        _ => false,
    }
}

pub async fn remove_device(udid: &str) {
    let mut stream = UnixStream::connect(NETMUXD_SOCKET)
        .await
        .expect("Could not connect to netmuxd socket, is it running?");

    let mut request = plist::Dictionary::new();
    request.insert("MessageType".into(), "RemoveDevice".into());
    request.insert("DeviceID".into(), udid.into());

    let request = raw_packet::RawPacket::new(request, 69, 69, 69);
    let request: Vec<u8> = request.into();

    if let Err(e) = stream.write_all(&request).await {
        error!("Error writing to netmuxd socket: {}", e);
    }
}
