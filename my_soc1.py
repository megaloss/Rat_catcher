
import socket
import threading
import random
from PIL import Image



HOST = '192.168.0.86' 
#socket.gethostbyname(socket.gethostname())               
PORT = 5050              # Arbitrary non-privileged port
#DISCONNECT_MESSAGE=''
img=Image.open('map.png')
print ('Map loaded. Size: ', img.size)

# only on this color we can place targets
color = (70,51,52)
connections=[]

# initiating socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))



def broadcast(msg):
    msg=msg.encode('utf-8')
    print ('broadcasting to ',len(connections),' clients')
    for conn in connections:
        #print (conn, msg)
        try:
            conn.sendall(msg)
        except:
            break 


def set_rat(img, color):
    ## setting new target location om img where color is the possible position color
    x_size=img.size[0]
    y_size=img.size[1]
    found = False
    while not found:
        x=random.randint(10,x_size)
        y=random.randint(10,y_size)
        if img.load()[x,y]==color:
            found=True
    print ('set target position at ',x/x_size*100,' : ',y/y_size*100)
    print ('color is ', img.load()[x,y])
    return x/x_size,y/y_size

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    global x,y, color
    connected = True
    while connected:
        data = conn.recv(15)
        if not data:
            print ('I GOT A BREAK !!!') 
            break
        #print ('received:', data)
        data = data.decode('utf-8')
        #print ('prefix is: ',data[0])

        if data[0]=='1':
            # target was destroyed, ititialize new target
            _,player,score = data.split(';')

            # notify everyone who did it
            print (player, ' has got the prey. His score is: ', score)            
            x,y = set_rat(img, color)
            mess= ';'.join (['1',str(x), str(y), player])
            
            # send new target location to all players 
            print('New location of target: ',x*100,':',y*100)                       
            thread = threading.Thread(target=broadcast, args=(mess,))
            thread.start()



        elif data[0]=='0':
            #a new player logged in
            print (data[2:],'joined the game and requesting target position')
            #send target info to a new player 
            mess= ';'.join( ['3', str(x),str(y)])
            print ('...which are:',x*100,'%',y*100,'%')
            conn.sendall(mess.encode('utf-8'))
            
            # and notifying other players
            print ('time to notify everyone')
            mess='2'+';'+data[2:]
            print (mess)
            thread = threading.Thread(target=broadcast, args=(mess,))
            thread.start()


        elif str(data[0]).isalpha():
            # player reported his position
            player, px, py = data.split(';')
            print (player,' moved to position: ',px,py)


    conn.close()
    connections.remove(conn)
    print ('Terminated: ',addr)
        

def start(x,y):
    global connections
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}")
    while True:
        
        conn, addr = server.accept()
        
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        connections += [conn]
        thread.start()
        
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == '__main__':
    print("[STARTING] server is starting...")
    x,y = set_rat(img, color)
    start(x,y)
