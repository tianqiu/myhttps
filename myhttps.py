import os
import threading
import Queue
import ssl
import socket
import select
import urllib
import time
import logging
EOL1=b'\n\n'
EOL2=b'\n\r\n'
cwd="/myhttps/www"
LOG="/myhttps/log.txt"
CERT="/myhttps/cert.pem"
KEY="/myhttps/key.pem"
HTTPIP="127.0.0.1"
HTTPLISTEN=8080
HTTPSIP="127.0.0.1"
HTTPSLISTEN=4433
logging.basicConfig(filename = os.path.join(os.getcwd(), LOG), level = logging.ERROR)

def readconf():
    global cwd,LOG,CERT,KEY,HTTPIP,HTTPLISTEN,HTTPSIP,HTTPSLISTEN
    try:
        f=open("myhttps.conf","r")
        conf=f.read()
        f.close()
    except:
        pass
    try:
        PATHconf=conf.split("PATH{")[-1]
        PATHconf=PATHconf.split("}")[0]
        PATHconf=PATHconf.split("\n")[1:-1]
        for i in PATHconf:
            name=i.split(":")[0]
            path=i.split(":")[1]
            if name == "CWD":
                cwd=path
            elif name == "LOG":
                LOG=path
            elif name == "CERT":
                CERT=path
            elif name == "KEY":
                KEY=path
    except Exception,e:
        logging.error(e)
    try:
        HTTPconf=conf.split("HTTP{")[-1]
        HTTPconf=HTTPconf.split("}")[0]
        HTTPconf=HTTPconf.split("\n")[1:-1]
        for i in HTTPconf:
            name=i.split(":")[0]
            path=i.split(":")[1]
            if name == "IP":
                HTTPIP=path
            elif name == "LISTEN":
                HTTPLISTEN=int(path)

    except Exception,e:
        logging.error(e)

    try:
        HTTPSconf=conf.split("HTTPS{")[-1]
        HTTPSconf=HTTPSconf.split("}")[0]
        HTTPSconf=HTTPSconf.split("\n")[1:-1]
        for i in HTTPSconf:
            name=i.split(":")[0]
            path=i.split(":")[1]
            if name == "IP":
                HTTPSIP=path
            elif name == "LISTEN":
                HTTPSLISTEN=int(path)

    except:
        pass

    try:
        Rconf=conf.split("R{")[-1]
        Rconf=Rconf.split("}")[0]
        Rconf=Rconf.split("\n")[1:-1]
        Wconf=conf.split("W{")[-1]
        Wconf=Wconf.split("}")[0]
        Wconf=Wconf.split("\n")[1:-1]
        Xconf=conf.split("X{")[-1]
        Xconf=Xconf.split("}")[0]
        Xconf=Xconf.split("\n")[1:-1]
        Sconf=conf.split("S{")[-1]
        Sconf=Sconf.split("}")[0]
        Sconf=Sconf.split("\n")[1:-1]
    except:
        return

    #R
    for i in Rconf:
        try:
            path=i.split(":")[0]
            types=i.split(":")[1]
            types=types.split(" ")
            files=os.popen("ls "+cwd+path).read()
            files=files.split("\n")[0:-1]
            files=filter(lambda n:os.path.isdir(cwd+path+"/"+n) == False,files)
            for file in files:
                try:
                    os.system("chmod 000 "+cwd+path+"/"+file)
                except:
                    pass
            for file in files:
                type=file.split(".")[-1]
                if type in types:
                    os.system("chmod u+r "+cwd+path+"/"+file)
        except:
            pass
    #W
    for i in Wconf:
        try:
            path=i.split(":")[0]
            types=i.split(":")[1]
            types=types.split(" ")
            files=os.popen("ls "+cwd+path).read()
            files=files.split("\n")[0:-1]
            files=filter(lambda n:os.path.isdir(cwd+path+"/"+n) == False,files)
            for file in files:
                type=file.split(".")[-1]
                if type in types:
                    os.system("chmod u+w "+cwd+path+"/"+file)
        except:
            pass

    #X
    for i in Xconf:
        try:
            path=i.split(":")[0]
            types=i.split(":")[1]
            types=types.split(" ")
            files=os.popen("ls "+cwd+path).read()
            files=files.split("\n")[0:-1]
            files=filter(lambda n:os.path.isdir(cwd+path+"/"+n) == False,files)
            for file in files:
                type=file.split(".")[-1]
                if type in types:
                    os.system("chmod u+x "+cwd+path+"/"+file)
        except:
            pass

    #S
    for i in Sconf:
        try:
            path=i.split(":")[0]
            num=i.split(":")[1]
            os.system("chmod "+num+" "+cwd+path)
        except:
            pass


def deal200head(path):
    head="HTTP/1.1 200 OK\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+path))+"\r\n"
    return head
