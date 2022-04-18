##################################
# Created on Apr 17, 2022
# @author: lsimmons
##################################
import serial, time, getopt, sys, datetime
import paho.mqtt.client as paho

ver     = "VEDMQTT v1.00 - 04/18/2022"
auth    = "L. Simmons"
github  = "simmonslr"

serPort = "serPort"     # USB Port

mqID    = ver           # MQTT Client ID
mqHost  = "mqHost"      # MQTT Host
mqPort  = "mqPort"      # MQTT Host Port
mqUID   = "mqUID"       # MQTT Host User ID
mqPW    = "mqPW"        # MQTT Host Password
mqTopic = "mqTopic"     # MQTT Topic

freq    = 5             # only send every
pktCnt  = freq          # this many packets

maxChr  = 1000          # max packet size
chrCnt  = 0             # cur chr count

####################################
#                                  #
####################################
class vedirect:

    (WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(4)
    
    ######################################
    def __init__ ( self, serialport ):
        self.serialport = serialport
        self.ser = serial.Serial ( serialport, 19200, timeout=10 )
        self.header1 = str.encode ( '\r' )
        self.header2 = str.encode ( '\n' )
        self.delimiter = str.encode ( '\t' )
        self.key = ''
        self.value = ''
        self.bytes_sum = 0;
        self.state = self.WAIT_HEADER
        self.dict = {}
#       self.dict["vedVer"] = vedVer;

    ######################################
    def input ( self, byte ):

        global chrCnt
        
        chrCnt = chrCnt + 1
        if ( chrCnt > maxChr ):                         # circuit breaker
            print ( "input() error - chr overrun: " + str ( chrCnt ))
            chrCnt = 0
            self.key = ''
            self.value = ''
            self.state = self.WAIT_HEADER
            return ( "Bad Checksum" )

        try:

            if self.state == self.WAIT_HEADER:
                self.bytes_sum += ord ( byte )
                if byte == self.header1:                # CR (/r)
                    self.state = self.WAIT_HEADER
                elif byte == self.header2:              # LF (/n)
                    self.state = self.IN_KEY
                return None

            elif self.state == self.IN_KEY:
                self.bytes_sum += ord(byte)
                if byte == self.delimiter:              # TAB (/t)
                    if (self.key == 'Checksum'):
                        self.state = self.IN_CHECKSUM
                    else:
                        self.state = self.IN_VALUE
                else:
                    self.key += bytes.decode ( byte )
                return None
        
            elif self.state == self.IN_VALUE:
                self.bytes_sum += ord(byte)
                if byte == self.header1:                    # CR (/r)
                    self.state = self.WAIT_HEADER
                    if ( self.valid() ):
                        self.dict[self.key] = self.value;   # set key/value
                    self.key = '';
                    self.value = '';
                else:
                    self.value += bytes.decode ( byte )
                return None
        
            elif self.state == self.IN_CHECKSUM:
                self.bytes_sum += ord ( byte )
                self.key = ''
                self.value = ''
                self.state = self.WAIT_HEADER
                if (self.bytes_sum % 256 == 0):
                    chrCnt = 0
                    self.bytes_sum = 0
                    return self.dict
                else:
                    chrCnt = 0
                    self.bytes_sum = 0
                    return ( "Bad Checksum" )

        except Exception as ex:
            chrCnt = 0
            self.key = ''
            self.value = ''
            self.state = self.WAIT_HEADER
            print ( "input() exception" )
            print ( "Exception: {}".format(type(ex).__name__))
            print ( "Exception: {}".format ( ex ))
            return ( "Bad Checksum" )

    ######################################
    def read_data_callback ( self, callbackFunction ):
        
        while True:
            byte = self.ser.read(1)
            packet = self.input(byte)
            if (packet != None):
                callbackFunction ( packet )
                self.dict = {}
#               self.dict["ver"] = ver;

    ######################################
    def valid ( self ):

        v = True

        if ( ":A" in self.key ):        # async msg
            v = False
        if ( "\\n" in self.key ):       # NL
            v = False
        if ( "\\r" in self.key ):       # CR
            v = False
        if ( "\\t" in self.key ):       # TAB
            v = False
        if ( "x" in self.key ):         # HEX data
            v = False
    
        return v
        
####################################
#                                  #
####################################
def print_data_callback ( data ):

    global pktCnt, freq

    try:
        s = repr ( data )
        print ( str ( pktCnt ) + ": " + s )
        if not ( "Bad Checksum" in s ):
            if ( pktCnt >= freq ):
                mqPost ( data )
                pktCnt = 0
                print ( "==========================================" )    
        else:
            time.sleep ( 1 )

    except Exception as ex:
        print ( "print_data_callback() exception" )
        print ( "Exception: {}".format(type(ex).__name__))
        print ( "Exception: {}".format ( ex ))
        time.sleep ( 1 )

    pktCnt = pktCnt + 1    
    
####################################
#                                  #
####################################
def mqPost ( dic ):

    global serPort, mqID, mqHost, mqPort, mqUID, mqPW, mqTopic

    try:
        print ( dic )
        mq = paho.Client ( mqID )  
        mq.username_pw_set ( mqUID, mqPW )
        mq.connect ( mqHost, int ( mqPort ))
        mq.publish ( mqTopic + "ver",  ver  )
        mq.publish ( mqTopic + "auth", auth )
        mq.publish ( mqTopic + "github", github )
        mq.publish ( mqTopic + "port", serPort )

        dt = datetime.datetime.now()
        mq.publish ( mqTopic + "date", dt.strftime ( '%m/%d/%Y' ))
        mq.publish ( mqTopic + "time", dt.strftime ( '%H:%M:%S.%f' )[:-3] )

        for k, v in dic.items():
            k = k.replace ( "#", "" )
#           print ( k + ": " + v )
            mq.publish ( mqTopic + k, v )

    except Exception as ex:
        print ( "MQTT Exception: {}".format(type(ex).__name__))
        print ( "MQTT Exception: {}".format ( ex ))

####################################
#                                  #
####################################
def getArgs ( argv ):
    
    global serPort, mqHost, mqPort, mqUID, mqPW, mqTopic

    try:
        opts, args = getopt.getopt ( argv,"hs:o:p:u:w:t:", [ "serPort=", "mqHost=", "mqPort=", "mqUID=", "mqPW=", "mqTopic=" ] )
    except getopt.GetoptError:
        print ( "vedirectmqtt.py -s <serPort> -o <mqHost> -p <mqPort> -u <mqUID> -w <mqPW> -t <mqTopic>" )
        sys.exit ( 2 )

    for opt, arg in opts:
        if opt in ( '-h', "--help" ):
            print ( "vedirectmqtt.py -s <serPort> -o <mqHost> -p <mqPort> -u <mqUID> -w <mqPW> -t <mqTopic>" )
            sys.exit()
        elif opt in ("-s", "--serPort"):
            serPort = arg
        elif opt in ("-o", "--mqHost"):
            mqHost = arg
        elif opt in ("-p", "--mqPort"):
            mqPort = arg
        elif opt in ("-u", "--mqUID"):
            mqUID = arg
        elif opt in ( "-w", "--mqPW"):
            mqPW = arg
        elif opt in ( "-t", "--mqTopic" ):
            mqTopic = arg

    return serPort

####################################
#                                  #
####################################
if __name__ == '__main__':

    getArgs ( sys.argv[1:] )

    print ( "===============")
    print ( ver )
    print ( "serPort: " + serPort )
    print ( "mqHost:  " + mqHost  )
    print ( "mqPort:  " + mqPort  )
    print ( "mqUID:   " + mqUID   )
    print ( "mqPW:    " + mqPW    )
    print ( "mqTopic: " + mqTopic )

    ve = vedirect ( serPort )
    ve.read_data_callback ( print_data_callback ) 