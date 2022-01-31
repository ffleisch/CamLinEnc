import serial
import time
import numpy as np
print("Hello wall")

arduino=None

try:
    arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.5)

except serial.serialutil.SerialException:
    print("No Aruino Connected")


def write_read(x):
    arduino.write(x)
    time.sleep(0.05)
    data = arduino.readline()
    return data



def wait_for_finish():
    wait_speed=1000
    set_speed(wait_speed)
    num_stuffing=512
    do_cardinal(0,0,num_stuffing)
    time.sleep(wait_speed*num_stuffing/1.0e6)

def do_cardinal(left,right,num):
    """
    Move a number of steps on both motors in the specified directions
    :param left:
    :type left: int
    Direction of the left motor (-1,0,1)
    :param right:
    :type right: int
    Direction of the right motor (-1,0,1)
    :param num:
    :type num: int
    Number ofg steps to take
    """
    steps=[]
    for i in range(num):
        steps.append((left,right))
    do_steps(steps)


chunk_size=16
buffer_limit=128


def set_speed(mikros):
    """
    Send the time interval to wait to the microcontroller
    :param mikros:
    :type mikros: int
    time interval to wait between steps
    """
    bytes=mikros.to_bytes(4,byteorder="big")
    data=[1<<4]
    data.extend(bytes)
    #print(bytes)
    send_bytes(data)

def send_bytes(data):

    arduino.write(bytes(data))

    def read_ard_buff_size():
        # arduino.flushInput()
        res = arduino.readline()
        #print(res)
        try:
            res = res.split()[-1]
            res = int(res)
        except ValueError:
            res = 0
        except IndexError:
            res = 0
        #print(res)
        return res

    res = read_ard_buff_size()
    #print(res)
    # if(res==0):
    #    print("Arduino Buffer empty")

    if (res == 255):
        raise Exception("Arduino Buffer full")
    while True:
        res = read_ard_buff_size()
        if res == 255:
            raise Exception("Arduino Buffer full")

        if res < buffer_limit:
            break
        # time.sleep(0.025)

    arduino.flushInput()


def do_steps(steps):
    #print("len",len(steps))
    #print("steps",steps)
    while(len(steps)>0):
        chunk=steps[:chunk_size]
        steps=steps[chunk_size:]
        #print(chunk)

        data=[]
        for i,c in enumerate(chunk):

            left=c[0]
            right=c[1]
            b=0
            if(left!=0):
                b|=0b0100
            if(left>0):
                b|=0b1000

            if (right !=0):
                b |= 0b0001
            if (right <0):
                b |= 0b0010
            data.append(b)

            #print(c,b)
        #print(data)
        send_bytes(data)


def reverse(steps):
    steps_new=[]

    for s in steps:
        steps_new.insert(0,(s[0]*-1,s[1]*-1))
    return steps_new

def sum_steps(steps):
    a=0
    b=0
    for s in steps:
        a+=s[0]
        b+=s[0]
    print(a,b)

if arduino is not None:
    do_cardinal(0,0,100)


if __name__=="__main__":
    time.sleep(1)

    set_speed(500)
    #do_cardinal(-1,-1,1000)
    for i in range(100):
        test_steps=[(-1,-1) for i in range(256)]
        set_speed(500+i*10)
        do_steps(test_steps)
    #for i in range(1000):
    #    set_speed(1000+i)
    #set_speed(5000)
    #do_steps(reverse(test_steps))



    #print(test_steps)
    #print(reverse(test_steps))
    #print(sum_steps(test_steps))
    #print(sum_steps(reverse(test_steps)))
    #do_cardinal(-1,0,10000)

