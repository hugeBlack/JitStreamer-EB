# Usage on MacOS

## Building
Clone and build the following repositories:

[netmuxd](https://github.com/jkcoxson/netmuxd)
[tunneld-rs](https://github.com/jkcoxson/tunneld-rs)
[JitStreamer-EB](https://github.com/jkcoxson/JitStreamer-EB)

```bash
# Clone repositories
git clone https://github.com/jkcoxson/netmuxd.git
git clone https://github.com/jkcoxson/tunneld-rs.git
git clone https://github.com/jkcoxson/JitStreamer-EB.git

# Build each project
cd netmuxd && cargo build --release
cd ../tunneld-rs && cargo build --release
cd ../JitStreamer-EB && cargo build --release
```

## Usage
If you have a weird Python and brew dumpster fire like I do, create a venv
and install the dependencies:

```bash
mkdir venv
python3 -m venv venv
pip3 install requests aiosqlite pymobiledevice3
```

Download the [runners](../src/runners) folder to your folder

## Running Services
Run the following commands in 3 separate terminals:

1. Tunneld:
```bash
sudo RUST_LOG=info USBMUXD_SOCKET_ADDRESS=127.0.0.1:27015 ./target/release/tunneld-rs
```

2. Netmuxd:
```bash
sudo RUST_LOG=info ./target/release/netmuxd --disable-unix --host 127.0.0.1 --plist-storage ~/Desktop/plist_storage
```

3. JitStreamer:
```bash
RUST_LOG=info PLIST_STORAGE=~/Desktop/plist_storage ALLOW_REGISTRATION=2 USBMUXD_SOCKET_ADDRESS=127.0.0.1:27015 ./target/release/jitstreamer-eb
```

## Final Steps
1. Get your shortcut from [jkcoxson.com/jitstreamer](https://jkcoxson.com/jitstreamer)
2. Change the IP to your Mac's IP address
3. Go to `your.macs.ip:9172/upload`
4. Submit your pairing file
5. Profit
