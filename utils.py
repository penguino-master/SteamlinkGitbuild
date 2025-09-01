import subprocess
import re

def get_volume():
    result = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True)
    match = re.search(r'(\d+)%', result.stdout)
    return int(match.group(1)) if match else None

def set_volume(percent):
    subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"])

def get_ip_mac():
    ip_output = subprocess.getoutput("hostname -I").strip()
    ipv4 = next((ip for ip in ip_output.split() if re.match(r"\d+\.\d+\.\d+\.\d+", ip)), "N/A")
    mac = subprocess.getoutput("cat /sys/class/net/eth0/address").strip()
    return ipv4, mac
