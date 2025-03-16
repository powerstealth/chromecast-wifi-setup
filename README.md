# Chromecast WiFi Setup Without Google Home

## Overview
This script allows you to connect a Chromecast device to a WiFi network without using the Google Home app. The process requires your Chromecast to be on Ethernet or, if it’s not, you must manually join its setup WiFi network. Once connected, the script configures the device to use your chosen WiFi network and can also change the Chromecast’s name.

Since March 9th, 2025, Google’s Certificate Authority (CA) for Chromecast has expired, so this script also enables you to bypass this issue and connect your Chromecast to a WiFi network directly.

This approach follows the process described in [this Reddit post](https://www.reddit.com/r/Chromecast/comments/1jae015/brief_howto_set_up_2nd_gen_google_chromecast/)

How to set up 2nd Gen Google Chromecast, with improvements made in the script, which can be found at [Chromecast WiFi Setup Script on Gist](https://github.com/powerstealth/chromecast-wifi-setup/edit/main/README.md).

## Features
- Connects a Chromecast to a WiFi network using a normal computer.
- Allows Chromecast initial setup without the Google Home app.
- Uses a computer’s network connection to configure the device.
- Encrypts the WiFi password using the Chromecast's public key.

## Requirements
- Python 3.x installed.
- Required Python libraries: `requests`, `cryptography`, `urllib3`.

## Installing dependencies
To install the required dependencies, use the following command:

    pip install requests cryptography

## How to Use

### Step 1: Configure the Script
The script must be configured with the following parameters before use:

1. **chromecast_ip**: The IP address of your Chromecast (usually `192.168.255.249` for a device in setup mode).
2. **wifi_ssid**: The SSID (name) of the WiFi network you want to connect your Chromecast to.
3. **wifi_auth_number**: The authentication type of your WiFi (7 for PSK).
4. **wifi_cipher_number**: The cipher type used by your WiFi (4 for WPA2).
5. **wifi_password**: The password for the WiFi network.
6. **chromecast_name**: The name you want to assign to the Chromecast (optional).

Here is an example of how the initial setup looks:

    chromecast_ip      = '192.168.255.249'
    wifi_ssid          = 'Mi Wifi'
    wifi_auth_number   = 7  # PSK
    wifi_cipher_number = 4  # WPA2
    wifi_password      = 'dslhK2!!sfsafS'
    chromecast_name    = 'Device1'

Modify these values to reflect your Chromecast's setup and the WiFi network you want it to connect to.

### Step 2: Run the Script
After configuration, execute the script with the following command:

    python3 castanet.py

### Step 3: Monitor the Connection Process
The script will connect your Chromecast to the WiFi network using its temporary hotspot. It will:
1. Scan for available WiFi networks.
2. Find and connect to the specified SSID.
3. Encrypt the WiFi password using the Chromecast's public key.
4. Configure the Chromecast to connect to the network.
5. Optionally, rename the Chromecast to the desired name.

### Step 4: Verify the Setup
Once the script completes, your Chromecast will be connected to the specified WiFi network. You can verify the connection and even modify settings through additional `curl` commands provided at the end of the script.

Example commands to verify device information:

    curl --insecure --tlsv1.2 --tls-max 1.2 https://${CHROMECAST_IP}:8443/setup/eureka_info | jq .

### Step 5: Optional Commands
Additional commands that you can use after setting up the Chromecast:
- **List known WiFi networks**:

      curl --insecure --tlsv1.2 --tls-max 1.2 https://${CHROMECAST_IP}:8443/setup/configured_networks | jq .

- **Forget a specific WiFi network**:

      curl --insecure --tlsv1.2 --tls-max 1.2 -H "content-type: application/json" -d '{"wpa_id": 0}' https://${CHROMECAST_IP}:8443/setup/forget_wifi

- **Change the Chromecast name**:

      curl --insecure --tlsv1.2 --tls-max 1.2 -H "content-type: application/json" -d '{"name": "NovakCast5000", "opt_in": {"crash": false, "stats": false, "opencast": false}}' https://${CHROMECAST_IP}:8443/setup/set_eureka_info

## Configuration
To configure the script:
1. Set the **chromecast_ip** to the IP address of your Chromecast (typically `192.168.255.249`).
2. Set the **wifi_ssid** and **wifi_password** to match your desired WiFi network.
3. Modify **wifi_auth_number** and **wifi_cipher_number** according to your WiFi's security settings (PSK and WPA2 are the most common).
4. Optionally, change **chromecast_name** to whatever you want your Chromecast to be called.

The script is designed to automatically detect and connect to the Chromecast's setup network, but you may need to find the IP manually using network tools like Wireshark if it's not automatically detected.

## Troubleshooting
- **Chromecast not detected**: If the Chromecast is not detected or the connection fails, ensure that the Chromecast is on its setup network and reachable at the IP `192.168.255.249`. You may need to manually find the IP address using network tools like Wireshark.
- **SSL Errors**: SSL certificate warnings are disabled in this script because Chromecast uses self-signed certificates. If you encounter SSL issues, this is expected.
- **Dependencies Missing**: If you get an error about missing dependencies, ensure that the necessary Python packages (`requests`, `cryptography`) are installed using `pip`.

## License
This script is open-source. Feel free to modify and use it as per your needs.
