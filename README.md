# Introduction

This project is based on the following electronic components:
1. ESP32-S3-Nano
2. ENS160 - for eCO2 & TVOC
3. VEML7700 - for luminosity of the environment. It can be left outdoors.
4. BME280 - for temperature, Humidity & pressure.

Project use I2C bus to communicate with the hardware sensors.
Pin A4 (SDA) & A5 (SCL) are used for I2C communication on the ESP32-S3-Nano

**_NOTE 1_**
Please note that ESP32-S3 or C6 will not work with the GCMP 256 or CCMP 256, AP shall use 128bit encryption instead of 256 meaning just the GCMP & CCMP (without 256 sufix).
You need to remove support of 256 bit encrtyption from the AP configuration otherwise the ESP will fall in WiFi connecting loop. THe ESP will see the WiFi networks,
but it will never connect. Please check the ESP32 documentaion for detailed specification. 

**_NOTE 2_**
BME280 is not perfect for temperature measurement as it use internal temprerature sensor to calibrate humidity. If you plan to use it for percise temperature
measurements then you need to use different hardware sensor. 

# Web access

This device allows pulling data by HTTP request getting JSON data, but main function is to send data to the zabbix server.
Currently there is no option within the code to disable pushing data to the zabbix server. Maybe in the next releaases there
could be an option to turn that off.

Device allow to check sensor data via simple HTTP page. It implements the simple http server. 

# Zabbix

The template has hardcoded the custom item names that must match these within the main.py file. If you plan to customize these names you need to change it in both files:
* main.py
* zabbix template.yaml

# Configuration

The configuration is done via setup.json file that is read on boot by main.py.
* SSID - WiFi network to which IoT device must connect to
* PASSWORD - WiFi password
* zabbix_server - IP address of the zabbix server to which push request will be made
* zabbix_port - TCP port number for zabbix active service communication
* hum_corr - integer value [-100:100] that tells in what direction to corect the humidity value
* temp_corr - integer value [-100:100] that tells in what direction to corect the temperatur value
* timezone - not much yet used, but just an integer [-12:12] representing timezone
* description - sting value with some description. It is used to display it on web page when you access IoT device with a browser
* nodename - FQDN device name that is also registered under exact same FQDN in zabbix
* pushtime - a time value [1:999999] in seconds between push to zabbix calls


# Resources
* https://github.com/awsiuk/ENS160

# Realization documentaion

![back of the sensors](https://github.com/awsiuk/weather_sensor/blob/main/Documentation/foto%20of%20the%20sensors%20back.JPG)
![simplified schematic](https://github.com/awsiuk/weather_sensor/blob/main/Documentation/weather%20sensor.drawio.png)

# Licence
You may use this code in comercial and personal use without fee. You are free to modify it and create copy of it and make your own project. When modifying this code in your own project that is separat from this package on personal or comericial purpose just leave credit information in your code for Lukasz Awsiukiewicz.
