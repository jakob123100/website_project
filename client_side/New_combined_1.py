#import os, glob, time, datetime, pickle
import os, time, datetime
#pip install minimalmodbus
import minimalmodbus
from api import datebase_inteface


dt = datetime.datetime.now()

Y_m_d="{:%Y_%m_%d}".format(dt)
Y_m="{:%Y_%m}".format(dt)
day_flag="{:%d}".format(dt)
month_flag="{:%m}".format(dt)
print ("Y_m_d",Y_m_d)
print ("day_flag", day_flag)
print ("month_flag", month_flag)

day_flag=0
log_period = 60 # seconds

#device_folder = "apa"
#device_file = device_folder + '/w1_slave'

#print ('{:%H:%M:%S},'.format(dt))

#day_data_list=[0]*10

# setings for temp
# These tow lines mount the device:
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
time.sleep(1)
temp_sensors=["28-02161673c3ee","28-00000a9e2e4a","28-00000a9eb0eb","28-00000a9dfdc5","28-00000a9e4f27"]

temp_c=[0]*len(temp_sensors)
base_dir ='/sys/bus/w1/devices/'

# Import Adafruit IO REST client.
from Adafruit_IO import Client, Feed, Data, RequestError
import datetime

ADAFRUIT_IO_KEY = 'aio_xWQJ24adS5QNaiZaz8Lmg3E3rHMG'
ADAFRUIT_IO_USERNAME = 'Zalongou'

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

#aio.send_data(temperature.key, 25)
# works the same as send now
#aio.append(temperature.key, 26)

def read_temp_raw(device_file):
    try:
        
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
    except IOError:
        print ("can not read file",device_file)
        lines = ('e7 00 4b 46 7f ff 0c 10 6b : crc=6b YES\n', 'e7 00 4b 46 7f ff 0c 10 6b t=-273000\n')
    return lines

def read_temp(temp_sensor):
    device_folder = (base_dir + temp_sensor)
    device_file = device_folder + '/w1_slave'   
#    lines = read_temp_raw(device_file)
      
    # Analyze if the last 3 characters are 'YES'.
    count=0
    while (count < 6):
        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        print ("lines", temp_sensor, lines)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            print ("count, temp_c", count, temp_c)
        if temp_c != 85:
            if temp_c != 127.937:
                count = 6
        count=count+1       
    return temp_c

def get_ABB_1(x):
#   client = ModbusClient(method='rtu', port='/dev/ttyUSB0', stopbits=1, bytesize=8, parity='N', baudrate=9600, timeout=0.3)
#   connection = client.connect()

    
    ABB_1 = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
    ABB_1.serial.baudrate = 9600         # Baud
    ABB_1.serial.timeout  = 0.3
    ABB_1.close_port_after_each_call = True
    time.sleep(0.2)
#    print(connection)
#0 Active import kWh 5000 4 0,01 kWh Unsigned
#1 Active export kWh 5004 4 0,01 kWh Unsigned
#2 Active net kWh 5008 4 0,01 kWh Signed

#3 Resettable active import 552C 4 0,01 kWh Unsigned
#4 Resettable active export 5530 4 0,01 kWh Unsigned

#5 Voltage L1-N 5B00 2 0,1 V Unsigned
#6 Voltage L2-N 5B02 2 0,1 V Unsigned
#7 Voltage L3-N 5B04 2 0,1 V Unsigned

#8 Current L1 5B0C 2 0,01 A Unsigned
#9 Current L2 5B0E 2 0,01 A Unsigned
#10 Current L3 5B10 2 0,01 A Unsigned

#11 Active power Total 5B14 2 0,01 W Signed
#12 Active power L1 5B16 2 0,01 W Signed
#13 Active power L2 5B18 2 0,01 W Signed
#14 Active power L3 5B1A 2 0,01 W Signed

#15 Frequency 5B2C 1 0,01 Hz Unsigned
    abb_data=[0]*34
    abb_full_data=[0]*68
    abb_register=[0]*170
    a=[0]*4
