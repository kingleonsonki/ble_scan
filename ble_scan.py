#!/usr/bin/env python3
"""
ble_scan.py — Simple Bluetooth LE scanner using bleak

Usage examples:
  python ble_scan.py --timeout 8
  python ble_scan.py --timeout 10 --filter-name "MySensor"

Works on Windows, macOS, and Linux (BLE only). For classic RFCOMM (classic Bluetooth) scanning consider PyBluez or platform-specific APIs.
"""
import asyncio
import argparse
import json
from typing import Optional

try:
    from bleak import BleakScanner
except Exception:
    BleakScanner = None


async def do_scan(timeout: float = 5.0, filter_name: Optional[str] = None):
    if BleakScanner is None:
        raise RuntimeError("bleak is not installed. Run: pip install bleak")

    print(f"Scanning for BLE devices for {timeout} seconds...")
    devices = await BleakScanner.discover(timeout=timeout)

    if filter_name:
        devices = [d for d in devices if d.name and filter_name.lower() in d.name.lower()]

    if not devices:
        print("No devices found.")
        return []

    formatted = []
    for d in devices:
        item = {
            "address": d.address,
            "name": d.name or "",
            "rssi": getattr(d, "rssi", None),
            # bleak 0.17+ exposes metadata or details depending on backend
            "details": getattr(d, "metadata", {}) or getattr(d, "details", {}),
        }
        formatted.append(item)
        print(f"Address: {item['address']:<20} Name: {item['name']:<30} RSSI: {item['rssi']}")

    return formatted


def parse_args():
    p = argparse.ArgumentParser(description="Bluetooth LE scanner (uses bleak)")
    p.add_argument("--timeout", "-t", type=float, default=5.0, help="scan duration in seconds (default 5)")
    p.add_argument("--filter-name", "-f", type=str, default=None, help="case-insensitive substring to filter by device name")
    p.add_argument("--json", action="store_true", help="output JSON instead of human-readable lines")
    return p.parse_args()


def main():
    args = parse_args()
    try:
        results = asyncio.run(do_scan(timeout=args.timeout, filter_name=args.filter_name))
    except Exception as e:
        print("Error during scan:", e)
        return 2

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
