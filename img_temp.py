#!/usr/bin/python
import rospy
import time
import RPi.GPIO as GPIO
from std_msgs.msg import String
from std_msgs.msg import Byte
import threading
import socket
import cv2
import numpy as np
import serial as ser
import matplotlib.pyplot as plt

global data_r
data_r=0
global bz_shot_2
bz_shot_2=1
global time_shot_2
time_shot_2=0
global bz_shot_3
bz_shot_3=1
global time_shot_3
time_shot_3=0
global pre_frame
pre_frame = None
global init_frame
init_frame = None
global count_ctrl
count_ctrl=0
global shot_tg_fsm
shot_tg_fsm=1
global bz_temp
bz_temp=1
global time_temp_op
time_temp_op=0

global temp_str
temp_str=''
temp_list=[]

plt_on=0
x=[]
y=[]
temp_max=0.0
temp_min=50.0
temp_float=0.0

mode_last=0
mode=0
sock=None
ctrl_cmd=""

def show_plt():
    global plt_on
    global x
    global y
    global temp_max
    global temp_min
    global temp_float
    global mode_last
    global mode
    while(1):
        if(plt_on==1):
            plt.clf()
            mmf='max:'+str(temp_max)+' min:'+str(temp_min)+' now:'+str(temp_float)
            plt.title(mmf)
            plt.scatter(x,y)
            plt.plot(x,y)
            plt.pause(0.001)
            plt.ioff()
            plt_on=0
        if(mode!=mode_last):
            print('close1')
            #plt.close()

def recv_temp():
    global temp_str
    se=ser.Serial("/dev/ttyTHS1",9600,timeout=1)
    while(1):
        if(se.in_waiting):
            temp_str=se.read(se.in_waiting)
            #print(sss[5:10])

def recv_ctrl():
    global mode
    global sock
    global ctrl_cmd
    while(1):
        if(mode==3):
            receive = sock.recv(1024) 
            if len(receive):
                ctrl_cmd=str(receive)
                print(ctrl_cmd)