def deal400():
    try:
        f=open(cwd+"/status/400.html","r")
    except:
        if os.path.exists(cwd+"/status/400.html"):
            return deal403()
        else:
            return deal404()
    ff=f.read()
    f.close()
    head="HTTP/1.1 400 Bad Request\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/400.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal404():
    try:
        f=open(cwd+"/status/404.html","r")
    except:
        if os.path.exists(cwd+"/status/404.html"):
            return deal403()
        else:
            return deal404()
    ff=f.read()
    f.close()
    head="HTTP/1.1 404 Not Found\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/404.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal403():
    try:
        f=open(cwd+"/status/403.html","r")
    except:
        if os.path.exists(cwd+"/status/403.html"):
            return deal403()
        else:
            return deal404()
    ff=f.read()
    f.close()
    head="HTTP/1.1 403 Forbidden\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/403.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal405():
    try:
        f=open(cwd+"/status/405.html","r")
    except:
        if os.path.exists(cwd+"/status/405.html"):
            return deal403()
        else:
            return deal404()
    ff=f.read()
    f.close()
    head="HTTP/1.1 405 Method Not Allowed\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/405.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal501():
    try:
        f=open(cwd+"/status/501.html","r")
    except:
        if os.path.exists(cwd+"/status/501.html"):
            return deal403()
        else:
            return deal404()
    ff=f.read()
    f.close()
    head="HTTP/1.1 501 Not Implemented\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/501.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff

def dealdir(path,method="GET"):
    ff=os.popen("python "+cwd+"/dealdir.py "+cwd+' '+path).read()
    head="HTTP/1.1 200 OK\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(len(ff))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealnone(path,method="GET"):
    print "dead"
    try:
        f=open(cwd+path,"r")
    except:
        return deal403()
    ff=f.read()
    f.close()
    head=deal200head(path)
    head+="Content-Type: text/none\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealhtml(path,method="GET"):
    head=deal200head(path)
    head+="Content-Type: text/html\r\n\r\n"
    try:
        f=open(cwd+path,"r")
    except:
        return deal403()
    ff=f.read()
    f.close()
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealphp(path,c,method="GET"):
    try:
        ff.popen("php "+cwd+path+" "+c).read()
    except:
        return deal403()
    head=deal200head()
    head+="Content-Type: text/html\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealcgi(path,types,cgican,method="GET"):
    if types == "py":
        try:
            ff=os.popen("python "+cwd+path+" "+cgican).read()
        except:
            return deal403()
    elif types == "pl" or "pm" or "perl":
        try:
            ff=os.popen("perl "+cwd+path+" "+cgican).read()
        except:
            return deal403()
    elif types == "php":
        try:
            ff=os.popen("php "+cwd+path+" "+cgican).read()
        except:
            return deal403()
    else:
        try:
            ff=os.popen("."+cwd+path+" "+cgican).read()
        except Exception,e:
            logging.error(e)
            f=open(cwd+path,"r")
            ff=f.read()
            f.close()
    head=deal200head(path)
    head+="Content-Type: text/html\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff

