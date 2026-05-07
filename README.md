# pcap-forensics

![CI](https://github.com/aka-met4ll0f/pcap-forensics/actions/workflows/ci.yml/badge.svg)
![Type](https://img.shields.io/badge/Type-Forensics-blue)

## Description
Network traffic capture and analysis automation for forensic and technical investigations.

## Included scripts
- `analisis_pcap.py`: runs multiple `tshark/capinfos` commands and builds a Markdown report.
- `tor_tunnel.sh`: routes local traffic through Tor, captures packets, and generates an analysis summary.

## Quick summary
| Script | Input | Output | Typical use |
|---|---|---|---|
| `analisis_pcap.py` | `.pcap/.pcapng` file | `.md` report | Technical and forensic packet-capture analysis |
| `tor_tunnel.sh` | `--start/--stop` flag | `.pcap` + `.txt` summary | Tor-routed traffic testing with evidence collection |

## Requirements
- Linux with `python3` and `bash`.
- `tshark`, `capinfos` (optional for extra checks), `tor`, `tcpdump`, `iptables`.

## Usage
1. Grant execution permissions:
   - `chmod +x analisis_pcap.py tor_tunnel.sh`
2. Run a capture analysis:
   - `python3 analisis_pcap.py -r Captura.pcapng -o reporte.md`
3. For forensic/OT mode:
   - `python3 analisis_pcap.py -r Captura.pcapng -o reporte_ot.md --forense-ot`
4. For Tor tunnel + capture:
   - `./tor_tunnel.sh --start`
   - run your traffic tests
   - `./tor_tunnel.sh --stop`

## Outputs
- Markdown reports (`reporte.md`, `reporte_ot.md`).
- Captures and reports in `~/tor_logs/`.

## Author
- Author: **met4ll0f**
- GitHub: `https://github.com/aka-met4ll0f`

## Legal Notice
Use only with explicit owner permission or in a controlled lab/CTF. The creator is not responsible for misuse.
