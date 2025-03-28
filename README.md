This project is based on following electronic components:
1. ESP32-S3-Nano
2. ENS160 - for eCO2 & TVOC
3. VEML7700 - for luminosity of the environment. It can be left outdoors.
4. BME280 - for temperature, Humidity & pressure.

Project use I2C bus to communicate with hardware sensors.
Pin A4 & A5 are used for I2C communication on ESP32-S3-Nano

NOTE!
Please note that ESP32-S3 or C6 will not work with GCMP 256 or CCMP 256, AP shall use 128bit encryption instead of 256 meaning just GCMP & CCMP (without 256 sufix).
You need to remove support of 256 bit encrtyption from AP configuration otherwise ESP will fall in WiFi connecting loop. ESP will see the WiFi networks,
but it will never connect. Please check ESP32 documentaion for detailed specification. 
