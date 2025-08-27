import argparse
import time
from .display import OledScreen, get_display_triplet

def _render_once(screen: OledScreen, iface: str):
    mode, ssid, ip = get_display_triplet(prefer_interface=iface)
    if mode and ssid and ip:
        screen.show_lines([f"Mode: {mode}", f"SSID: {ssid}", f"IP:   {ip}"])
    else:
        screen.clear()

def main():
    p = argparse.ArgumentParser(description="HamBot OLED network display")
    p.add_argument("--iface", default="wlan0", help="Interface to read IPv4 from (default: wlan0)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--oneshot", action="store_true", help="Render once and exit")
    g.add_argument("--refresh", type=int, metavar="SECONDS", help="Loop and refresh every N seconds")
    p.add_argument("--font", help="Optional TTF font path (e.g., Terminus TTF)")
    p.add_argument("--width", type=int, default=128)
    p.add_argument("--height", type=int, default=32)
    p.add_argument("--i2c-addr", type=lambda x: int(x, 0), default="0x3C", help="OLED I2C address (hex, e.g. 0x3C)")
    args = p.parse_args()

    screen = OledScreen(width=args.width, height=args.height, addr=args.i2c_addr, font_path=args.font)

    if args.oneshot:
        _render_once(screen, args.iface)
        return

    interval = args.refresh if args.refresh and args.refresh > 0 else 10
    while True:
        _render_once(screen, args.iface)
        time.sleep(interval)
