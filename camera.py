import cv2, os, sys, time, pygame, shelve, picamera, picamera.array
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
# ?? must run sudo modprobe bcm2835-v4l2 if using USB webcams


# initialize 
def init():
    pygame.init()
    pygame.mouse.set_visible(True)
    global myfont, myfont1, cam
    myfont = pygame.font.SysFont("Times New Roman", 50)
    myfont1 = pygame.font.SysFont("Times New Roman", 25)

    keys=pygame.key.get_pressed() 

# Define variables
def variables():
    global xres, yres, screen, whichline, x1, x2, x_change, lsl, usl, password, red, black, white, blue
    global yellow,magenta,cyan, linecolor,screen, a, b
    xres, yres = 640, 480 # monitor resolution
    password = "no"
    x1= xres * .65
    x2= xres * .35
    red = (255,0,0)
    black = (0,0,0)
    white = (255,255,255)
    blue = (0,0,255)
    yellow = (255,255,0)
    magenta = (255,0,255)
    black = (0,0,0)
    cyan = (0,255,255)
    linecolor = red
    whichline=1
    x_change=0
    usl = ""
    lsl = ""
    a=3
    b=3 
    screen = pygame.display.set_mode((xres,yres))

def updateScreen():
    pygame.draw.circle(screen,white,(xres/2,yres/2),100,1)
    pygame.draw.lines(screen,white,False,[((xres/2)-100,yres/2),((xres/2)+100,yres/2),1])
    pygame.draw.lines(screen,white,False,[(xres/2,(yres/2)-100),(xres/2,(yres/2)+100),1])
    label = myfont.render("Press any key", 1, white)
    label1 = myfont.render("to take picture.", 1, white)
    screen.blit(label, (5, 5))
    screen.blit(label1, (5, 45))
    pygame.display.update()
    
    
#  start here
variables()
init()
pygame.display.toggle_fullscreen()
cam = picamera.PiCamera(sensor_mode=1)
cam.start_preview(alpha=230)
cam.vflip = False
cam.hflip = False
updateScreen()
while True:
    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cam.close()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cam.close()
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_e:
                print("cam.framerate")
                print(cam.framerate)
                print("cam.shutter_speed")
                print(cam.shutter_speed)
                print("cam.exposure_speed")
                print(cam.exposure_speed)   
                print("**************************")
                print("cam.meter_mode")
                print(cam.meter_mode)
                print("cam.iso")
                print(cam.iso)
                print("cam.awb_gains")
                print(cam.awb_gains)
                print("cam.awb_mode")
                print(cam.awb_mode)
                print("cam.brightness")
                print(cam.brightness)
                print("cam.color_effects")
                print(cam.color_effects)
                print("cam.contrast")
                print(cam.contrast)
                print("cam.digital_gain")
                print(cam.digital_gain)
                print("cam.exposure_compensation")
                print(cam.exposure_compensation)
                print("cam.exposure_mode")
                print(cam.exposure_mode)
                print("cam.saturation")
                print(cam.saturation)
                print("cam.shutter_speed")
                print(cam.shutter_speed)
                print("cam.exposure_speed")
                print(cam.exposure_speed)        
                print("cam.sharpness")
                print(cam.sharpness)
                print("cam.sensor_mode")
                print(cam.sensor_mode)
            else:
                img = cam.capture('/home/pi/Images/image.jpg')
            
                    
