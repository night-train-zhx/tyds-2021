#!/usr/bin/python
import socket
import cv2
import numpy
import time
import sys
  
def SendVideo():
    address=('192.168.43.133',8003)
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(address)
        print("yy")
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("rr")
    capture = cv2.VideoCapture("/dev/v4l/by-id/usb-RYS_SY_1080P_camera_200901010001-video-index0")
    print("oo")
    ret, frame = capture.read()
    print("pp")
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),15]
    print("aa")
    while ret:
	print("bb")
        time.sleep(0.01)
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        
        sock.send(str.encode(str(len(stringData)).ljust(16)))
        sock.send(stringData)
        receive = sock.recv(1024)
        if len(receive):print(str(receive))
        ret, frame = capture.read()
        if cv2.waitKey(10) == 27:
            break
    sock.close()
     
if __name__ == '__main__':
    SendVideo()
