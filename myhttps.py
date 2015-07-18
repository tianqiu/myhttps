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

def dealdir(path):
    ff=os.popen("python dealdir.py "+cwd+' '+path).read()
    head="HTTP/1.1 200 OK\r\n"
    head+="Date:"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) +"\r\n"
    head+="Server:server of qiutian\r\n"
    head+="Content-Length:"+str(len(ff))+"\r\n"
    head+="Content-Type: text/html\r\n\r\n"
    return head+ff

def dealphpbak(path,url,method,request,types):
    if method=='GET':
        if len(url.split('?'))>1:
            can=url.split('?')[1]
            cann=can.split('&')
            a=[i.split('=')[1] for i in cann]
            b=' '
            i=0
            while i<len(a):
                b=b+' '+a[i]
                i=i+1
        else:
            if types=='py':
                v=os.popen('python '+cwd+path)
            elif types=='c':
                os.system('gcc '+cwd+path+' -o '+cwd+path[0:-2])
                v=os.popen(cwd+path[0:-2]).read()
                os.system('rm '+cwd+path[0:-2]+' -f')
            else:
                v=os.popen(types+' '+cwd+path)
            return v.read()
    else:
        po=request.split('\n\r\n')[1]
        if po!='':
            print "po"
            cann=po.split('&')
            print 'cann'
            a=[i.split('=')[1] for i in cann]
            print a
            b=' '
            i=0
            while i<len(a):
                b=b+' '+a[i]
                i=i+1
            print 'B'

            print b
            if types=='py':
                v=os.popen('python '+cwd+path+b).read()
            elif types=='c':
                os.system('gcc '+cwd+path+' -o '+cwd+path[0:-2])
                v=os.popen(cwd+path[0:-2]+b).read()
                os.system('rm '+cwd+path[0:-2]+' -f')
            else:
                v=os.popen(types+' '+cwd+path+b).read()
            v=urllib.unquote(v)
            return
def dealhtmlbak(path):
    f=open(cwd+path,"rb")
    y=f.read()
    y=header+y
    return
def dealjsbak(path):
    f=open(cwd+path,"rb")
    y=f.read()
    f.close()
    return y
def dealresponsebak(request):
    method=request.split(' ')[0]
    url=request.split(' ')[1]
    path=url.split('?')[0]
    if method=='GET' or method=='POST':
        if path=='/':
            if method=='POST':
                po=request.split('\n\r\n')[1]
                print "po"
                cann=po.split('&')
                print 'cann'
                a=[i.split('=')[1] for i in cann]
                print a
                b=' '
                i=0
                while i<len(a):
                    b=b+' '+a[i]
                    i=i+1
                print b
            f=open("index.html","rb")
            x=header+f.read()
            f.close()
            return x
        else:
            if os.path.exists(cwd+path):
                types=path.split('.')[-1]
                b=' '
                if len(url.split('?'))>1:
                    can=url.split('?')[1]
                    cann=can.split('&')
                    a=[i.split('=')[1] for i in cann]
                    i=0
                    while i<len(a):
                        b=b+' '+a[i]
                        i=i+1
                if path=='/his.txt':
                    if a[0]!='undefined':
                        b=urllib.unquote(b)
                        v=os.system('python sub.py '+b)
                    f=open("his.txt","r")
                    v=f.read()
                    f.close()
                    return v
                if types=='html':
                    return dealhtml(path)
                elif types=='php' or types=='py' or types=='c' or types=='sh':
                    return dealphp(path,url,method,request,types)
                elif (types=='js' or types=='css'):
                    return dealjs(path)
                else:
                    f=open(cwd+path,"rb")
                    x=f.read()
                    f.close()
                    return x
            else:
                f=open("index.html","rb")
                x=header+f.read()
                f.close()
                return x
    else:
        f=open("index.html","rb")
        x=header+f.read()
        f.close()
        return x

def dealresponse(request):
    method=request.split(' ')[0]
    try:
        url=request.split(' ')[1]
        if url[0]!='/' or url[0:3]=="/..":
            return deal400()
        path=url.split('?')[0]
    except:
        return deal400()
    if method!="GET"and"POST"and"HEAD"and"OPTIONS":
        return deal501()
    if method == "GET":
        if os.path.exists(cwd+path):
            if os.path.isdir(cwd+path) and path!='/':
                return dealdir(path)
            else:
                if types == 'html':
                    return dealhtml(path)
        else:
            return deal404()






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
                    httprespones[filenoo]=dealresponse(httprequests[filenoo])
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
                if EOL1 in httprequests[filenoo] or EOL2 in httprequests[filenoo] or True:
                    print('-'*40 + '\n' + httprequests[filenoo])
                    print threading.current_thread().name
                    httprespones[filenoo]=dealresponse(httprequests[filenoo])
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
    for i in range(100):
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
                        connstream[connection.fileno()] = context.wrap_socket(connection, server_side=True,do_handshake_on_connect=True)
                        linkway[connection.fileno()]="https"
                        connections[connection.fileno()] = connection
                        httprequests[connection.fileno()] = b''
                        httprequests[connection.fileno()] = b''
                elif event & select.EPOLLIN:
                    epoll.modify(fileno,select.EPOLLOUT)
                    queue.put(fileno)
                elif event & select.EPOLLHUP:
                    #print 'd'
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