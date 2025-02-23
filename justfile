build:
  cargo build --release
run: build
  sudo ./target/release/jitstreamer-eb
docker-build:
  cargo clean
  sudo docker build -t jkcoxson/jitstreamer-eb .
docker-run:
  sudo docker run --rm -it \
  --name jitstreamer-eb \
  -p 9172:9172 \
  -p 51869:51869/udp \
  -v jitstreamer-lockdown:/var/lib/lockdown \
  -v jitstreamer-wireguard:/etc/wireguard \
  -v $(pwd)/jitstreamer.db:/app/jitstreamer.db \
  -e RUST_LOG=info \
  --cap-add=NET_ADMIN \
  --device /dev/net/tun:/dev/net/tun \
  jitstreamer-eb
docker-shell:
  sudo docker exec -it jitstreamer-eb /bin/bash
