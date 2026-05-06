# pcap-forensics

![CI](https://github.com/aka-met4ll0f/pcap-forensics/actions/workflows/ci.yml/badge.svg)
![Tipo](https://img.shields.io/badge/Tipo-Forensics-blue)

## Descripción
Automatización de captura y análisis de tráfico para investigación de red.

## Scripts incluidos
- `analisis_pcap.py`: ejecuta múltiples comandos `tshark/capinfos` y construye un reporte Markdown.
- `tor_tunnel.sh`: enruta tráfico local por Tor, captura paquetes y genera resumen de análisis.

## Resumen rápido
| Script | Entrada | Salida | Uso típico |
|---|---|---|---|
| `analisis_pcap.py` | Archivo `.pcap/.pcapng` | Reporte `.md` | Análisis técnico y forense de capturas de red |
| `tor_tunnel.sh` | Parámetro `--start/--stop` | `.pcap` + resumen `.txt` | Pruebas de tráfico enroutado por Tor con evidencia |

## Requisitos
- Linux con `python3` y `bash`.
- `tshark`, `capinfos` (opcional para extras), `tor`, `tcpdump`, `iptables`.

## Uso
1. Da permisos de ejecución:
   - `chmod +x analisis_pcap.py tor_tunnel.sh`
2. Ejecuta análisis de una captura:
   - `python3 analisis_pcap.py -r Captura.pcapng -o reporte.md`
3. Para modo forense/OT:
   - `python3 analisis_pcap.py -r Captura.pcapng -o reporte_ot.md --forense-ot`
4. Para túnel Tor + captura:
   - `./tor_tunnel.sh --start`
   - realiza pruebas de tráfico
   - `./tor_tunnel.sh --stop`

## Salidas
- Reportes Markdown (`reporte.md`, `reporte_ot.md`).
- Capturas y reportes en `~/tor_logs/`.

## Autor
- Autor: **met4ll0f**
- GitHub: `https://github.com/aka-met4ll0f`

## Aviso legal
Usar solo con permiso del propietario del sistema o en laboratorio/CTF. El creador no se hace responsable por el mal uso.
