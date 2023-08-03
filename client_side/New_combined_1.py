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

def get_ABB_1():
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
    return abb_data, abb_full_data, b

def get_ABB_2():
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
    return abb_data, abb_full_data, b



di = datebase_inteface()

while True:
    for x in range(0, len(temp_sensors)):
        temp_c[x]=read_temp(temp_sensors[x])
    print ("last temp C", temp_c)
    print("-") 
    
    abb_list_1, abb_list_1_expl, z1=get_ABB_1() # Get reading from ABB meter 1
    abb_list_2, abb_list_2_expl, z2=get_ABB_2() # Get reading from ABB meter 2
#    if z1==1:
#        abb_list_1=abb_list_1_old
#    day_data_list[0]=abb_list_1[0]
    print ("abb_list_1", abb_list_1)
    print ("abb_expl  ", abb_list_1_expl)
    print ("z1        ", z1)
    print ("-")
    
    print ("abb_list_2", abb_list_2)
    print ("abb_expl  ", abb_list_2_expl)
    print ("z2        ", z2)
    print ("-")

    print(f"Is connected: {di.is_connencted()}")

    dt = datetime.datetime.now()

    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.outdoor, dt, temp_c[0]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.indoor, dt, temp_c[1]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.heatpump_in, dt, temp_c[2]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.heatpump_out, dt, temp_c[3]))
    print(di.insert(di.paths.sites.koltrastvägen, di.paths.categories.temperature.sauna, dt, temp_c[4]))