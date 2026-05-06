#!/usr/bin/env bash
set -euo pipefail

# DISCLAIMER: uso autorizado en laboratorio/controlado.
# Autor: met4ll0f | https://github.com/aka-met4ll0f

print_banner() {
  cat <<'EOF'
 _____ ___  ____    _____ _   _ _   _ _   _ _____ _
|_   _/ _ \|  _ \  |_   _| | | | \ | | \ | | ____| |
  | || | | | |_) |   | | | | | |  \| |  \| |  _| | |
  | || |_| |  _ <    | | | |_| | |\  | |\  | |___| |___
  |_| \___/|_| \_\   |_|  \___/|_| \_|_| \_|_____|_____|
EOF
}

TOR_UID=$(id -u tor)
TORRC="/etc/tor/torrc"
LOG_DIR="$HOME/tor_logs"
TIMESTAMP=$(date +%F_%H-%M-%S)
LOG_FILE="$LOG_DIR/tor_traffic_${TIMESTAMP}.pcap"
REPORT_FILE="$LOG_FILE.txt"

ensure_packages() {
  if command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm tor tcpdump wireshark-cli || true
  elif command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y tor tcpdump tshark || true
  fi
}

start_tor_tunnel() {
  ensure_packages
  mkdir -p "$LOG_DIR"
  sudo systemctl enable tor
  sudo systemctl restart tor

  sudo iptables -F
  sudo iptables -t nat -F
  sudo iptables -t nat -A OUTPUT -d 127.0.0.0/8 -j RETURN
  sudo iptables -t nat -A OUTPUT -m owner --uid-owner "$TOR_UID" -j RETURN
  sudo iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5353
  sudo iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports 9040
  sudo iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
  sudo iptables -A OUTPUT -o lo -j ACCEPT
  sudo iptables -A OUTPUT -m owner --uid-owner "$TOR_UID" -j ACCEPT
  sudo iptables -A OUTPUT -j REJECT

  sudo tcpdump -i lo port 9050 or port 9040 -w "$LOG_FILE" &
  echo $! > "$LOG_DIR/tcpdump.pid"
  echo "[OK] Capturando en $LOG_FILE"
}

analyze_capture() {
  {
    echo "===== Análisis de tráfico Tor ====="
    tshark -r "$LOG_FILE" -q -z io,phs
  } > "$REPORT_FILE" || true
  echo "[OK] Reporte: $REPORT_FILE"
}

stop_tor_tunnel() {
  if [ -f "$LOG_DIR/tcpdump.pid" ]; then
    sudo kill "$(cat "$LOG_DIR/tcpdump.pid")" || true
    rm -f "$LOG_DIR/tcpdump.pid"
  fi
  sudo iptables -F
  sudo iptables -t nat -F
  sudo systemctl stop tor || true
  analyze_capture
}

case "${1:-}" in
  --start) print_banner; start_tor_tunnel ;;
  --stop) print_banner; stop_tor_tunnel ;;
  *) echo "Uso: $0 --start | --stop" ;;
esac