#    device=1
    b=0
    
    abb_register=["Active import kWh","5000",4,"kWh","Unsigned",
                  "Active export kWh","5004",4,"kWh","Unsigned",
                  "Active net kWh","5008",4,"kWh","Signed",
                  "Resettable active import","552C",4,"kWh","Unsigned",
                  "Resettable active export","5530",4,"kWh","Unsigned",
                  "Voltage L1-N","5B00",2,"V","Unsigned",
                  "Voltage L2-N","5B02",2,"V","Unsigned",
                  "Voltage L3-N","5B04",2,"V","Unsigned",
                  "Current L1","5B0C",2,"A","Unsigned",
                  "Current L2","5B0E",2,"A","Unsigned",
                  "Current L3","5B10",2,"A","Unsigned",
                  "Active power Total","5B14",2,"W","Signed",
                  "Active power L1","5B16",2,"W","Signed",
                  "Active power L2","5B18",2,"W","Signed",
                  "Active power L3","5B1A",2,"W","Signed",
                  "Frequency","5B2C",1,"Hz","Unsigned",
                  "Phase angle power Total","5B2D",1,"deg","Signed",
                  "Phase angle power L1","5B2E",1,"deg","Signed",
                  "Phase angle power L2","5B2F",1,"deg","Signed",
                  "Phase angle power L3","5B30",1,"deg","Signed",
                  "Phase angle voltage L1","5B31",1,"deg","Signed",
                  "Phase angle voltage L2","5B32",1,"deg","Signed",
                  "Phase angle voltage L3","5B33",1,"deg","Signed",
                  "Phase angle current L1","5B37",1,"deg","Signed",
                  "Phase angle current L2","5B38",1,"deg","Signed",
                  "Phase angle current L3","5B39",1,"deg","Signed",
                  "Power factor Total","5B3A",1,"–","Signed",
                  "Power factor L1","5B3B",1,"–","Signed",
                  "Power factor L2","5B3C",1,"–","Signed",
                  "Power factor L3","5B3D",1,"–","Signed",
                  "Current quadrant Total","5B3E",1,"-","Unsigned",
                  "Current quadrant L1","5B3F",1,"-","Unsigned",
                  "Current quadrant L2","5B40",1,"-","Unsigned",
                  "Current quadrant L3","5B41",1,"-","Unsigned"]
    
    lenght_abb_reg=len(abb_register)
    s=int(lenght_abb_reg/5)
#    print ("s",s)
    for i in range(0,s):
        p=i*5+0
        text=abb_register[p]
        p=i*5+1
        modbus_reg=abb_register[p]
        p=i*5+2
        number=abb_register[p]
        p=i*5+3
        unit=abb_register[p]
        p=i*5+4
        un_si=abb_register[p]
        
#       print ("hex",int(modbus_reg,16))
#       print ("p",p, abb_register[p])
#       print ("modbus reg", hex(modbus_reg))
#       time.sleep(0.2)
        try:
#           value = client.read_holding_registers(int(modbus_reg,16), number, unit=device)
            a=ABB_1.read_registers(int(modbus_reg,16), number, functioncode=3)
        except IOError:
            print("Failed to read from ABB_1")
#            print('Error message: {}'.format(value))
            b=1
            a=[0,0,0,0]
    
  


#       value = client.read_holding_registers(int(modbus_reg,16), number, unit=device)
#print(client.read_holding_registers(23296, 1, unit=1))

#       if not value.isError():
#            '''isError() method implemented in pymodbus 1.4.0 and later'''
#           a=(value.registers)

#       else:
            # Do stuff to error handling.
#          print('Error message: {}'.format(value))
#          b=1
#       a=(value.registers)
      #  print ("a1",a)
#        abb_data[0]=a[3]
        if modbus_reg == "5B00":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B02":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B04":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B0C":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B0E":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B10":           
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if number == 4 and un_si == "Unsigned":
            value=int("1000000000000",16)*a[0]+int("100000000",16)*a[1]+int("10000",16)*a[2]+a[3] # four words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text       
        if number == 1 and un_si == "Unsigned":
            value=a[0] # one word and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text       
        if number == 2 and un_si == "Signed":
            value=int("10000",16)*a[0]+a[1]
            if value > 0x7fffffff:
                value = value - 2**32
          #      print ("2 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
            
        if number == 1 and un_si == "Signed":
            value=a[0]
            if value > 0x7fff:
                value = value - 2**16
             #   print ("1 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
                
        if number == 4 and un_si == "Signed":
            value=int("1000000000000",16)*a[0]+int("100000000",16)*a[1]+int("10000",16)*a[2]+a[3] # four words and Unsigned
            if value > 0x7fffffffffffffff:
                value = value - 2**64
             #   print ("4 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
          #  print ("abb1_full_data=", abb_full_data[i*2],abb_full_data[i*2+1])
                       
            
