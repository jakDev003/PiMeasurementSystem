import cv2
import numpy as np
from time import sleep
from threading import Thread    


class cameraClassPi:
    def __init__(self):
        from picamera import PiCamera
        from picamera.array import PiRGBArray

        # initialize the camera and stream
        self.camera = PiCamera()
        #self.camera.sensor_mode = 1
        self.camera.resolution = (1280,720)
        self.camera.framerate = 32
        self.shutter_speed = self.camera.exposure_speed
        self.start()

        self.rawCapture = PiRGBArray(self.camera)

    def stopP(self):
        # stop preview
        self.camera.stop_preview()

    def start(self):
        # indicate that the thread should be stopped
        self.camera.start_preview(alpha=160)

    def capture(self, path):
        self.camera.capture(path)
        
    def stop(self):
        # indicate that the thread should be stopped
        self.camera.close()

class cameraClassWeb:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update).start()
        return self

    def takePicture(self, path):
        cv2.imwrite(path, self.frame)


    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True




    