def dealresponse(request):
    method=request.split(' ')[0]
    try:
        url=request.split(' ')[1]
        if url[0]!='/' or url[0:3]=="/..":
            return deal400()
        path=url.split('?')[0]
    except Exception,e:
        logging.error(e)
        return deal400()
    if method!="GET"and"POST"and"HEAD"and"OPTIONS"and"TRACE":
        return deal501()
    if url == '/':
        try:
            f=open(cwd+"/index.html")
        except:
            return deal403()
        ff=f.read()
        f.close()
        head=deal200head("/index.html")
        head+="Content-Type: text/html\r\n\r\n"
        return head+ff

    #WHEN THR WAY IS "GET" or "HEAD":
    if method == "GET" or "HEAD":
        if os.path.exists(cwd+path):
            if os.path.isdir(cwd+path) and path!='/':
                return dealdir(path,method)
            else:
                c = ' '
                cgican = ' '
                if len(url.split('?'))>1 and url.split('?')[1]!='':
                    can=url.split('?')[1]
                    cgican=can.replace("&","\&")
                    cann=can.split('&')
                    a=[i.split('=')[1] for i in cann]
                    i=0
                    while i<len(a):
                        c=c+' '+a[i]
                        i=i+1

                filename=path.split('/')[-1]
                if len(filename.split('.'))>1:
                    types=filename.split('.')[-1]
                else:
                    types="none"
                if len(path)>9 and path[0:9] == "/cgi-bin/":
                    return dealcgi(path,types,cgican,method)
                elif types == "none":
                    return dealnone(path,method)
                elif types == 'html':
                    return dealhtml(path,method)
                elif types == 'php':
                    return dealphp(path,c,method)
                else:
                    try:
                        f=open(cwd+path,"r")
                    except:
                        return deal403()
                    ff=f.read()
                    f.close()
                    return ff
        else:
            return deal404()

    #WHEN THE WAY IS "POST":
    if method == "POST":
        if os.path.exists(cwd+path):
            if os.path.isdir(cwd+path) and path!='/':
                return dealdir(path)
            else:
                c = ' '
                cgican = ' '
                if len(request.split('\n\r\n'))>1 and request.split('\n\r\n')[1]!='':
                    can=request.split('\n\r\n')[1]
                    cgican=can.replace("&","\&")
                    cann=can.split('&')
                    a=[i.split('=')[1] for i in cann]
                    i=0
                    while i<len(a):
                        c=c+' '+a[i]
                        i=i+1

                filename=path.split('/')[-1]
                if len(filename.split('.'))>1:
                    types=filename.split('.')[-1]
                    print filename.split('.')
                else:
                    types="none"
                if len(path)>9 and path[0:9] == "/cgi-bin/":
                    return dealcgi(path,types,cgican)
                elif types == "none":
                    return dealnone(path)
                elif types == 'html':
                    return dealhtml(path)
                elif types == 'php':
                    return dealphp(path,c)
                else:
                    try:
                        f=open(cwd+path,"r")
                    except:
                        return deal403()
                    ff=f.read()
                    f.close()
                    return ff
        else:
            return deal404()

    #WHEN THE WAY IS "DELETE":
    if method == "DELETE":
        if os.path.exists(cwd+path):
            try:
                if os.path.isdir(cwd+path):
                    os.system("rm -Rf "+cwd+path)
                else:
                    os.system("rm -f "+cwd+path)
            except Exception,e:
                logging.error(e)
                return deal405()
        else:
            return deal404()

    #WHEN THE WAY IS "TRACE":
    if method == "TRACE":
        head=deal200head()
        head+="Content-Type: message/http"
        return head+request