#        print ("a", hex(i), a[i])
    x=x+1
    if x >= 2:
        x = 2
    return abb_data, abb_full_data, x

def get_ABB_2(x):
#   client = ModbusClient(method='rtu', port='/dev/ttyUSB0', stopbits=1, bytesize=8, parity='N', baudrate=9600, timeout=0.3)
#   connection = client.connect()

    
    ABB_1 = minimalmodbus.Instrument('/dev/ttyUSB0', 3)  # port name, slave address (in decimal)
    ABB_1.serial.baudrate = 9600         # Baud
    ABB_1.serial.timeout  = 0.3
    ABB_1.close_port_after_each_call = True
    time.sleep(0.2)
#    print(connection)
#0 Active import kWh 5000 4 0,01 kWh Unsigned
#1 Active export kWh 5004 4 0,01 kWh Unsigned
#2 Active net kWh 5008 4 0,01 kWh Signed

#3 Resettable active import 552C 4 0,01 kWh Unsigned
#4 Resettable active export 5530 4 0,01 kWh Unsigned

#5 Voltage L1-N 5B00 2 0,1 V Unsigned
#6 Voltage L2-N 5B02 2 0,1 V Unsigned
#7 Voltage L3-N 5B04 2 0,1 V Unsigned

#8 Current L1 5B0C 2 0,01 A Unsigned
#9 Current L2 5B0E 2 0,01 A Unsigned
#10 Current L3 5B10 2 0,01 A Unsigned

#11 Active power Total 5B14 2 0,01 W Signed
#12 Active power L1 5B16 2 0,01 W Signed
#13 Active power L2 5B18 2 0,01 W Signed
#14 Active power L3 5B1A 2 0,01 W Signed

#15 Frequency 5B2C 1 0,01 Hz Unsigned
    abb_data=[0]*34
    abb_full_data=[0]*68
    abb_register=[0]*170
    a=[0]*4
#    device=1
    b=0
    
    abb_register=["Active import kWh","5000",4,"kWh","Unsigned",
                  "Active export kWh","5004",4,"kWh","Unsigned",
                  "Active net kWh","5008",4,"kWh","Signed",
                  "Resettable active import","552C",4,"kWh","Unsigned",
                  "Resettable active export","5530",4,"kWh","Unsigned",
                  "Voltage L1-N","5B00",2,"V","Unsigned",
                  "Voltage L2-N","5B02",2,"V","Unsigned",
                  "Voltage L3-N","5B04",2,"V","Unsigned",
                  "Current L1","5B0C",2,"A","Unsigned",
                  "Current L2","5B0E",2,"A","Unsigned",
                  "Current L3","5B10",2,"A","Unsigned",
                  "Active power Total","5B14",2,"W","Signed",
                  "Active power L1","5B16",2,"W","Signed",
                  "Active power L2","5B18",2,"W","Signed",
                  "Active power L3","5B1A",2,"W","Signed",
                  "Frequency","5B2C",1,"Hz","Unsigned",
                  "Phase angle power Total","5B2D",1,"deg","Signed",
                  "Phase angle power L1","5B2E",1,"deg","Signed",
                  "Phase angle power L2","5B2F",1,"deg","Signed",
                  "Phase angle power L3","5B30",1,"deg","Signed",
                  "Phase angle voltage L1","5B31",1,"deg","Signed",
                  "Phase angle voltage L2","5B32",1,"deg","Signed",
                  "Phase angle voltage L3","5B33",1,"deg","Signed",
                  "Phase angle current L1","5B37",1,"deg","Signed",
                  "Phase angle current L2","5B38",1,"deg","Signed",
                  "Phase angle current L3","5B39",1,"deg","Signed",
                  "Power factor Total","5B3A",1,"–","Signed",
                  "Power factor L1","5B3B",1,"–","Signed",
                  "Power factor L2","5B3C",1,"–","Signed",
                  "Power factor L3","5B3D",1,"–","Signed",
                  "Current quadrant Total","5B3E",1,"-","Unsigned",
                  "Current quadrant L1","5B3F",1,"-","Unsigned",
                  "Current quadrant L2","5B40",1,"-","Unsigned",
                  "Current quadrant L3","5B41",1,"-","Unsigned"]
    
    lenght_abb_reg=len(abb_register)
    s=int(lenght_abb_reg/5)
