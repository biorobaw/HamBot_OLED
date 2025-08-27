import subprocess
from typing import Optional, Tuple

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


def _get_ip_for_interface(interface: str) -> str:
    try:
        output = subprocess.check_output(
            ["ip", "-4", "addr", "show", interface],
            text=True
        )
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
    except Exception:
        pass
    return "No IP"


def _active_wifi_ssid() -> Optional[str]:
    # Returns SSID if connected as a Wi-Fi client; else None
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"], text=True).strip()
        return ssid or None
    except subprocess.CalledProcessError:
        return None


def _active_ap_ssid_via_nmcli() -> Optional[str]:
    # If broadcasting an AP via NetworkManager, returns SSID; else None
    try:
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active"],
            text=True
        )
        for line in output.splitlines():
            if not line.strip():
                continue
            name, ctype = line.split(":", 1)
            if ctype == "802-11-wireless":
                return name
    except Exception:
        pass
    return None


def get_display_triplet(prefer_interface: str = "wlan0") -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Returns (mode, ssid, ip) or (None, None, None) if nothing to show.
    mode ∈ {"WiFi", "AP"}.
    """
    ssid = _active_wifi_ssid()
    if ssid:
        return "WiFi", ssid, _get_ip_for_interface(prefer_interface)

    ap_ssid = _active_ap_ssid_via_nmcli()
    if ap_ssid:
        return "AP", ap_ssid, _get_ip_for_interface(prefer_interface)

    return None, None, None


class OledScreen:
    def __init__(self, width: int = 128, height: int = 32, addr: int = 0x3C, reset_pin=board.D4, font_path: Optional[str] = None):
        i2c = board.I2C()
        reset = digitalio.DigitalInOut(reset_pin)
        self._oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c, addr=addr, reset=reset)
        self._oled.fill(0)
        self._oled.show()
        self.width, self.height = width, height
        self.font = ImageFont.load_default() if font_path is None else ImageFont.truetype(font_path, 12)

    def show_lines(self, lines):
        img = Image.new("1", (self.width, self.height))
        draw = ImageDraw.Draw(img)
        for i, text in enumerate(lines[:3]):
            draw.text((0, i * 10), text, font=self.font, fill=255)
        self._oled.image(img)
        self._oled.show()

    def clear(self):
        self._oled.fill(0)
        self._oled.show()
