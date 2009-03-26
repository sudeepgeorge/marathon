#This script is used along with SendSerial.py . It is used to read the data that is sent over
#serial port by the WiReach module and displays it to the user.
 
 
import serial
import datetime
 
COM_PORT=4
d={}
 
# Windows -
master_port=serial.Serial(COM_PORT)
master_port.open()
 
 
while True:
    try:
        #read_size = master_port.inWaiting()
        #sys.stdout.flush()
        #response = master_port.read(8)
        #sys.stdout.write(response) # This avoids the insertion of \n or ' ' by print command.
        
        packet=master_port.read(8)
        now=datetime.datetime.now().strftime("%H:%M:%S")
        if (packet[0]=='*') and (packet[1]=='T') and (packet[5]=='#'):
            
            if (packet[2]=='A') and (packet[3]=='G'):
                pass
            else:
                id=int(packet[2:5])
                d[id]=now
                print d
        
        
 
    except KeyboardInterrupt: #Ctrl-C
        print "\nUser has closed the script."
        break
      
    except EOFError: # Ctrl-Z
        print "\nUser has closed the script."
        break
 
 
master_port.close()
 