#    print ("s",s)
    for i in range(0,s):
        p=i*5+0
        text=abb_register[p]
        p=i*5+1
        modbus_reg=abb_register[p]
        p=i*5+2
        number=abb_register[p]
        p=i*5+3
        unit=abb_register[p]
        p=i*5+4
        un_si=abb_register[p]
        
#       print ("hex",int(modbus_reg,16))
#       print ("p",p, abb_register[p])
#       print ("modbus reg", hex(modbus_reg))
#       time.sleep(0.2)
        try:
#           value = client.read_holding_registers(int(modbus_reg,16), number, unit=device)
            a=ABB_1.read_registers(int(modbus_reg,16), number, functioncode=3)
        except IOError:
            print("Failed to read from ABB_1")
#            print('Error message: {}'.format(value))
            b=1
            a=[0,0,0,0]
    
  


#       value = client.read_holding_registers(int(modbus_reg,16), number, unit=device)
#print(client.read_holding_registers(23296, 1, unit=1))

#       if not value.isError():
#            '''isError() method implemented in pymodbus 1.4.0 and later'''
#           a=(value.registers)

#       else:
            # Do stuff to error handling.
#          print('Error message: {}'.format(value))
#          b=1
#       a=(value.registers)
      #  print ("a1",a)
#        abb_data[0]=a[3]
        if modbus_reg == "5B00":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B02":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B04":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/10
            abb_full_data[i*2]=value/10
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B0C":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B0E":
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if modbus_reg == "5B10":           
            value=int("10000",16)*a[0]+a[1] # two words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
        if number == 4 and un_si == "Unsigned":
            value=int("1000000000000",16)*a[0]+int("100000000",16)*a[1]+int("10000",16)*a[2]+a[3] # four words and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text       
        if number == 1 and un_si == "Unsigned":
            value=a[0] # one word and Unsigned
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text       
        if number == 2 and un_si == "Signed":
            value=int("10000",16)*a[0]+a[1]
            if value > 0x7fffffff:
                value = value - 2**32
          #      print ("2 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
            
        if number == 1 and un_si == "Signed":
            value=a[0]
            if value > 0x7fff:
                value = value - 2**16
             #   print ("1 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
                
        if number == 4 and un_si == "Signed":
            value=int("1000000000000",16)*a[0]+int("100000000",16)*a[1]+int("10000",16)*a[2]+a[3] # four words and Unsigned
            if value > 0x7fffffffffffffff:
                value = value - 2**64
             #   print ("4 signed neg value=",value)
            abb_data[i]=value/100
            abb_full_data[i*2]=value/100
            abb_full_data[i*2+1]=text
          #  print ("abb1_full_data=", abb_full_data[i*2],abb_full_data[i*2+1])
                       
            
#        print ("a", hex(i), a[i])
    x=x+1
    if x >= 2:
        x = 2

    return abb_data, abb_full_data, x


def map_on_data(abb_list_1, abb_list_2, abb_list_1_old, abb_list_2_old, temp_c, day_data_list):
 
# ABB list
#0 Active import kWh 5000 4 0,01 kWh Unsigned
#1 Active export kWh 5004 4 0,01 kWh Unsigned
#2 Active net kWh 5008 4 0,01 kWh Signed

#3 Resettable active import 552C 4 0,01 kWh Unsigned
#4 Resettable active export 5530 4 0,01 kWh Unsigned

