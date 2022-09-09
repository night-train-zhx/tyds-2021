#!/usr/bin/python
import pyaudio
import wave
import numpy as np
import time
import sys
import threading
import socket
import rospy
import RPi.GPIO as GPIO
from std_msgs.msg import String
from std_msgs.msg import Byte
global bz_start
bz_start=0
global count_silent
count_silent=0

bz_sendAM=0
bz_sendAS=0
data_r=0
ctrl_cmd=""
mode=0
mode_last=0
sock=None

def send_audio():
    global bz_sendAM
    global bz_sendAS
    global sock
    print('gg')
    address=('192.168.43.133',8004)
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(address)
        print("yy")
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("rr")
    time.sleep(0.2)
    while(1):
        if(bz_sendAM==1):
            time.sleep(0.3)
            print('send_begin_AM')
            with open('max_vol.wav','rb') as f1:
                for l in f1:
                    sock.sendall(l)
            print('AM_send finished')
            #five=7
            #sock.send(str.encode(str(five).ljust(16)))
            bz_sendAM=0
        if(bz_sendAS==1):
            time.sleep(0.3)
            with open('slc_vol.wav','rb') as f2:
                for l in f2:
                    sock.sendall(l)
            print('AS_send finished')
            bz_sendAS=0

def spin_vol():
    print('aa')
    rospy.spin()
    print('bb')

def callback(data):
    global data_r
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    data_r=data.data
    data_r=int(data_r)/10

def recv_ctrl():
    global mode
    global sock
    global ctrl_cmd
    while(1):
        if(mode==3):
            print('33333333')
            receive = sock.recv(1024) 
            if len(receive):
                ctrl_cmd=str(receive)
                print(ctrl_cmd)

def Monitor():
    global bz_sendAM
    global bz_sendAS
    global bz_start
    global count_silent
    global data_r
    global mode
    global ctrl_cmd
    rospy.init_node('vol_recv', anonymous=True)
    rospy.Subscriber("/button", Byte, callback)
    rospy.sleep(1)
    spin_thread = threading.Thread(target = spin_vol)
    spin_thread.start()

    SA_thread = threading.Thread(target = send_audio)
    SA_thread.start()
    ctrlA_thread = threading.Thread(target = recv_ctrl)
    ctrlA_thread.start()
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
    WAVE_OUTPUT_FILENAME = "max_vol.wav"
    p = pyaudio.PyAudio()
    record_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    play_stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    print("begin")
    frames = []
    while (True):
        #print('mode='+str(mode))
        mode=data_r
        if((mode==1)|(mode==2)|(mode==5)):
            bz_start=0
            bz_sendAM=0
            bz_sendAS=0
            count_silent=0
            print 'begin '
            time_start=time.time()
            for i in range(0, 100):
                data = record_stream.read(CHUNK)
                play_stream.write(data)
            time_end=time.time()
            print('time'+str(time_end-time_start))
            
        elif(mode==3):
            if(ctrl_cmd=="a"):
                print 'begin '
                time_start=time.time()
                for i in range(0, 50):
                    data = record_stream.read(CHUNK)
                    play_stream.write(data)
                    frames.append(data)
                time_end=time.time()
                print('time'+str(time_end-time_start))
            elif(ctrl_cmd=="b"):
                wf = wave.open('slc_vol.wav', 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                frames=[]
                bz_sendAS=1
                ctrl_cmd=""
        
        elif(mode==4):
            print 'begin '
            time_start=time.time()
            for i in range(0, 50):
                data = record_stream.read(CHUNK)
                if(bz_start==1):
                    play_stream.write(data)
                    frames.append(data)
            time_end=time.time()
            print('time'+str(time_end-time_start))
            audio_data = np.fromstring(data, dtype=np.short)
            large_sample_count_1000 = np.sum( audio_data > 1300 )
            large_sample_count_500 = np.sum( audio_data > 700 )
            temp = np.max(audio_data)
            print('max'+str(temp)+'  max_count_1000  :'+str(large_sample_count_1000))
            print('max'+str(temp)+'  max_count_500  :'+str(large_sample_count_500))
            if(bz_start==0):
                if large_sample_count_1000>10 :
                    bz_start=1
                    print "has found"
                    print 'current thres:',temp 
    #                break
            if(bz_start==1):
                if(large_sample_count_500<10):
                    count_silent=count_silent+1
                else:
                    count_silent=0
                if(count_silent>10):
                    bz_start=0
                    count_silent=0
                    wf = wave.open('max_vol.wav', 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    frames=[]
                    bz_sendAM=1

    record_stream.stop_stream()
    record_stream.close()
    play_stream.stop_stream()
    play_stream.close()
    p.terminate()

if __name__ == '__main__':
    Monitor()
