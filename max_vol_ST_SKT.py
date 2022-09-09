#!/usr/bin/python
import pyaudio
import wave
import numpy as np
import time
import socket
global bz_start
bz_start=0
global count_silent
count_silent=0

def Monitor():
    global bz_start
    global count_silent

    address=('192.168.43.133',8002)
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(address)
        print("yy")
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("rr")

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 48000
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
        print 'begin '
        time_start=time.time()
        for i in range(0, 100):
            data = record_stream.read(CHUNK)
	    if(bz_start==1):
		sock.send(data)
                play_stream.write(data)
                frames.append(data)
        time_end=time.time()
        print('time'+str(time_end-time_start))
        audio_data = np.fromstring(data, dtype=np.short)
        large_sample_count_1000 = np.sum( audio_data > 1200 )
        large_sample_count_500 = np.sum( audio_data > 600 )
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
		frames=[]
    record_stream.stop_stream()
    record_stream.close()
    play_stream.stop_stream()
    play_stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

if __name__ == '__main__':
    Monitor()