#5 Voltage L1-N 5B00 2 0,1 V Unsigned
#6 Voltage L2-N 5B02 2 0,1 V Unsigned
#7 Voltage L3-N 5B04 2 0,1 V Unsigned

#8 Current L1 5B0C 2 0,01 A Unsigned
#9 Current L2 5B0E 2 0,01 A Unsigned
#10 Current L3 5B10 2 0,01 A Unsigned

#11 Active power Total 5B14 2 0,01 W Signed
#12 Active power L1 5B16 2 0,01 W Signed
#13 Active power L2 5B18 2 0,01 W Signed
#14 Active power L3 5B1A 2 0,01 W Signed

#15 Frequency 5B2C 1 0,01 Hz Unsigned

    dt = datetime.datetime.now()
    #day energy
    if day_data_list[1] != int('{:%d}'.format(dt)):
        day_data_list[16]=0
        day_data_list[21]=0
        day_data_list[26]=0
        day_data_list[31]=0
        day_data_list[36]=0
        day_data_list[41]=0
        day_data_list[46]=0
        day_data_list[51]=0
        day_data_list[56]=0
        day_data_list[61]=0
        day_data_list[66]=0
        day_data_list[71]=0
     
#0 hour
#1 day
#2 week
#3 month
#4 year

#5 "Grid power, kW" *, +- xxx.xxx
#6 "Home power, kW" *, +- xxx.xxx
#7 "PV solar power, kW" *, +- xxx.xxx
#8 "Battery power, kW" *, +- xxx.xxx

#9 "Temp outdoor, C", *, +- xxx.xxx
#10 "Temp indoor, C", *, +- xxx.xxx
#11 "Temp heatpump in, C", *, +- xxx.xxx
#12 "Temp heatpump out, C", *, +- xxx.xxx
#13 "Temp sauna, C", *, +- xxx.xxx
#14 "Air pressure, hPa", *, +- xxxx.xx

#15 "Grid import hour energy, kWh" * , +- xxxxxx.xxx
#16 "Grid import day energy, kWh" * , +- xxxxxx.xxx
#17 "Grid import week energy, kWh"
#18 "Grid import month energy, kWh"
#19 "Grid import year energy, kWh"

#20 "Grid export hour energy, kWh" * , +- xxxxxx.xxx
#21 "Grid export day energy, kWh" * , +- xxxxxx.xxx
#22 "Grid export week energy, kWh"
#23 "Grid export month energy, kWh"
#24 "Grid export year energy, kWh"

#25 "Grid net hour energy, kWh" * , +- xxxxxx.xxx
#26 "Grid net day energy, kWh" * , +- xxxxxx.xxx
#27 "Grid net week energy, kWh"
#28 "Grid net month energy, kWh"
#29 "Grid net year energy, kWh" 

#30 "PV solar hour energy, kWh" * , +- xxxxxx.xxx
#31 "PV solar day energy, kWh" * , +- xxxxxx.xxx
#32 "PV solar week energy, kWh"
#33 "PV solar month energy, kWh"
#34 "PV solar year energy, kWh" 

#35 "Home hour energy, kWh" * , +- xxxxxx.xxx
#36 "Home day energy, kWh" * , +- xxxxxx.xxx
#37 "Home week energy, kWh"
#38 "Home month energy, kWh"
#39 "Home year energy, kWh"  

#40 "Battery hour energy, kWh"
#41 "Battery temp_c[0]day energy, kWh"
#42 "Battery week energy, kWh"
#43 "Battery month energy, kWh"
#44 "Battery year energy, kWh"  

#45 "Grid import end hour energy, kWh" * , +- xxxxxx.xxx
#46 "Grid import end day energy, kWh" * , +- xxxxxx.xxx
#47 "Grid import end week energy, kWh"
#48 "Grid import end month energy, kWh"
#49 "Grid import end year energy, kWh"

#50 "Grid export end hour energy, kWh" * , +- xxxxxx.xxx
#51 "Grid export end day energy, kWh" * , +- xxxxxx.xxx
#52 "Grid export end week energy, kWh"
#53 "Grid export end month energy, kWh"
#54 "Grid export end year energy, kWh"