class Thread(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self._queue=queue
    def run(self):
        while True:
            filenoo,eventt=self._queue.get()

            ##WHEN THE WAY IS HTTPS:
            if linkway[filenoo] == "https" or False:
                if eventt & select.EPOLLMSG:
                    while True:
                        try:
                            try:
                                connections[filenoo].setblocking(1)
                                connstream[filenoo].setblocking(1)
                               # print 'do11'
                                connstream[filenoo].do_handshake()
                                #print 'do'
                            except Exception,e:
                                logging.error(e)
                            connections[filenoo].setblocking(0)
                            connstream[filenoo].setblocking(0)
                            aa=connstream[filenoo].recv(1024)
                            httprequests[filenoo] += aa
                            break
                        except ssl.SSLWantReadError,e:
                            #print "wantread"
                            logging.error(e)
                        except Exception,e:
                            #print "readelse"
                            logging.error(e)
                            break
                    if EOL1 in httprequests[filenoo] or EOL2 in httprequests[filenoo]:
                        #print('-'*40 + '\n' + httprequests[filenoo])
                        try:
                            httprespones[filenoo]=dealresponse(httprequests[filenoo])
                            epoll.modify(filenoo,select.EPOLLOUT)
                        except Exception,e:
                            logging.error(e)
                            httprespones[filenoo]=''
                    else:
                        if httprequests[filenoo]=='' or aa == '' or EOL1 in aa or EOL2 in aa:
                            try:
                                epoll.modify(filenoo,0)
                            except:
                                pass
                        else:
                            try:
                                epoll.modify(filenoo,select.EPOLLIN)
                            except:
                                pass
                    #print 'c'
                elif eventt & select.EPOLLPRI:
                    while True:
                        try:
                            connections[filenoo].setblocking(1)
                            connstream[filenoo].setblocking(1)
                            connstream[filenoo].do_handshake()
                            connections[filenoo].setblocking(0)
                            connstream[filenoo].setblocking(0)
                            byteswritten[filenoo] = connstream[filenoo].send(httprespones[filenoo])
                            httprespones[filenoo] = httprespones[filenoo][byteswritten[filenoo]:]
                            break
                        except ssl.SSLWantWriteError,e:
                            print "wantwrite"
                            logging.error(e)
                        except Exception,e:
                            print "writeelse"
                            try:
                                connections[filenoo].setblocking(0)
                                connstream[filenoo].setblocking(0)
                            except Exception,e:
                                logging.error(e)
                            logging.error(e)
                    if len(httprespones[filenoo]) == 0:
                        try:
                            epoll.modify(filenoo,0)
                        except:
                            pass
                        try:
                            connstream[filenoo].shutdown(socket.SHUT_RDWR)
                            connections[filenoo].shutdown(socket.SHUT_RDWR)
                        except Exception,e:
                            logging.error(e)
                    else:
                        try:
                            epoll.modify(filenoo,select.EPOLLOUT)
                        except:
                            pass

            ##WHEN THE WAY IS HTTP:
            elif linkway[filenoo] == "http" or False:
                if eventt & select.EPOLLMSG:
                    #while True:
                    try:
                        aa=connections[filenoo].recv(1024)
                    except:
                        pass
                    httprequests[filenoo] += aa
                    if EOL1 in httprequests[filenoo] or EOL2 in httprequests[filenoo]:
                        #print('-'*40 + '\n' + httprequests[filenoo])
                        try:
                            httprespones[filenoo]=dealresponse(httprequests[filenoo])
                            epoll.modify(filenoo,select.EPOLLOUT)
                        except Exception,e:
                            print "fopenerror"
                            logging.error(e)
                            httprespones[filenoo]=''
                    else:
                        if httprequests[filenoo]=='' or aa == '' or EOL1 in aa or EOL2 in aa:
                            epoll.modify(filenoo,0)
                        else:
                            try:
                                epoll.modify(filenoo,select.EPOLLIN)
                            except:
                                pass

                elif eventt & select.EPOLLPRI:
                    #print 'o'
                    #while True:
                    try:
                        byteswritten[filenoo] = connections[filenoo].send(httprespones[filenoo])
                    except:
                        pass
                    httprespones[filenoo] = httprespones[filenoo][byteswritten[filenoo]:]
                    if len(httprespones[filenoo]) == 0:
                        try:
                            epoll.modify(filenoo, 0)
                        except:
                            pass
                        try:
                            connections[filenoo].shutdown(socket.SHUT_RDWR)
                        except:
                            pass
                    else:
                        try:
                            epoll.modify(filenoo,select.EPOLLOUT)
                        except:
                            pass
                self._queue.task_done()





if __name__=="__main__":
    readconf()
    queue=Queue.Queue()
    for i in range(500):
        t=Thread(queue)
        t.setDaemon(True)
        t.start()
    print "thread finished"
    context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile=CERT, keyfile=KEY)
    serversockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversockets.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversockets.bind((HTTPSIP, HTTPSLISTEN))
    serversockets.listen(20000)
    serversockets.setblocking(0)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((HTTPIP, HTTPLISTEN))
    serversocket.listen(20000)
    serversocket.setblocking(0)
    epoll = select.epoll()
    epoll.register(serversockets.fileno(), select.EPOLLIN)
    epoll.register(serversocket.fileno(), select.EPOLLIN)
    try:
        connections={}
        httprequests={}
        httprespones={}
        connstream={}
        linkway={}
        byteswritten={}
        while True:
            events=epoll.poll(1)
            for fileno,event in events:
                if event & select.EPOLLPRI:
                    pass
                elif event & select.EPOLLMSG:
                    pass
                elif fileno == serversockets.fileno() or fileno == serversocket.fileno():
                    #print 'a'
                    if fileno == serversocket.fileno():
                        connection,address=serversocket.accept()
                        connection.setblocking(0)
                        epoll.register(connection.fileno(),select.EPOLLIN)
                        linkway[connection.fileno()]="http"
                        connections[connection.fileno()] = connection
                        httprequests[connection.fileno()] = b''
                        httprespones[connection.fileno()] = b''
                    else:
                        connection,address=serversockets.accept()
                        epoll.register(connection.fileno(),select.EPOLLIN)
                        try:
                            connstream[connection.fileno()] = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=False)
                            linkway[connection.fileno()]="https"
                            connection.setblocking(0)
                            connstream[connection.fileno()].setblocking(0)
                            connections[connection.fileno()] = connection
                            httprequests[connection.fileno()] = b''
                            httprespones[connection.fileno()] = b''
                        except Exception,e:
                            logging.error(e)
                            epoll.modify(connection.fileno(),0)
                            epoll.unregister(connection.fileno())
                            connection.shutdown(socket.SHUT_RDWR)
                            connection.close()
                elif event & select.EPOLLIN:
                    #print 'b'
                    epoll.modify(fileno,select.EPOLLMSG)
                    queue.put((fileno,select.EPOLLMSG))
                elif event & select.EPOLLOUT:
                    #print 'c'
                    epoll.modify(fileno,select.EPOLLPRI)
                    queue.put((fileno,select.EPOLLPRI))
                elif event & select.EPOLLHUP:
                    #print 'd'
                    epoll.unregister(fileno)
                    try:
                        connstream[fileno].close()
                    except Exception,e:
                        logging.error(e)
                    connections[fileno].close()
                    del connections[fileno]
                    try:
                        del connstream[fileno]
                    except Exception,e:
                        logging.error(e)
                    del linkway[fileno]
    finally:
        print 'e'
        epoll.unregister(serversockets.fileno())
        epoll.close()
        serversockets.close()