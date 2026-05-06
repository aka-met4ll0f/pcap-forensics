#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path


BANNER = r"""
   _                _ _     _     ____   ____    _    ____
  / \   _ __   __ _| (_)___(_)___|  _ \ / ___|  / \  |  _ \
 / _ \ | '_ \ / _` | | / __| / __| |_) | |     / _ \ | |_) |
/ ___ \| | | | (_| | | \__ \ \__ \  __/| |___ / ___ \|  __/
/_/   \_\_| |_|\__,_|_|_|___/_|___/_|    \____/_/   \_\_|
"""


def run_shell_command(cmd: str):
    result = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def md_escape_path(path_str: str) -> str:
    return path_str.replace("\\", "\\\\")


def slugify(text: str) -> str:
    s = text.lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n",
        "(": "", ")": "", "/": "", ",": "", ".": "", ":": "", ";": "",
        "[": "", "]": "", "{": "", "}": "", "'": "", '"': "", "¿": "", "?": "",
        "¡": "", "!": "", "&": "y", "–": "-", "—": "-"
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return "-".join(s.split())


def build_forensic_ot_commands(pcap_path: str):
    pcap_q = f'"{pcap_path}"'
    return [
        {"title": "Hash SHA256 de la captura (cadena de custodia)", "desc": "Integridad forense.", "cmd": f"sha256sum {pcap_q}"},
        {"title": "Resumen de protocolos por paquete", "desc": "Top protocolos.", "cmd": f"tshark -r {pcap_q} -T fields -e frame.protocols | sort | uniq -c | sort -nr | head -100"},
        {"title": "Broadcast Ethernet", "desc": "Conteo de broadcast.", "cmd": f"tshark -r {pcap_q} -Y 'eth.dst == ff:ff:ff:ff:ff:ff' -T fields -e eth.dst | sort | uniq -c | sort -nr"},
        {"title": "Top puertos OT/ICS", "desc": "Puertos industriales frecuentes.", "cmd": f"tshark -r {pcap_q} -Y '(tcp.port == 502) || (tcp.port == 102) || (tcp.port == 20000) || (tcp.port == 44818) || (tcp.port == 4840) || (tcp.port == 2404) || (udp.port == 47808) || (udp.port == 2222) || (udp.port == 44818)' -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e _ws.col.Protocol -e _ws.col.Info"},
    ]


def build_commands(pcap_path: str, include_extras: bool = True, include_forensic_ot: bool = False):
    pcap_q = f'"{pcap_path}"'
    base_commands = [
        {"title": "Jerarquía de protocolos", "desc": "Distribución de protocolos.", "cmd": f"tshark -r {pcap_q} -q -z io,phs"},
        {"title": "IPs únicas con conteo", "desc": "IPs origen/destino.", "cmd": f"tshark -r {pcap_q} -T fields -e ip.src -e ip.dst | tr '\\t' '\\n' | grep -Eo '([0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}' | sort | uniq -c | sort -nr"},
        {"title": "Conversaciones IP", "desc": "Resumen de pares IP.", "cmd": f"tshark -r {pcap_q} -q -z conv,ip"},
        {"title": "SNMP comunidades", "desc": "Comunidades SNMP en claro.", "cmd": f"tshark -r {pcap_q} -Y 'snmp' -T fields -e snmp.community | sort -u"},
    ]
    extra_commands = [
        {"title": "Metadatos de captura", "desc": "Información con capinfos.", "cmd": f"capinfos {pcap_q}"},
        {"title": "Endpoints IP", "desc": "Top endpoints.", "cmd": f"tshark -r {pcap_q} -q -z endpoints,ip"},
        {"title": "Conversaciones TCP", "desc": "Flujos TCP.", "cmd": f"tshark -r {pcap_q} -q -z conv,tcp"},
        {"title": "Expert Info", "desc": "Alertas del analizador.", "cmd": f"tshark -r {pcap_q} -q -z expert"},
    ]
    commands = base_commands + (extra_commands if include_extras else [])
    if include_forensic_ot:
        commands += build_forensic_ot_commands(pcap_path)
    return commands


def generate_markdown_report(pcap_path: str, out_md: str, include_extras: bool = True, include_forensic_ot: bool = False):
    commands = build_commands(pcap_path, include_extras=include_extras, include_forensic_ot=include_forensic_ot)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines = [
        f"# Reporte de análisis de captura: `{md_escape_path(pcap_path)}`",
        "",
        f"- **Fecha de ejecución:** {now}",
        f"- **Archivo:** `{md_escape_path(pcap_path)}`",
        f"- **Comandos ejecutados:** {len(commands)}",
        "",
        "## Disclaimer",
        "Uso exclusivo para análisis autorizado.",
        "Autor: met4ll0f | GitHub: https://github.com/aka-met4ll0f",
        "",
        "## Contenido",
        "",
    ]

    for i, item in enumerate(commands, start=1):
        anchor = slugify(f"{i}. {item['title']}")
        report_lines.append(f"{i}. [{item['title']}](#{anchor})")

    report_lines += ["", "---", ""]
    success_count = 0
    fail_count = 0
    for idx, item in enumerate(commands, start=1):
        stdout, stderr, rc = run_shell_command(item["cmd"])
        success_count += int(rc == 0)
        fail_count += int(rc != 0)
        report_lines += [
            f"## {idx}. {item['title']}",
            "",
            item["desc"],
            "",
            "```bash",
            item["cmd"],
            "```",
            "",
            f"**Código de salida:** `{rc}`",
            "",
            "```text",
            stdout if stdout else "[Sin salida estándar]",
            "```",
            "",
        ]
        if stderr:
            report_lines += ["```text", stderr, "```", ""]
        report_lines += ["---", ""]

    report_lines += [
        "## Resumen",
        "",
        f"- Comandos exitosos: **{success_count}**",
        f"- Comandos con error: **{fail_count}**",
        "",
    ]
    Path(out_md).write_text("\n".join(report_lines), encoding="utf-8")


def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Genera reporte Markdown desde una captura pcap/pcapng.")
    parser.add_argument("-r", "--read", required=True, help="Ruta del archivo .pcap/.pcapng")
    parser.add_argument("-o", "--output", default="reporte_captura.md", help="Ruta de salida .md")
    parser.add_argument("--sin-extras", action="store_true", help="Solo comandos base.")
    parser.add_argument("--forense-ot", action="store_true", help="Activa comandos forense/OT.")
    args = parser.parse_args()

    pcap_path = args.read
    if not os.path.isfile(pcap_path):
        print(f"[ERROR] No existe el archivo: {pcap_path}", file=sys.stderr)
        sys.exit(1)
    if shutil.which("tshark") is None:
        print("[ERROR] tshark no está instalado o no está en PATH.", file=sys.stderr)
        sys.exit(1)

    generate_markdown_report(
        pcap_path,
        args.output,
        include_extras=not args.sin_extras,
        include_forensic_ot=args.forense_ot,
    )
    print(f"[OK] Reporte generado en: {args.output}")


if __name__ == "__main__":
    main()