def rec_socket():
    global data_r
    global bz_shot_2
    global time_shot_2
    global bz_shot_3
    global time_shot_3
    global pre_frame
    global init_frame
    global count_ctrl
    global shot_tg_fsm
    global temp_str
    global bz_temp
    global time_temp_op
    global temp_list
    global plt_on
    global x
    global y
    global temp_max
    global temp_min
    global temp_float
    global mode_last
    global mode
    global sock
    global ctrl_cmd
    print('gg')
    address=('192.168.43.133',8003)
    try:

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(address)
        print("yy")
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("rr")
    time.sleep(0.2)
    ff=open('/home/opencv/socket_test/muilt_th/temp.txt','w')
    ff.write('temperature:(once per minute)\n')
    ff.close()
    while 1:
        mode=data_r
        #mode=3  #debug
        #print('mode='+str(mode))
        if(bz_temp==1):  #send_temp
            time_temp_op=time.time()
            temp_5=temp_str[5:10]
            temp_float=int(temp_5[0])*10.0+int(temp_5[1])*1.0+int(temp_5[3])*0.1+int(temp_5[4])*0.01
            if(temp_float>temp_max):
                temp_max=temp_float
            if(temp_float<temp_min):
                temp_min=temp_float
            #print('temp_float '+str(temp_float))
            ff=open('/home/opencv/socket_test/muilt_th/temp.txt','a')
            ff.write(str(temp_float)+'\n')
            ff.close()
            temp_list.append(temp_float)
            if(len(temp_list)>=30):
                temp_list.remove(temp_list[0])
            temp_data=str.encode(temp_5)
            five=5
            bz_temp=0
            if(mode!=0)&(mode!=2)&((mode!=3)|((mode==3)&(ctrl_cmd=="c"))):
                sock.send(str.encode(str(five).ljust(16)))
                sock.send(temp_data)
                y=np.array(temp_list)
                num=y.size
                x=np.arange(1,num+1,1)
                plt_on=1
            else:
                plt_on=0
                #plt.close('all')
        else:
            if((time.time()-time_temp_op)>1.0):
                bz_temp=1
        #if mode changed, something should be re init  and send bz to closewindows
        #pass
        if(mode!=mode_last):
            #plt.close('all')
            bz_shot_3=1
            bz_shot_2=1
            time_shot_3=0
            shot_tg_fsm=1
            pre_frame=None
            print('close2')
            cv2.destroyAllWindows()
            cv2.waitKey(5)

        if(mode==3):
            if(ctrl_cmd=="r"):
                print('rrrrrrrr')
                #plt.close('all')
                capture = cv2.VideoCapture("/dev/v4l/by-id/usb-RYS_SY_1080P_camera_200901010001-video-index0")
                ret, frame = capture.read()
                print("pp")
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                data = np.array(imgencode)
                stringData = data.tostring()
                sock.send(str.encode(str(len(stringData)).ljust(16)))
                sock.send(stringData)
                #frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                cv2.imshow("frame",frame)
                #plt.pause(0.001)
                #plt.ioff()
                print("rr")
                capture.release()
                ctrl_cmd=""

        elif(mode==2)|(mode==4):
            if(bz_shot_2==1):
                time_shot_2=time.time()
                capture = cv2.VideoCapture("/dev/v4l/by-id/usb-RYS_SY_1080P_camera_200901010001-video-index0")
                ret, frame = capture.read()
                cv2.imshow('frame',frame)
                print("pp")
                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                data = np.array(imgencode)
                stringData = data.tostring()
                sock.send(str.encode(str(len(stringData)).ljust(16)))
                sock.send(stringData)
                capture.release()
                bz_shot_2=0
            else:
                if(time.time()-time_shot_2>=3):
                    bz_shot_2=1
                    time_shot_2=0
        elif(mode==5):
            #print('ii')
            if(bz_shot_3==1):
                print('mm')
                time_shot_3=time.time()
                capture = cv2.VideoCapture("/dev/v4l/by-id/usb-RYS_SY_1080P_camera_200901010001-video-index0")
                ret, frame = capture.read()
                cv2.imshow('timer',frame)
                print("pp")
                
                gray_lwpCV = cv2.resize(frame, (500, 500))
                gray_lwpCV = cv2.cvtColor(gray_lwpCV, cv2.COLOR_BGR2GRAY)
                gray_lwpCV = cv2.GaussianBlur(gray_lwpCV, (21, 21), 0)
                if pre_frame is None:
                    pre_frame = gray_lwpCV
                else:
                    if(shot_tg_fsm==1):
                        img_delta = cv2.absdiff(pre_frame, gray_lwpCV)
                        thresh = cv2.threshold(img_delta, 55, 255, cv2.THRESH_BINARY)[1]
                        thresh = cv2.dilate(thresh, None, iterations=2)
                        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        cv2.imshow('contra',thresh)
                        for c in contours:
                            print('area::'+str(cv2.contourArea(c)))
                            if cv2.contourArea(c) < 5000:
                                continue
                            else:
                                init_frame=pre_frame
                                shot_tg_fsm=4
                                print("there are some thing"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                                #cv2.imshow(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg', frame)
                                encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
                                result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                                data = np.array(imgencode)
                                stringData = data.tostring()
                                sock.send(str.encode(str(len(stringData)).ljust(16)))
                                sock.send(stringData)
                                break
                        pre_frame = gray_lwpCV
                    elif(shot_tg_fsm==2):
                        cv2.imshow('init_frame',init_frame)
                        img_delta = cv2.absdiff(init_frame, gray_lwpCV)
                        thresh = cv2.threshold(img_delta, 55, 255, cv2.THRESH_BINARY)[1]
                        thresh = cv2.erode(thresh, None, iterations=2)
                        white_count=len(thresh[thresh==255])
                        cv2.imshow('contra_back',thresh)
                        print('area:::::::::::'+str(white_count))
                        if white_count > 2000:
                            encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
                            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
                            data = np.array(imgencode)
                            stringData = data.tostring()
                            sock.send(str.encode(str(len(stringData)).ljust(16)))
                            sock.send(stringData)
                        else:
                            shot_tg_fsm=3
                            print("back to background"+str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
                            #cv2.imshow(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + '.jpg', frame)
                    elif(shot_tg_fsm==3):
                        count_ctrl=count_ctrl+1
                        if(count_ctrl>=2):
                            six=6
                            sock.send(str.encode(str(six).ljust(16)))
                            count_ctrl=0
                            shot_tg_fsm=1
                            pre_frame = gray_lwpCV
                    elif(shot_tg_fsm==4):
                        count_ctrl=count_ctrl+1
                        if(count_ctrl>=2):
                            count_ctrl=0
                            shot_tg_fsm=2
                    
                capture.release()
                bz_shot_3=0
            else:
                if(time.time()-time_shot_3>=1):
                    bz_shot_3=1
                    time_shot_3=0
        cv2.waitKey(1)
        mode_last=mode

def thread_job():
    print('aa')
    rospy.spin()
    print('bb')

def callback(data):
    global data_r
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    data_r=data.data
    data_r=int(data_r)/10

def listener():
    global data_r
    rospy.init_node('listener', anonymous=True)
    add_thread = threading.Thread(target = thread_job)
    add_thread.start()
    soc_ctrl_thread = threading.Thread(target = rec_socket)
    soc_ctrl_thread.start()
    temp_thread = threading.Thread(target = recv_temp)
    temp_thread.start()
    plt_thread = threading.Thread(target = show_plt)
    plt_thread.start()
    ctrl_thread = threading.Thread(target = recv_ctrl)
    ctrl_thread.start()
    rospy.Subscriber("/button", Byte, callback)
    rospy.sleep(1)
    while(1):
        print('data:'+str(data_r))
        time.sleep(1)
        #rospy.spin()

if __name__ == '__main__':
    listener()
