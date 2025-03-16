#!/usr/bin/env python3
# castanet.py: Script to connect a chromecast to a WiFi network.
#
# Allows you to put your Chromecast on WiFi and do Chromecast initial setup
# without using the Google Home app at all, just using a normal computer.
#
# You do need your Chromecast to be on Ethernet, or (untested) to join its setup WiFi
# network with your PC, and you also need to find out its IP yourself with e.g.
# Wireshark.
#
#
# Since 2025-03-09 the CA of Google for Chromecast is expired (see https://www.reddit.com/r/Chromecast/comments/1j7lhrs/comment/mgy1a88/ )
# To enable Cast from android:
# 1) enable adb
# 2) adb shell am start-activity -a com.google.android.gms.cast.settings.CastSettingsCollapsingDebugAction

import os
import sys
import json
import time
import subprocess
import requests
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

# Disable SSL warnings for self-signed certificates
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
    import json
    from cryptography.hazmat.primitives import serialization
except ImportError as e:
    print(f"Error: Missing dependency - {e}")
    print("Install required packages with: pip install requests cryptography")
    sys.exit(1)


def main():
    # STEP0 => Connect to the chromecast temporary hotspot wifi
    chromecast_ip      = '192.168.255.249'
    wifi_ssid          = 'Gatto Spiderman 2.4'
    wifi_auth_number   = 7 # PSK
    wifi_cipher_number = 4 # WPA2
    wifi_password      = 'topolinoJosh!'
    chromecast_name    = 'Master Bedroom'
    
    print(f"Connecting {chromecast_ip} to {wifi_ssid} with password {wifi_password}")

    # Base URL for API requests
    base_url = f"https://{chromecast_ip}:8443/setup"

    # Get the device's public key
    info_response = requests.get(f"{base_url}/eureka_info", verify=False)
    info_json = info_response.json()
    chromecast_pubkey = info_json["public_key"]
    
    if wifi_auth_number != '':
        # Scan for WiFi networks
        requests.post(f"{base_url}/scan_wifi", verify=False)
        print("Scanning for WiFi networks...")
        time.sleep(20)  # Wait for scan to complete
        
        # Get scan results
        wifi_response = requests.get(f"{base_url}/scan_results", verify=False)
        wifi_json = wifi_response.json()
        
        # Find our network
        wifi_network = None
        for network in wifi_json:
            if network["ssid"] == wifi_ssid:
                wifi_network = network
                break
        
        if not wifi_network:
            print(f"Error: Could not find WiFi network '{wifi_ssid}'", file=sys.stderr)
            sys.exit(1)
        
        wifi_auth_number = wifi_network["wpa_auth"]
        wifi_cipher_number = wifi_network["wpa_cipher"]
        print(json.dumps(wifi_network, indent=2))
    
    # Encrypt the password for the device
    encrypted_key = encrypt_password(wifi_password, chromecast_pubkey)
    
    # Generate the command to connect
    connect_command = {
        "ssid": wifi_ssid, 
        "wpa_auth": wifi_auth_number, 
        "wpa_cipher": wifi_cipher_number, 
        "enc_passwd": encrypted_key
    }
    
    # And the command to save the connection
    save_command = {"keep_hotspot_until_connected": True}
    
    # Send the commands
    headers = {"content-type": "application/json"}
    
    connect_response = requests.post(
        f"{base_url}/connect_wifi", 
        headers=headers,
        data=json.dumps(connect_command),
        verify=False
    )
    print("Connect response: %s", connect_response.status_code)
    print("Connect Headers: %s", connect_response.headers)
    
    save_response = requests.post(
        f"{base_url}/save_wifi", 
        headers=headers,
        data=json.dumps(save_command),
        verify=False
    )
    print("Connect response: %s", save_response.status_code)
    print("Connect Headers: %s", save_response.headers)
    print("Connect Headers: %s", save_response.text)
    
    # Set the Chromecast name if provided
    if chromecast_name:
        rename_command = {
            "name": chromecast_name,
            "opt_in": {
                "crash": False,
                "stats": False,
                "opencast": False
            }
        }
        
        rename_response = requests.post(
            f"{base_url}/set_eureka_info",
            headers=headers,
            data=json.dumps(rename_command),
            verify=False
        )
        print(f"Renamed Chromecast to '{chromecast_name}'. Response:", rename_response.status_code)
    
    print("\nConnection commands sent successfully!")
    print("""
Additional commands you can run:
- To see device info:
  curl --insecure --tlsv1.2 --tls-max 1.2 https://${CHROMECAST_IP}:8443/setup/eureka_info | jq .
- To list known networks:
  curl --insecure --tlsv1.2 --tls-max 1.2 https://${CHROMECAST_IP}:8443/setup/configured_networks | jq .
- To forget a network:
  curl --insecure --tlsv1.2 --tls-max 1.2 -H "content-type: application/json" -d '{"wpa_id": 0}' https://${CHROMECAST_IP}:8443/setup/forget_wifi
- To set name and opt out of things:
  curl --insecure --tlsv1.2 --tls-max 1.2 -H "content-type: application/json" -d '{"name": "NovakCast5000", "opt_in": {"crash": false, "stats": false, "opencast": false}}' https://${CHROMECAST_IP}:8443/setup/set_eureka_info
""")

def encrypt_password(password, public_key_pem):
    """Encrypt the WiFi password with the Chromecast's public key"""
    
    # Format the key properly
    public_key_pem = f"-----BEGIN RSA PUBLIC KEY-----\n{public_key_pem}\n-----END RSA PUBLIC KEY-----"
    
    # Load the public key
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode('utf-8'),
        backend=default_backend()
    )
    
    # Encrypt the password
    encrypted_data = public_key.encrypt(
        password.encode('utf-8'),
        padding.PKCS1v15()
    )
    
    # Return the base64 encoded result
    return base64.b64encode(encrypted_data).decode('utf-8')

if __name__ == "__main__":
    #check_dependencies()
    main()