# Usage on MacOS

Rough instructions by jkcoxson, could be explained better.

## Building

Clone the following repos and build them with cargo:

[netmuxd](https://github.com/jkcoxson/netmuxd)
[tunneld-rs](https://github.com/jkcoxson/tunneld-rs)
[JitStreamer-EB](https://github.com/jkcoxson/JitStreamer-EB)

```bash
cargo build --release
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

Run the following commands in separate terminals, they'll do the magic.

```bash
sudo RUST_LOG=info USBMUXD_SOCKET_ADDRESS=127.0.0.1:27015 ./target/release/tunneld-rs
sudo RUST_LOG=info ./target/release/netmuxd --disable-unix --host 127.0.0.1 --plist-storage ~/Desktop/plist_storage
RUST_LOG=info PLIST_STORAGE=~/Desktop/plist_storage ALLOW_REGISTRATION=2 USBMUXD_SOCKET_ADDRESS=127.0.0.1:27015 ./target/release/jitstreamer-eb
```

Get your shortcut from the [site](https://jkcoxson.com/jitstreamer)
and change the IP to your Mac's IP

## Yay

Go to ``your.macs.ip:9172/upload`` and submit your pairing file.
Run the shortcut. Profit.
