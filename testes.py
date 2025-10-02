import socket
from datetime import datetime
import ntplib
import urllib.request
import json

def internet_connection(host="1.1.1.1", port=53, timeout=1):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

def datetime_from_internet():
    """Retorna datetime da internet sem milissegundos ou None se não conseguir."""
    
    if not internet_connection():
        return None

    # Tenta NTP
    ntp_servers = ["pool.ntp.org", "time.google.com", "time.windows.com"]
    for server in ntp_servers:
        try:
            client = ntplib.NTPClient()
            response = client.request(server, version=3, timeout=2)
            return datetime.fromtimestamp(response.tx_time).replace(microsecond=0)
        except Exception:
            continue

    # Fallback HTTP
    try:
        url = "https://worldtimeapi.org/api/ip"
        req = urllib.request.Request(url, headers={"User-Agent": "Python"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.load(resp)
            dt_str = data["datetime"]
            dt = datetime.fromisoformat(dt_str[:-6]).replace(microsecond=0)
            return dt
    except Exception:
        return None

# Uso
dt = datetime_from_internet()
if dt:
    print("Data/hora da internet (sem ms):", dt)
else:
    print("Não foi possível obter a data/hora da internet")
