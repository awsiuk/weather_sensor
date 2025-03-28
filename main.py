import network
import socket
import machine
import json
import urandom
import time
import _thread
import struct
import uos

from myENS160 import *
from myVEML7700 import *
from BME280 import *

#for random function needed to generate session identifier
keys = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'


data={
    "temp": 0,
    "hum": 0,
    "AQI": 0,
    "TVOC": 0,
    "eCO2": 0,
    "lux": 0,
    "pressure": 0.0}

#create a function that updates a host variable, host is this node where the code is running so it should be taken from config file
#these keys are created within zabbix template (and must be exactly the same)
#values for these keys are some random data for tests and should be changed during data initialization
#and later updated while a code runs
#this data structure holds a data that will be transmited to the zabbix server
zabbix_data = {
    "request": "agent data",
    "data": [
        {"id":1, "host": "dummy", "key": "custom.pogodynka.temp", "value": 0.0, "clock": 0,"ns": 0},
        {"id":2, "host": "dummy", "key": "custom.pogodynka.hum", "value": 0.0, "clock": 0,"ns": 0},
        {"id":3, "host": "dummy", "key": "custom.pogodynka.AQI", "value": 0, "clock": 0,"ns": 0},
        {"id":4, "host": "dummy", "key": "custom.pogodynka.TVOC", "value": 0, "clock": 0,"ns": 0},
        {"id":5, "host": "dummy", "key": "custom.pogodynka.eCO2", "value": 0, "clock": 0,"ns": 0},
        {"id":6, "host": "dummy", "key": "custom.pogodynka.lux", "value": 0, "clock": 0,"ns": 0},
        {"id":7, "host": "dummy", "key": "custom.pogodynka.pressure", "value": 0.0, "clock": 0,"ns": 0.0}
        ],
    "session": ""
}

#used by zabbix packet creation
def randstr(length=32, aSeq=keys):
    return ''.join((urandom.choice(aSeq) for _ in range(length)))

#this function updates package structure based on collected data
def build_packet():
    #get time counters need by zabbix server
    #this is the time when data was collected
    epoch=time.localtime()
    nstime=time.time_ns()   
    
    #setting session time
    zabbix_data["session"]=randstr()
    #putting data into the zabbix packet
    for item in zabbix_data["data"]:
        item["clock"]=epoch
        item["ns"]=nstime
        key=item["key"].split(".")[2]
        item["value"]=data[key]

    #return content of packet that should be sent to zabbix server
    #print(b"ZBXD\1" + struct.pack("<II", len(str(json.dumps(zabbix_data))), 0) + str(json.dumps(zabbix_data)))
    return b"ZBXD\1" + struct.pack("<II", len(str(json.dumps(zabbix_data))), 0) + str(json.dumps(zabbix_data))


#this function sends data to the zabbix server
def t_zabbix_active(ip, pushtime):
    
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("connecting to zabbix")
        try:
            s.connect((ip, 10051))
            s.send(build_packet())
            out=s.recv(4096)
            print("Zabbix server response: ",out)
        except:
            print("error sending data to the zabbix server")
        s.close()
        print("zabbix connection closed")
        #customize sleep time here before next data sent to zabbix
        time.sleep(pushtime)

            
#read configuration for the application so it does not need to use predefined values in a code
def read_the_config():
    global config
    with open("setup.json") as json_data_file:
        config = json.load(json_data_file)
    #set basic variables
    for tab in range(len(zabbix_data["data"])):
        zabbix_data["data"][tab]["host"]=config["nodename"]

#this is main function providing HTTP server capability
def t_web_server(ip):
    address = (ip, 80)
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    try:
        connection = socket.socket()
        connection.bind(addr)
        connection.listen(1)
        print(connection)
    except:
        print("Port 80 not yet released by kernel. Reseting...")
        machine.reset()
        return

    
    while True:
        print("Web server is waiting for connection")
        client, client_addr = connection.accept()
        print("Incoming connection from:", str(client_addr))
        try:
            print("handling the client request")
            request = client.recv(2048)
            print("getting client data")
            process_http_request(request, client)
            print("handling done")
        except:
            print("ERROR: unable to handle the client")
        print("Closing connection to:", str(client_addr))
        client.close()
    print("exiting")
    return

