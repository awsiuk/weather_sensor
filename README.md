***BASELINE***
This project is based on following electronic components:
1. ESP32-S3-Nano
2. ENS160 - for eCO2 & TVOC
3. VEML7700 - for luminosity of the environment. It can be left outdoors.
4. BME280 - for temperature, Humidity & pressure.

Project use I2C bus to communicate with hardware sensors.
Pin A4 (SDA) & A5 (SCL) are used for I2C communication on ESP32-S3-Nano

***NOTE!***
Please note that ESP32-S3 or C6 will not work with GCMP 256 or CCMP 256, AP shall use 128bit encryption instead of 256 meaning just GCMP & CCMP (without 256 sufix).
You need to remove support of 256 bit encrtyption from AP configuration otherwise ESP will fall in WiFi connecting loop. ESP will see the WiFi networks,
but it will never connect. Please check ESP32 documentaion for detailed specification. 

***WEBACCESS***
This device allow pulling data by HTTP request getting JSON data, but main function is to send data to zabbix server.
Currently there is no option within code to disable pushing data to zabbix server. Maybe in next releaases there
could be an option to turn that off.

Device allow to check sensor data via simple HTTP page. It implement simple http server. 

***Zabbix***
Template has hardcoded custom item names that must match these within main.py file. If you plan to customize names you need to change it in both files:
* main.py
* zabbix template.yaml

***Configuration***
Configuration is done via setup.json file that is read on boot by main.py.
SSID - WiFi network to which IoT device must connect to
PASSWORD - WiFi password
zabbix_server - IP address of the zabbix server to which push request will be made
zabbix_port - TCP port number for zabbix active service communication
hum_corr - integer value [-100:100] that tells in what direction to corect the humidity value
temp_corr - integer value [-100:100] that tells in what direction to corect the temperatur value
timezone - not much yet used, but just an integer [-12:12] representing timezone
description - sting value with some description. It is used to display it on web page when you access IoT device with a browser
nodename - FQDN device name that is also registered under exact same FQDN in zabbix
pushtime - a time value [1:999999] in seconds between push to zabbix calls
