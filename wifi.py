import time
import subprocess
import logging
from datetime import datetime
import sys

# SSID and password for the access point mode
AP_SSID = "raspberry-pee"
AP_PASSWORD = "11111112"

# Function to prepare hostapd and dnsmasq configurations
def prepare_access_point_config():
    # Configure hostapd
    hostapd_conf = """
    interface=wlan0
    driver=nl80211
    ssid={}
    hw_mode=g
    channel=7
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase={}
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    """.format(AP_SSID, AP_PASSWORD)

    with open("/etc/hostapd/hostapd.conf", "w") as f:
        f.write(hostapd_conf)

    # Configure dnsmasq
    dnsmasq_conf = """
    interface=wlan0
    dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
    """

    with open("/etc/dnsmasq.conf", "w") as f:
        f.write(dnsmasq_conf)

# Function to check network connection
def check_network_connection():
    try:
        # Use ping to check for network connectivity
        subprocess.check_output(['ping', '-c', '1', '8.8.8.8'])
        return True
    except subprocess.CalledProcessError:
        return False

# Function to switch to Access Point mode
def switch_to_access_point_mode():
    print("Switching to Access Point mode...")
    prepare_access_point_config()
    subprocess.call(['sudo', 'systemctl', 'stop', 'dhcpcd'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'wpa_supplicant'])
    subprocess.call(['sudo', 'ifconfig', 'wlan0', 'down'])
    subprocess.call(['sudo', 'iwconfig', 'wlan0', 'mode', 'ap'])
    subprocess.call(['sudo', 'ifconfig', 'wlan0', 'up'])
    subprocess.call(['sudo', 'systemctl', 'start', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'start', 'dnsmasq'])

# Function to switch back to Station mode
def switch_to_station_mode():
    print("Switching back to Station mode...")
    subprocess.call(['sudo', 'systemctl', 'stop', 'hostapd'])
    subprocess.call(['sudo', 'systemctl', 'stop', 'dnsmasq'])
    subprocess.call(['sudo', 'ifconfig', 'wlan0', 'down'])
    subprocess.call(['sudo', 'iwconfig', 'wlan0', 'mode', 'managed'])
    subprocess.call(['sudo', 'ifconfig', 'wlan0', 'up'])
    subprocess.call(['sudo', 'systemctl', 'start', 'dhcpcd'])
    subprocess.call(['sudo', 'systemctl', 'start', 'wpa_supplicant'])


def main():
    current_date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s' )
                    # filename=os.path.expanduser(f"/var/rasp-monitor/log_{current_date}.txt"))    
    # while True:
    #     if check_network_connection():
    #         print("Network is connected.")
    #     else:
    #         print("Network is not connected. Switching to Access Point mode...")
    #         switch_to_access_point_mode()

    #     # Sleep for 5 seconds before checking again
    #     time.sleep(5)


    if len(sys.argv) != 2:
        print("Usage: python main.py [ap|ws]")
        return
    mode = sys.argv[1]
    if mode == "ap":
        print("Access Point mode selected")
        switch_to_access_point_mode()
    elif mode == "ws":
        print("Station mode selected")
        switch_to_station_mode()

if __name__ == '__main__':
    main()
