import os
import threading
import Queue
import ssl
import socket
import select
import urllib
import time
EOL1=b'\n\n'
EOL2=b'\n\r\n'
cwd=os.getcwd()

def deal200head(path):
    head="HTTP/1.1 200 OK\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+path))+"\r\n"
    return head
def deal400():
    f=open("status/400.html","r")
    ff=f.read()
    f.close()
    head="HTTP/1.1 400 Bad Request\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/400.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal404():
    f=open("status/404.html","r")
    ff=f.read()
    f.close()
    head="HTTP/1.1 404 Not Found\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/404.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal405():
    f=open("status/405.html","r")
    ff=f.read()
    f.close()
    head="HTTP/1.1 405 Method Not Allowed\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/405.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff
def deal501():
    f=open("status/501.html","r")
    ff=f.read()
    f.close()
    head="HTTP/1.1 501 Not Implemented\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(os.path.getsize(cwd+"/status/501.html"))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff

def dealdir(path,method="GET"):
    ff=os.popen("python dealdir.py "+cwd+' '+path).read()
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
    f=open(cwd+path,"r")
    ff=f.read()
    f.close()
    head=deal200head(path)
    head+="Content-Type: text/none\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealhtml(path,mthod="GET"):
    head=deal200head(path)
    head+="Content-Type: text/html\r\n\r\n"
    f=open(cwd+path,"r")
    ff=f.read()
    f.close()
    if method == "HEAD":
        return head
    else:
        return head+ff
def dealphp(path,c,method="GET"):
    ff.popen("php "+cwd+path+" "+c).read()
    head=deal200head()
    head+="Content-Type: text/html\r\n\r\n"
    if method == "HEAD":
        return head
    else:
        return head+ff

def dealcgi(path,types,cgican,method="GET"):
    if types == "py":
        ff=os.popen("python "+cwd+path+" "+cgican).read()
    elif types == "pl" or "pm" or "perl":
        ff=os.popen("perl "+cwd+path+" "+cgican).read()
    elif types == "php":
        ff=os.popen("php "+cwd+path+" "+cgican).read()
    else:
        try:
            ff=os.popen("."+cwd+path+" "+cgican).read()
        except:
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
    except:
        return deal400()
    if method!="GET"and"POST"and"HEAD"and"OPTIONS"and"TRACE":
        return deal501()
    if url == '/':
        f=open(cwd+"/index.html")
        ff=f.read()
        f.close()
        head=deal200head("/index.html")
        head+="Content-Type: text/html\r\n\r\n"
        return head+ff

    #WHEN THR WAY IS "GET" or "HEAD":
    if method == "GET" or "HEAD":
        if os.path.exists(cwd+path):
            print cwd+path
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
                    print filename.split('.')
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
                    f=open(cwd+path,"r")
                    ff=f.read()
                    f.close()
                    return ff
        else:
            return deal404()

    #WHEN THE WAY IS "POST":
    if method == "POST":
        if os.path.exists(cwd+path):
            print cwd+path
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
                    f=open(cwd+path,"r")
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
            except:
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
            filenoo=self._queue.get()
            ##WHEN THE WAY IS HTTPS:
            if linkway[filenoo] == "https":
                try:
                    #print filenoo
                    connstream[filenoo].do_handshake()
                    httprequests[filenoo] = connstream[filenoo].recv(1024)
                except ssl.SSLWantReadError:
                    print 'wantread'
                except:
                    pass
                if httprequests[filenoo]=='':
                    epoll.unregister(filenoo)
                if EOL1 in httprequests[filenoo] or EOL2 in httprequests[filenoo]:
                    print('-'*40 + '\n' + httprequests[filenoo])
                    try:
                        httprespones[filenoo]=dealresponse(httprequests[filenoo])
                    except:
                        httprespones[filenoo]=''
                print 'c'
                try:
                    connstream[filenoo].do_handshake()
                    byteswritten = connstream[filenoo].send(httprespones[filenoo])
                    httprespones[filenoo] = httprespones[filenoo][byteswritten:]
                    epoll.modify(filenoo, 0)
                except ssl.SSLWantWriteError:
                    print ("wanterror")
                except:
                    pass

            ##WHEN THE WAY IS HTTP:
            elif linkway[filenoo] == "http":
                try:
                    httprequests[filenoo] = connections[filenoo].recv(1024)
                except:
                    pass
                print httprequests[filenoo]
                if httprequests[filenoo]=='':
                    epoll.unregister(filenoo)
                if EOL1 in httprequests[filenoo] or EOL2 in httprequests[filenoo] or:
                    print('-'*40 + '\n' + httprequests[filenoo])
                    print threading.current_thread().name
                    try:
                        httprespones[filenoo]=dealresponse(httprequests[filenoo])
                    except:
                        httprespones[filenoo]=''
                if httprequests[filenoo]=='':
                    epoll.unregister(filenoo)
                try:
                    byteswritten = connections[filenoo].send(httprespones[filenoo])
                    httprespones[filenoo] = httprespones[filenoo][byteswritten:]
                except:
                    pass
                try:
                    epoll.modify(filenoo, 0)
                except:
                    pass

            #SHUTDOWN:
            try:
                connstream[fileno].shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                connections[fileno].shutdown(socket.SHUT_RDWR)
            except:
                pass
            self._queue.task_done()





if __name__=="__main__":
    queue=Queue.Queue()
    for i in range(1):
        t=Thread(queue)
        t.setDaemon(True)
        t.start()
    context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    serversockets = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversockets.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversockets.bind(('127.0.0.1', 443))
    serversockets.listen(100)
    serversockets.setblocking(0)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('127.0.0.1', 883))
    serversocket.listen(100)
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
        while True:
            events=epoll.poll(1)
            for fileno,event in events:
                #print events
                if event & select.EPOLLOUT:
                    pass
                elif fileno == serversockets.fileno() or fileno == serversocket.fileno():
                    print 'a'
                    if fileno == serversocket.fileno():
                        connection,address=serversocket.accept()
                        epoll.register(connection.fileno(),select.EPOLLIN)
                        linkway[connection.fileno()]="http"
                        connections[connection.fileno()] = connection
                        httprequests[connection.fileno()] = b''
                        httprequests[connection.fileno()] = b''
                    else:
                        connection,address=serversockets.accept()
                        epoll.register(connection.fileno(),select.EPOLLIN)
                        try:
                            connstream[connection.fileno()] = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=True)
                            linkway[connection.fileno()]="https"
                            connections[connection.fileno()] = connection
                            httprequests[connection.fileno()] = b''
                            httprequests[connection.fileno()] = b''
                        except:
                            epoll.modify(connection.fileno(),0)
                            epoll.unregister(connection.fileno())
                            connection.shutdown(socket.SHUT_RDWR)
                            connection.close()
                elif event & select.EPOLLIN:
                    print 'b'
                    epoll.modify(fileno,select.EPOLLOUT)
                    queue.put(fileno)
                elif event & select.EPOLLHUP:
                    print 'd'
                    epoll.unregister(fileno)
                    try:
                        connstream[fileno].close()
                    except:
                        pass
                    connections[fileno].close()
                    del connections[fileno]
                    try:
                        del connstream[fileno]
                    except:
                        pass
                    del linkway[fileno]
    finally:
        print 'e'
        epoll.unregister(serversockets.fileno())
        epoll.close()
        serversockets.close()