#this function process received buffer and serves a web files from WWW folder
def process_http_request(buffer, client_sock):
    print("debug")
    buf=buffer.decode("utf-8")
    #spliting buffer to extraxt first line from HTTP header - parsing header
    header=buf.split('\r\n')		#split HTML header into separate lines that can be processed and where proper header element can be found
    header_url=header[0].split(" ")	#split first line from client request such as GET http://www.com/section/page.html HTTP/1.1
    HTML_METHOD=header_url[0]			#GET POST PUT etc
    FILE_PATH=header_url[1]				#section/page.html
    HTTP_code=200
    print("processing:",FILE_PATH)
    ext=(FILE_PATH.rpartition(".")[2]).lower()
    
    if ext=="css":
        content_type="text/css"
    elif ext=="jpg" or ext=="jpeg":
        content_type="image/jpeg"
    elif ext=="gif":
        content_type="image/gif"
    elif ext=="png":
        content_type="image/png"
    elif ext=="ico":
        content_type="image/x-icon"
    else:
        content_type="text/html"

    if FILE_PATH=="/api":
        print("this is API")
        page=json.dumps(data)
        fileSize=len(page)
        
        if HTTP_code >=200 and HTTP_code<300:
            client_sock.send('HTTP/1.1 '+str(HTTP_code)+' OK\r\nContent-type: '+content_type+'\r\nServer: latechLite\r\nContent-Length:'+str(fileSize)+'\r\n\r\n')
            client_sock.send(page)
    else:
        if not FILE_PATH or FILE_PATH=="/":
            FILE_PATH="/www/index.html"
        else:
            FILE_PATH="/www/"+FILE_PATH

        try:
            print("trying to open a file: ",FILE_PATH)
            f=open(FILE_PATH,"rb")
        except:
            print("failed to open a file: ", FILE_PATH)
            FILE_PATH="/www_err/err404.html"
            HTTP_code=404
            f=open(FILE_PATH,"rb")
        
        fileSize=uos.stat(FILE_PATH)[6]
            
        print("sending back")
        if HTTP_code >=200 and HTTP_code<300:
            client_sock.send('HTTP/1.1 '+str(HTTP_code)+' OK\r\nContent-type: '+content_type+'\r\nServer: latechLite\r\nContent-Length:'+str(fileSize)+'\r\n\r\n')
        else:
            client_sock.send('HTTP/1.1 '+str(HTTP_code)+' Not Found\r\nContent-type: '+content_type+'\r\nServer: latechLite\r\nContent-Length:'+str(fileSize)+'\r\n\r\n')
        print("sending file")
        client_sock.send(f.read())
        print("closing file")
        f.close()
    return


###############
#I2C init for sensors readout
SCL_PIN=machine.Pin(11)
SDA_PIN=machine.Pin(12)
i2c=machine.I2C(0,scl=SCL_PIN, sda=SDA_PIN,freq=400000)

#getting basic config settings
read_the_config()
global config
print(config)

#base variables that are not within config - and should not be
WiFi_conn_err_count=0
WEB_FOLDER="/www/"

#setting up WiFi
global wlan
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['SSID'], config['PASSWORD'])
while wlan.isconnected() == False:
    print('Waiting for WiFi connection...')
    time.sleep(1)
ip = wlan.ifconfig()[0]
print(f'Wifi connected on {ip}')

#init hardware
ens=myENS160(i2c)
VEML=myVEML7700(i2c)
bme=BME280(i2c=i2c)
VEML.setGain(VEML7700_ALS_GAIN_1_8)
VEML.setALS(VEML7700_ALS_100MS)

#initiate collecting data thread
_thread.start_new_thread(t_web_server, (ip,) )
_thread.start_new_thread(t_zabbix_active, (config["zabbix_server"],config["pushtime"]) )

while True:

    try:
        data["AQI"]=ens.getAQI()
        data["TVOC"]=ens.getTVOC()
        data["eCO2"]=ens.getECO2()
        data["lux"]=round(VEML.getLuxAls(),1)
        data["temp"]=round(bme.temperature,1)+config["temp_corr"]
        data["hum"]=round(bme.humidity,1)+config["hum_corr"]
        data["pressure"]=bme.pressure
    except:
        print("Unable to pull data from the HW sensors.")
    
    print("AQI=",data["AQI"],", TVOC=",data["TVOC"],", eCO2=",data["eCO2"],"lux=",data['lux'],"temp=",data["temp"],"hum=",data["hum"],"pressure",data["pressure"])
    #data["lux"]=round(VEML.getLuxAls(),1)
    #Wdata=aht.getWeather()
    
    
    if wlan.isconnected() == True:
        time.sleep(1)
    else:
        WiFi_conn_err_count+=1
        print('Ops! Lost WiFi, count=', WiFi_conn_err_count)
    if WiFi_conn_err_count>10:
        machine.reset()          
    time.sleep(1)
    

#this is side info not much related to the code
#https://www.sitepoint.com/get-url-parameters-with-javascript/
