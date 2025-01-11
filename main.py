import network
import socket
import machine
import json
import urandom
import time
import uos
import _thread

data={
    "temp": 0.0,
    "hum": 0.0,
    "AQI": 0,
    "TVOC": 0,
    "eCO2": 0,
    "lux": 0,
    "pressure": 0.0}

#read configuration for the application so it does not need to use predefined values in a code
def read_the_config():
    global config
    with open("setup.json") as json_data_file:
        config = json.load(json_data_file)


#this is main function providing HTTP server capability
def t_web_server(ip):
    address = (ip, 80)
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    
    connection = socket.socket()
    connection.bind(addr)
    connection.listen(1)
    print(connection)
    
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
read_the_config()
global config
print(config)

#variables
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

#initiate collecting data thread
_thread.start_new_thread(t_web_server, (ip,) )

while True:
    
    if wlan.isconnected() == True:
        time.sleep(1)
    else:
        WiFi_conn_err_count+=1
        print('Ops! Lost WiFi, count=', WiFi_conn_err_count)
    if WiFi_conn_err_count>10:
        machine.reset()          
    time.sleep(1)
    



#https://www.sitepoint.com/get-url-parameters-with-javascript/
