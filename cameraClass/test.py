# import the necessary packages
import numpy, imutils, time, pygame, cv2, math, sys, os
from PIL import Image
from pygame.locals import *
from cameraClass import *

def init():
    global color, vs, camera_index, screen, screen_width, xres, yres
    global mWIDTH, mHEIGHT, usePiCameraTF
    pygame.init()

    xres = 1280
    yres = 720

    # grab size of monitor
    infoObject = pygame.display.Info()
    mWIDTH = infoObject.current_w
    mHEIGHT = infoObject.current_h
    
    updateScreenSize()

    usePiCameraTF = False
    
    print("[INFO] xres: %s" % xres)
    print("[INFO] yres: %s" % yres)
    print('')
    print('')

    # set title of screen
    pygame.display.set_caption("Python Camera Scope")

#    usePiCameraTF = False
    # initialize the video stream and allow the camera sensor to warmup
    if(usePiCameraTF):
        vs = cameraClassPi()
    else:
        vs = cameraClassWeb()
    vs.start()
    time.sleep(2.0)

def updateScreenSize():
    global screen, xres, yres
    screen_width, screen_height = xres, yres
    screen=pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)


def getCamFrame(color,vs):
    global height, width, channels, img, saveFrame1, saveSurface, img
    global zoom, rotozoomChg
    # grab the frame from the threaded video stream and resize it
    frame = vs.read()
    #frame = imutils.resize(frame, width=720)
    width = pygame.surfarray.make_surface(frame).get_width()
    height = pygame.surfarray.make_surface(frame).get_height()
    
    # adjust color
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    # image comes reversed so this will fix that
    #rotate image
    frame = numpy.rot90(frame)
    # flip image
    frame = cv2.flip(frame,0)
        
    # save frame to use in measuremode and calibration
    #saveFrame1 = frame
    screen.fill(black)
    if(zoom):
        size=pygame.surfarray.make_surface(frame).get_rect() #get rectangle coordinates
        offsetX = (size[2]/16)*1
        offsetY = (size[3]/16)*1
        left = offsetX
        upper = offsetY
        right = width - offsetX
        lower = height - offsetY
        pil_im = Image.fromarray(frame) #convert opencv image to PIL image
        croppedIm = pil_im.crop((left,upper,right,lower)) #crop image
        croppedIm = numpy.array(croppedIm)
        croppedIm = imutils.resize(croppedIm, width=size[3]) #resize to fit screen
        #testImg(croppedIm)
        frame = croppedIm

    # make into pygame surface
    frame=pygame.surfarray.make_surface(frame)

    # save frame to use in measuremode and calibration
    saveSurface = frame

    return frame

def blitCamFrame(frame,screen):
    global width, height
    width = frame.get_width()
    height = frame.get_height()
    screen.blit(frame,((mWIDTH/2)-(width/2),(mHEIGHT/2)-(height/2)))
    return screen


def cleanQuit():
    global screen
    cv2.destroyAllWindows()
    pygame.quit()    
    sys.exit()

def run():
    global screen, resolution, label1, password, calibfeature, xres, yres, myfont
    global crossHairDes, vs, rotozoomChg, zoom, usePiCameraTF
    running = True
    while running:
        frame=getCamFrame(color,vs)
        screen=blitCamFrame(frame,screen)
        pygame.display.update()
        for event in pygame.event.get(): #process events since last loop cycle
            if event.type == pygame.QUIT:
                cleanQuit()
            elif event.key == pygame.K_p: # use picamera/usbcam
                if(usePiCameraTF):
                    usePiCameraTF = False
                    print("[DEBUG] usePiCameraTF: %s" % usePiCameraTF)
                    print("[INFO] 'p' pressed...switching cameras: Usbcam")
                else:
                    usePiCameraTF = True
                    print("[DEBUG] usePiCameraTF: %s" % usePiCameraTF)
                    print("[INFO] 'p' pressed...switching cameras: RPi Cam")
                saveZoomData()
                vs.stop()
                init() # reinitialize to use new camera
            print('')
            print('')

                    


init()
run()
cleanQuit()