#55 "Grid net end hour energy, kWh" * , +- xxxxxx.xxx
#56 "Grid net end day energy, kWh" * , +- xxxxxx.xxx
#57 "Grid net end week energy, kWh"
#58 "Grid net end month energy, kWh"
#59 "Grid net end year energy, kWh" 

#60 "PV solar end hour energy, kWh" * , +- xxxxxx.xxx
#61 "PV solar end day energy, kWh" * , +- xxxxxx.xxx
#62 "PV solar end week energy, kWh"
#63 "PV solar end month energy, kWh"
#64 "PV solar end year energy, kWh" 

#65 "Home end hour energy, kWh" * , +- xxxxxx.xxx
#66 "Home end day energy, kWh" * , +- xxxxxx.xxx
#67 "Home end week energy, kWh"
#68 "Home end month energy, kWh"
#69 "Home end year energy, kWh"  

#70 "Battery end hour energy, kWh" , +- xxxxxx.xxx
#71 "Battery end day energy, kWh"
#72 "Battery end week energy, kWh"
#73 "Battery end month energy, kWh"
#74 "Battery end year energy, kWh"  

#75 "Battery SoC, %", +- xxx.x
#76 "Battery SoH, %", +- xxx.x
#77 "Battery capacity new, kWh", +- xxxxxx.xxx
#78 "Battery capacity now, kWh", +- xxxxxx.xxx

