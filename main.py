import time 
import subprocess
import requests
import re
import random
import os
import logging
import asyncio
from threading import Thread, Lock
from datetime import datetime

from flask import Flask, render_template, request

def is_internet_available():
    try:
        subprocess.check_output(["ping", "-c", "1", "-W", "2", "8.8.8.8"])
        return True
    except subprocess.CalledProcessError:
        return False

def wait_for_internet():
    while not is_internet_available():
        logging.info("Internet not available. Waiting...")
        time.sleep(1)  # Wait for 5 seconds before checking again

    logging.info("Internet connection is available!")
    
def getIfConfig():
    try:
        result_wlan0 = subprocess.check_output(['ip', 'addr', 'show', 'wlan0']).decode('utf-8')
        result_eth0 = subprocess.check_output(['ip', 'addr', 'show', 'eth0']).decode('utf-8')
        result_iwconfig = subprocess.check_output(['iwconfig', 'wlan0']).decode('utf-8')
        result = result_iwconfig + '\n' + result_wlan0 + '\n' + result_eth0
        cleaned_result = '\n'.join(line for line in result.splitlines() if line.strip())
        return cleaned_result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

def readWpaSupplicantConf():
    try:
        result = subprocess.check_output(['sudo', 'cat', '/etc/wpa_supplicant/wpa_supplicant.conf']).decode('utf-8')
        cleaned_result = '\n'.join(line for line in result.splitlines() if line.strip())
        return cleaned_result
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    print("Load index  ")
    if_config_data = getIfConfig()
    wpa_data = readWpaSupplicantConf()
    if request.method == 'POST':
        wpa_data = readWpaSupplicantConf()
        return redirect(url_for('index'))
    return render_template('index.html', if_config_data=if_config_data, wpa_data=wpa_data)


@app.route('/process', methods=['POST'])
def process():
    print("Load set network  ")
    id = request.form['id']
    password = request.form['password']
    wifi_cmd = '''network_id=$(sudo wpa_cli add_network | sed -n '2p') ; sudo wpa_cli set_network $network_id ssid '"'''+id+ '''"'; sudo wpa_cli set_network $network_id psk '"'''+password+'''"'; sudo wpa_cli enable_network $network_id; sudo wpa_cli save_config'''
    print(wifi_cmd)
    result = subprocess.check_output(wifi_cmd, shell=True, text=True)

    return f'ID: {id}, Password: {password}'

@app.route('/wpaconfig', methods=['POST'])
def wpaconfig():
    print("Load status wpa  ")
    return readWpaSupplicantConf()

@app.route('/remove_wifi_config', methods=['POST'])
def remove_wpaconfig():
    print("Load remove wpa  ")
    id = request.form['id']
    fetch_cmd = '''sudo wpa_cli list_networks | awk -v id="'''+id+'''" 'NR == '''+id+'''+2 {print $1}' '''
    fetch_result = subprocess.check_output(fetch_cmd, shell=True, text=True)
    print(f"fetch result = {fetch_result}")
    
    remove_cmd = '''sudo wpa_cli remove_network '''+fetch_result
    save_cmd  = ''' sudo wpa_cli save_config'''
    result = subprocess.check_output(remove_cmd, shell=True, text=True)
    time.sleep(0.2)
    result2 = subprocess.check_output(save_cmd, shell=True, text=True)

    return result


def main():
    current_date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s' )
                    # filename=os.path.expanduser(f"/var/rasp-monitor/log_{current_date}.txt"))    
    app.run(debug=True,host='0.0.0.0', port=10001)


if __name__ == '__main__':
    main()