#79 "Extra1" *, +- xxxxxx.xxx
#80 "Extra2" *, +- xxxxxx.xxx
#81 "Extra3" *, +- xxxxxx.xxx
#82 "Extra4" *, +- xxxxxx.xxx


    day_data_list[0]=0                                  #0 hour
    day_data_list[1]=int('{:%d}'.format(dt))            #1 day
    day_data_list[2]=0                                  #2 week
    day_data_list[3]=0                                  #3 month
    day_data_list[4]=0                                  #4 year

    day_data_list[5]=abb_list_1[11]                     #5 "Grid power, kW" *, +- xxx.xxx, = #11 Active power Total 5B14 2 0,01 W Signed
    day_data_list[6]=abb_list_1[11] + abb_list_2[11]    #6 "Home power, kW" *, +- xxx.xxx
    day_data_list[7]=abb_list_2[11]                     #7 "PV solar power, kW" *, +- xxx.xxx
    day_data_list[8]=0                                  #8 "Battery power, kW" *, +- xxx.xxx
  
    day_data_list[9]=temp_c[0]                          #9 "Temp outdoor, C", *, +- xxx.xxx
    day_data_list[10]=temp_c[1]                         #10 "Temp indoor, C", *, +- xxx.xxx
    day_data_list[11]=temp_c[2]                         #11 "Temp heatpump in, C", *, +- xxx.xxx
    day_data_list[12]=temp_c[3]                         #12 "Temp heatpump out, C", *, +- xxx.xxx
    day_data_list[13]=temp_c[4]                         #13 "Temp sauna, C", *, +- xxx.xxx
    day_data_list[14]=1013                              #14 "Air pressure, hPa", *, +- xxxx.xx

    day_data_list[15]=0                                 #15 "Grid import hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[16]=abb_list_1[0] - abb_list_1_old[0] + day_data_list[16]                                 #16 "Grid import day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[17]=0                                 #17 "Grid import week energy, kWh"
    day_data_list[18]=0                                 #18 "Grid import month energy, kWh"
    day_data_list[19]=0                                 #19 "Grid import year energy, kWh"

    day_data_list[20]=0                                 #20 "Grid export hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[21]=abb_list_1[1] - abb_list_1_old[1] + day_data_list[21]                                 #21 "Grid export day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[22]=0                                 #22 "Grid export week energy, kWh"
    day_data_list[23]=0                                 #23 "Grid export month energy, kWh"
    day_data_list[24]=0                                 #24 "Grid export year energy, kWh"

    day_data_list[25]=0                                 #25 "Grid net hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[26]=abb_list_1[2] - abb_list_1_old[2] + day_data_list[26]                                 #26 "Grid net day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[27]=0                                 #27 "Grid net week energy, kWh"
    day_data_list[28]=0                                 #28 "Grid net month energy, kWh"
    day_data_list[29]=0                                 #29 "Grid net year energy, kWh" 

    day_data_list[30]=0                                 #30 "PV solar hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[31]=abb_list_2[0] - abb_list_2_old[0] + day_data_list[31]                               #31 "PV solar day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[32]=0                                 #32 "PV solar week energy, kWh"
    day_data_list[33]=0                                 #33 "PV solar month energy, kWh"
    day_data_list[34]=0                                 #34 "PV solar year energy, kWh" 

    day_data_list[35]=0                                 #35 "Home hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[36]=day_data_list[31] + day_data_list[26]              #36 "Home day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[37]=0                                 #37 "Home week energy, kWh"
    day_data_list[38]=0                                 #38 "Home month energy, kWh"
    day_data_list[39]=0                                 #39 "Home year energy, kWh"  

    day_data_list[40]=0                                 #40 "Battery hour energy, kWh"
    day_data_list[41]=0                                 #41 "Battery day energy, kWh"
    day_data_list[42]=0                                 #42 "Battery week energy, kWh"
    day_data_list[43]=0                                 #43 "Battery month energy, kWh"
    day_data_list[44]=0                                 #44 "Battery year energy, kWh"  

    day_data_list[45]=0                                 #45 "Grid import end hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[46]=0                                 #46 "Grid import end day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[47]=0                                 #47 "Grid import end week energy, kWh"
    day_data_list[48]=0                                 #48 "Grid import end month energy, kWh"
    day_data_list[49]=0                                 #49 "Grid import end year energy, kWh"

    day_data_list[50]=0                                 #50 "Grid export end hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[51]=0                                 #51 "Grid export end day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[52]=0                                 #52 "Grid export end week energy, kWh"
    day_data_list[53]=0                                 #53 "Grid export end month energy, kWh"
    day_data_list[54]=0                                 #54 "Grid export end year energy, kWh"

    day_data_list[55]=0                                 #55 "Grid net end hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[56]=0                                 #56 "Grid net end day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[57]=0                                 #57 "Grid net end week energy, kWh"
    day_data_list[58]=0                                 #58 "Grid net end month energy, kWh"
    day_data_list[59]=0                                 #59 "Grid net end year energy, kWh" 

    day_data_list[60]=0                                 #60 "PV solar end hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[61]=0                                 #61 "PV solar end day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[62]=0                                 #62 "PV solar end week energy, kWh"
    day_data_list[63]=0                                 #63 "PV solar end month energy, kWh"
    day_data_list[64]=0                                 #64 "PV solar end year energy, kWh" 

    day_data_list[65]=0                                 #65 "Home end hour energy, kWh" * , +- xxxxxx.xxx
    day_data_list[66]=0                                 #66 "Home end day energy, kWh" * , +- xxxxxx.xxx
    day_data_list[67]=0                                 #67 "Home end week energy, kWh"
    day_data_list[68]=0                                 #68 "Home end month energy, kWh"
    day_data_list[69]=0                                 #69 "Home end year energy, kWh"  

    day_data_list[70]=0                                 #70 "Battery end hour energy, kWh" , +- xxxxxx.xxx
    day_data_list[71]=0                                 #71 "Battery end day energy, kWh"
    day_data_list[72]=0                                 #72 "Battery end week energy, kWh"
    day_data_list[73]=0                                 #73 "Battery end month energy, kWh"
    day_data_list[74]=0                                 #74 "Battery end year energy, kWh"  

    day_data_list[75]=0                                 #75 "Battery SoC, %", +- xxx.x
    day_data_list[76]=0                                 #76 "Battery SoH, %", +- xxx.x
    day_data_list[77]=0                                 #77 "Battery capacity new, kWh", +- xxxxxx.xxx
    day_data_list[78]=0                                 #78 "Battery capacity now, kWh", +- xxxxxx.xxx

    day_data_list[79]=0                                 #79 "Extra1" *, +- xxxxxx.xxx
    day_data_list[80]=0                                 #80 "Extra2" *, +- xxxxxx.xxx
    day_data_list[81]=0                                 #81 "Extra3" *, +- xxxxxx.xxx
    day_data_list[82]=0                                 #82 "Extra4" *, +- xxxxxx.xxx



    return day_data_list




day_data_list=[0]*85
abb_list_1=[0]*34
abb_list_2=[0]*34
abb_list_1_old=[0]*34
abb_list_2_old=[0]*34
z1=0
z2=0



di = datebase_inteface()
minute=0

while True:
    for x in range(0, len(temp_sensors)):
        temp_c[x]=read_temp(temp_sensors[x])
    print ("last temp C", temp_c)
    print("-") 
    
    abb_list_1_old = abb_list_1
    abb_list_2_old = abb_list_2

    abb_list_1, abb_list_1_expl, z1=get_ABB_1(z1) # Get reading from ABB meter 1
    abb_list_2, abb_list_2_expl, z2=get_ABB_2(z2) # Get reading from ABB meter 2
    
    if z1 == 1:
        abb_list_1_old = abb_list_1
    if z2 == 1:
        abb_list_2_old = abb_list_2

#    day_data_list[0]=abb_list_1[0]
    print ("abb_list_1", abb_list_1)
    print ("abb_expl  ", abb_list_1_expl)
    print ("z1        ", z1)
    print ("-")
    
    print ("abb_list_2", abb_list_2)
    print ("abb_expl  ", abb_list_2_expl)
    print ("z2        ", z2)
    print ("-")

    day_data_list=map_on_data(abb_list_1, abb_list_2, abb_list_1_old, abb_list_2_old, temp_c, day_data_list)

    dt = datetime.datetime.now()

    for i in range(len(day_data_list)):
        day_data_list[i] = day_data_list[i] // 0.01 / 100

    print(f"Is connected: {di.is_connencted()}")

    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.outdoor, dt, day_data_list[9]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.indoor, dt, day_data_list[10]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.heatpump_in, dt, day_data_list[11]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.heatpump_out, dt, day_data_list[12]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.sauna, dt, day_data_list[13]))
    
    
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.grid.power, dt, day_data_list[5]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.home.power, dt, day_data_list[6]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.pv.power, dt, day_data_list[7]))

    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.grid.imported.day, dt, day_data_list[16]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.pv.day, dt, day_data_list[31]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.home.day, dt, day_data_list[36]))

    '''try:
        temperature = aio.feeds('temp-outdoor')
    except RequestError:
        feed = Feed(name="temperature")
        temperature = aio.create_feed(feed)
    '''

    if minute != int('{:%M}'.format(dt)):
        minute = int('{:%M}'.format(dt))
        temperature = day_data_list[9]

        # Latitude and Longitude values for a location
        latitude = 59.25593
        longitude = 17.97447

        # Create a dictionary containing data and additional parameters
        data = {
            'value': temperature,
            'lat': latitude,
            'lon': longitude,
        }
        '''

        # Send data to the 'temp-outdoor' feed
        aio.send_data(aio.feeds('temp-outdoor').key, data)

        #aio.send_data(aio.feeds('temp-outdoor').key, day_data_list[9], 'lat':59.25593, 'lon':17.97447, )
        #aio.send_data(aio.feeds('temp-outdoor').key, day_data_list[9], {'lat': 59.25593, 'lon': 17.97447})
        '''
        aio.send_data(aio.feeds('temp-outdoor').key, day_data_list[9])
        aio.send_data(aio.feeds('temp-indoor').key, day_data_list[10])
        aio.send_data(aio.feeds('temp-heatpump-in').key, day_data_list[11])
        aio.send_data(aio.feeds('temp-heatpump-out').key, day_data_list[12])
        aio.send_data(aio.feeds('temp-sauna').key, day_data_list[13])

        aio.send_data(aio.feeds('power-grid').key, day_data_list[5])
        aio.send_data(aio.feeds('power-house').key, day_data_list[6])
        aio.send_data(aio.feeds('power-pv').key, day_data_list[7])

        aio.send_data(aio.feeds('energy-house-day').key, day_data_list[36])
        aio.send_data(aio.feeds('energy-grid-day').key, day_data_list[16])

# works the same as send now
#aio.append(temperature.key, 26)
