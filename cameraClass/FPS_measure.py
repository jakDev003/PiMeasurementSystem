# import the necessary packages
import numpy, imutils, time, pygame, cv2, math, sys, os, gc
from PIL import Image
from pygame.locals import *
from cameraClass import *
import Tkinter as tk

def init():
    global color, vs, camera_index, screen, screen_width, xres, yres, os
    global mWIDTH, mHEIGHT, monSize, resolution, label1, usePiCameraTF
    pygame.init()    
    variables()

    color=False
    label1 = "test"

    # set defaults
    readZoomData() # read zoom and pi camera data
    getMonSize() # grab the resolution of the monitor

    print("[INFO] xres: %s" % xres)
    print("[INFO] yres: %s" % yres)
    print("[INFO] monSize: %s" % monSize)
    print('')
    print('')

#    usePiCameraTF = False
    resolution = 999
    # initialize the video stream and allow the camera sensor to warmup
    if(usePiCameraTF):
        vs = cameraClassPi()
        resolution = 0000    
    else:
        vs = cameraClassWeb()
        vs.start()
        
    # read calibration data
    dataCal = (1,1,1,1,1,1) # set defaults if no file is found
    loadCalData()
    
    # set title of screen
    pygame.display.set_caption("Python Camera Scope")
    adjustRes()


def updateScreenSize():
    global screen, xres, yres, mWIDTH, mHEIGHT
    screen_width, screen_height = xres, yres
    try:
        screen=pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)
    except:
        print("[WARN] Could not SET screen size 2.")
        mWIDTH = 800
        mHEIGHT = 440
        xres = mWIDTH
        yres = mHEIGHT
        print("[WARN] *Fixed* Monitor width: %s" % mWIDTH)
        print("[WARN] *Fixed* Monitor height: %s" % mHEIGHT)
        screen=pygame.display.set_mode((mWIDTH,mHEIGHT), pygame.RESIZABLE)


def updateScreenSizePiCam():
    global screen, xres, yres, mWIDTH, mHEIGHT
    screen_width, screen_height = mWIDTH, mHEIGHT
    try:
        screen=pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)
    except:
        print("[WARN] Could not SET screen size 2.")
        mWIDTH = 800
        mHEIGHT = 440
        xres = mWIDTH
        yres = mHEIGHT
        print("[WARN] *Fixed* Monitor width: %s" % mWIDTH)
        print("[WARN] *Fixed* Monitor height: %s" % mHEIGHT)
        screen=pygame.display.set_mode((mWIDTH,mHEIGHT), pygame.RESIZABLE)

# Define variables
def variables():
    global whichline, x_change, lsl, usl, password, red, black, white, blue
    global yellow, magenta, cyan, green, linecolor, a, b, path, width, height, channels
    global count, d, calibfactor, trk, crossHairDes, fNameCal, fNameZoom, crossHairShow
    crossHairDes = 1
    #xres, yres = 1920, 1080 # monitor resolution
    password = "no"
    
    #path = "C:/temp/Images/"
    path = "/home/pi/Images/"
    fNameCal = path + "calibration.npy"
    fNameZoom = path + "rotozoom.npy"
    
    trk = 1
    red = (255,0,0)
    black = (0,0,0)
    white = (255,255,255)
    blue = (0,0,255)
    yellow = (255,255,0)
    magenta = (255,0,255)
    black = (0,0,0)
    cyan = (0,255,255)
    green = (0,255,0)
    linecolor = red
    whichline=1
    x_change=0
    usl = ""
    lsl = ""
    a=3
    b=3
    width = 0
    height = 0
    channels= 0
    count = 0
    crossHairShow = True # set default


def readZoomData():
    global rotozoomChg, zoom, usePiCameraTF, fNameZoom
    try:
        data = numpy.load(fNameZoom)        
        zoom = data[0]
        usePiCameraTF = data[1]
        crossHairShow = data[2]
        print("[INFO] Zoom: %s, usePiCamera: %s, crossHairShow %s" % (zoom, usePiCameraTF, crossHairShow))        
    except:
        print("[WARN] Could not read rotozoom: %s" % fNameZoom)        
        zoom = False
        usePiCameraTF = True
        crossHairShow = True
    rotozoomChg = False # triggers zoom or rotate of live image
    print("[DEBUG] usePiCameraTF_Read: %s" % usePiCameraTF)
    print('')
    print('')

def saveZoomData():
    global rotozoomChg, zoom, usePiCameraTF, fNameZoom
    try:
        data = [0,0,0]
        data[0] = zoom
        data[1] = usePiCameraTF
        data[2] = crossHairShow
        numpy.save(fNameZoom,data)
        rotozoomChg = False
        print("[INFO] Zoom: %s, usePiCamera: %s, crossHairShow %s" % (zoom, usePiCameraTF, crossHairShow))        
    except:
        print("[ERROR] 06: Could not write rotozoom: %s" % fNameZoom)
    print("[DEBUG] usePiCameraTF_Save: %s" % usePiCameraTF)
    print('')
    print('')

def getMonSize():
    global mWIDTH, mHEIGHT, monSize, xres, yres
    # grab size of monitor using Tkinter
    try:
        root = tk.Tk()
        mWIDTH = root.winfo_screenwidth()
        mHEIGHT = root.winfo_screenheight()
        print("[INFO] Monitor width: %s" % mWIDTH)
        print("[INFO] Monitor height: %s" % mHEIGHT)
    except:
        print("[WARN] Could not OBTAIN screen size.")
        mWIDTH = 1920
        mHEIGHT = 1080
        print("[WARN] *Fixed* Monitor width: %s" % mWIDTH)
        print("[WARN] *Fixed* Monitor height: %s" % mHEIGHT)
    print('')
    print('')

    # check if monitor is proper resolution
    if(mWIDTH == 1920 and mHEIGHT == 1080): monSize = 1080
    elif(mWIDTH == 1280 and mHEIGHT == 720): monSize = 720
    elif(mWIDTH == 720 and mHEIGHT == 480): monSize = 480
    elif(mWIDTH == 720 and mHEIGHT == 576): monSize = 576
    elif(mWIDTH == 800 and mHEIGHT == 440): monSize = 800
    elif(mWIDTH == 3840 and mHEIGHT == 2160): monSize = 3840
    else: 
        monSize = mHEIGHT # so program will have something to work with
    xres = int(mWIDTH)
    yres = int(mHEIGHT)
    updateScreenSize()
    
#------measure section begin------
def auto_update_edges():
    global thrs1,thrs2, vis
    # compute the median of the single channel pixel intensities
    v = numpy.median(gray)
    # apply automatic Canny edge detection using the computed median
    thrs1 = int(max(0, (a) * v))
    thrs2 = int(min(255, (b) * v))
    edge = cv2.Canny(gray, thrs1, thrs2, apertureSize=5, L2gradient=True)
    vis = cap.copy()
    vis[edge != 0] = (255,0,0) # blue because RGB is reversed
 
def get_edge_image(frame):
    global thrsh1, thrsh2, ex, usePiCameraTF
    global rotated_imagen, rotated_rect, orig_cent, imagen, gray, cap
    ex=False
    screen.fill(black) # blacks out screen
    pygame.display.update()
    label = myfont.render("Capturing Image...", 1, white)    
    screen.blit(label, ((xres/16)*7, (yres/16)*8))
    pygame.display.update()
    frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    #resize image using imutils
    frame = imutils.resize(frame, width=int(xres), height=int(yres))
    height, width, channels = frame.shape
    #rotate image
    frame=numpy.array(frame)
    cap = frame
    gray = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
    auto_update_edges()
    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
    imagen = pygame.surfarray.make_surface(frame)
    if(usePiCameraTF==False):
        imagen = pygame.transform.rotate(imagen,180)
        imagen = pygame.transform.flip(imagen,0,1)
    else:
        imagen = pygame.transform.rotate(imagen,90)
    rotated_imagen = imagen
    rotated_rect=rotated_imagen.get_rect()
    orig_cent = xres/2, yres/2
    rotated_rect.center = orig_cent
    return rotated_imagen

def checkpassword(): 
    global password
    pwnum = ""
    while True:
        pygame.draw.rect(screen,white,((xres/16)*1,(yres/16)*1,(xres/16)*14,(yres/16)*14)) # whites out part of screen
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                cleanQuit()
            if evt.type == KEYDOWN:
                if evt.key == K_BACKSPACE:
                    pwnum = pwnum[:-1]
                elif (  evt.key == K_RETURN
                        or evt.key == K_KP_ENTER
                    ):
                    if pwnum == "7777":
                        password="yes"
                    else:
                        password="no"
                        label = myfont.render("Password Incorrect. Returning to Live Mode", 1, red)
                        screen.blit(label, (xres*.25, yres*.5))
                        pygame.display.update()
                        time.sleep(3)
                        pygame.draw.rect(screen,black,(0,0,xres,yres))
                        pygame.display.update()
                    return()
                elif (  evt.unicode.isdigit()
                     or evt.key == K_PERIOD
                     or evt.key == K_KP_PERIOD
                    ):
                    pwnum += evt.unicode                    
        label = myfont.render("Type Password and press ENTER:", 1, black)
        screen.blit(label, ((xres/16)*2, (yres/16)*2))
        label = myfont.render("CALIBRATION MODE", 1, blue)
        screen.blit(label, ((xres/16)*3, (yres/16)*3))        
        pygame.display.flip()    
    
# asks for size of calibration feature
def name(calibfeature):
    while True:
        pygame.draw.rect(screen,white,((xres/16)*1,(yres/16)*1,(xres/16)*14,(yres/16)*14)) # whites out part of screen
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                cleanQuit()
            if evt.type == KEYDOWN:
                if evt.key == K_BACKSPACE:
                    calibfeature = calibfeature[:-1]
                elif (  evt.key == K_RETURN
                        or evt.key == K_KP_ENTER
                    ):
                    try:
                        a = float(calibfeature)
                    except ValueError:
                        calibfeature = "0"
                    else:
                        return (calibfeature)
                elif (  evt.unicode.isdigit()
                     or evt.key == K_PERIOD
                     or evt.key == K_KP_PERIOD
                    ):
                    calibfeature += evt.unicode                    
        block = myfont.render(calibfeature +" mils", True, red)
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        label = myfont.render("Type calibration feature size in inches, and press ENTER:", 1, black)
        screen.blit(label, ((xres/16)*2, (yres/16)*2))
        label = myfont.render("CALIBRATION MODE", 1, blue)
        screen.blit(label, ((xres/16)*3, (yres/16)*3))        
        pygame.display.flip()

# adjusts lines to size of feature
def calibrate():
    global x1, whichline, x2, x_change, calibfactor, event, rotated_imagen, rotated_rect
    global linecolor, x, y, click_alpha, a, b, imagen, orig_cent, delta, usePiCameraTF, saveFrame1
    s=pygame.Surface((50,2))
    s.fill(white)
    x = 0
    y = 0
    click_alpha = 0
    rot= 0
    rot_val=0
    if(usePiCameraTF):
        vs.capture(path + "temp.jpg")
        saveFrame1 = cv2.imread(path + "temp.jpg")
        saveFrame1=cv2.cvtColor(saveFrame1,cv2.COLOR_RGB2BGR)
        frame = get_edge_image(saveFrame1)
        os.remove(path + "temp.jpg")
        if(usePiCameraTF):
            vs.stopP()
    else:
        frame = get_edge_image(saveFrame1)
    x1 = 0
    x2 = 0
    while True:
        screen.fill(black)
        # check for events
        if click_alpha != 0:
            click_alpha = click_alpha - 10
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # RIGHT click
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1  
                if event.button == 2: # wheel click
                    screen.fill(black)
                    pygame.display.update()
                    label = myfont.render("Returning to Live Mode", 1, white)
                    screen.blit(label, ((xres/16)*5.3, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(1)
                    pygame.draw.rect(screen,black,(0,0,xres,yres))
                    pygame.display.update()
                    if(usePiCameraTF):
                        vs.start()
                    return()
                elif event.button == 1: # LEFT click
                    x, y = event.pos
                    if whichline==1:
                        x1 = find_blue_pixel()
                    elif whichline==2:
                        x2 = find_blue_pixel()
                elif event.button == 4: # wheel up
                        rot_val += .5
                        screen.fill(black)
                elif event.button == 5: # wheel down
                        rot_val -= .5
                        screen.fill(black)
  
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key ==  K_KP4:
                    x_change = -.5 
                if event.key == pygame.K_RIGHT or event.key == K_KP6:
                    x_change = .5
                elif event.key == pygame.K_c:
                    pygame.image.save(screen,"grid.jpg")
                elif event.key == pygame.K_UP or event.key == K_KP8:
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1
                elif event.key == pygame.K_KP_MINUS:
                    pygame.draw.rect(screen,black,((xres/16)*4,(yres/16)*7,(xres/16)*8,(yres/16)*2))
                    pygame.display.update()
                    label = myfont.render("Reducing Edge Detection", 1, white)
                    screen.blit(label, ((xres/16)*5.3, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(0.25)
                    hold_rot_val = rot_val
                    rot=0
                    a=a+.3
                    b=b+.3
                    auto_update_edges()
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    if(usePiCameraTF==False):
                        imagen = pygame.transform.rotate(imagen,180)
                        imagen = pygame.transform.flip(imagen,0,1)
                    else:
                        imagen = pygame.transform.rotate(imagen,90)
                    rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                    rotated_rect=rotated_imagen.get_rect()
                    orig_cent = xres/2, yres/2
                    rotated_rect.center = orig_cent
                    rot_val = hold_rot_val
                elif event.key == pygame.K_KP_PLUS:
                    pygame.draw.rect(screen,black,((xres/16)*4,(yres/16)*7,(xres/16)*8,(yres/16)*2))
                    pygame.display.update()
                    label = myfont.render("Increasing Edge Detection", 1, white)
                    screen.blit(label, ((xres/16)*5.3, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(0.25)
                    hold_rot_val = rot_val
                    rot=0
                    a=a-.3
                    b=b-.3
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    if(usePiCameraTF==False):
                        imagen = pygame.transform.rotate(imagen,180)
                        imagen = pygame.transform.flip(imagen,0,1)
                    else:
                        imagen = pygame.transform.rotate(imagen,90)
                    rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                    rotated_rect=rotated_imagen.get_rect()
                    orig_cent = xres/2, yres/2
                    rotated_rect.center = orig_cent
                    auto_update_edges()
                    rot_val = hold_rot_val
                elif event.key == pygame.K_KP_ENTER:
                    calibfactor = float(calibfeature)/(abs(x1-x2))
                    saveCalData(calibfactor)
                    screen.fill(black)
                    pygame.display.update()
                    label = myfont.render("Cal Feature = " + str(calibfeature) + " mils.", 1, green)
                    screen.blit(label, ((xres/16)*6, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(2)
                    screen.fill(black)
                    pygame.display.update()
                    return()
            if event.type == pygame.KEYUP:
                if ( event.key == pygame.K_LEFT
                     or event.key == pygame.K_RIGHT
                     or event.key == pygame.K_KP4
                     or event.key == pygame.K_KP6
                   ):
                    x_change = 0
        screen.blit(rotated_imagen,rotated_rect)
        if rot != rot_val:
                rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                rotated_rect=rotated_imagen.get_rect()
                rotated_rect.center=orig_cent
                rot = rot_val
        if whichline==1:
            x1=x1+x_change
            pygame.draw.circle(screen, red, (int(x1),60), 10)
            pygame.draw.circle(screen, red, (int(x1),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        elif whichline==2:
            x2=x2+x_change
            pygame.draw.circle(screen, red, (int(x2),60), 10)
            pygame.draw.circle(screen, red, (int(x2),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        pygame.draw.rect(screen,linecolor,(x1,20,1,yres*.91))
        pygame.draw.rect(screen,linecolor,(x2,20,1,yres*.91))
        
        x = xres/16
        y = yres/16
        pygame.draw.rect(screen,black,((xres/16)*1,(yres/16)*14,(xres/8)*7,90))
        label = myfontMC.render("Cal Feature = " + str(calibfeature) + " mils.  Adjust lines and press ENTER", 1, yellow)
        screen.blit(label, (x*5.25, y*14.6))
        
        
        s.set_alpha(click_alpha)
        screen.blit(s, (x-25,y))
        pygame.display.update()

def saveCalData(factor):
    global dataCal, cal480, cal576, cal720, cal800, cal999, cal000, calibfactor, fNameCal, resolution
    if(resolution==480):
        dataCal[0] = factor
        dataCal[1] = dataCal[1]
        dataCal[2] = dataCal[2]
        dataCal[3] = dataCal[3]
        dataCal[4] = dataCal[4]
        dataCal[5] = dataCal[5]
    elif(resolution==576):
        dataCal[0] = dataCal[0]
        dataCal[1] = factor
        dataCal[2] = dataCal[2]
        dataCal[3] = dataCal[3]
        dataCal[4] = dataCal[4]
        dataCal[5] = dataCal[5]
    elif(resolution==720):
        dataCal[0] = dataCal[0]
        dataCal[1] = dataCal[1]
        dataCal[2] = factor
        dataCal[3] = dataCal[3]
        dataCal[4] = dataCal[4]
        dataCal[5] = dataCal[5]
    elif(resolution==800):
        dataCal[0] = dataCal[0]
        dataCal[1] = dataCal[1]
        dataCal[2] = dataCal[2]
        dataCal[3] = factor
        dataCal[4] = dataCal[4]
        dataCal[5] = dataCal[5]
    elif(resolution==999):
        dataCal[0] = dataCal[0]
        dataCal[1] = dataCal[1]
        dataCal[2] = dataCal[2]
        dataCal[3] = dataCal[3]
        dataCal[4] = factor
        dataCal[5] = dataCal[5]
    elif(resolution==0):
        dataCal[0] = dataCal[0]
        dataCal[1] = dataCal[1]
        dataCal[2] = dataCal[2]
        dataCal[3] = dataCal[3]
        dataCal[4] = dataCal[4]
        dataCal[5] = factor
    try:
        numpy.save(fNameCal,dataCal)
    except:
        print("[WARN] Could not save calibration: %s" % fNameCal)

def loadCalData():
    global dataCal, cal480, cal576, cal720, cal800, cal999, call000, calibfactor, fNameCal, resolution
    try:
        dataCal = numpy.load(fNameCal)
    except:
        print("[WARN] Could not load calibration: %s" % fNameCal)
    try:
        if(resolution==480):
            factor = dataCal[0]
            dataCal[1] = dataCal[1]
            dataCal[2] = dataCal[2]
            dataCal[3] = dataCal[3]
            dataCal[4] = dataCal[4]
            dataCal[5] = dataCal[5]
        elif(resolution==576):
            dataCal[0] = dataCal[0]
            factor = dataCal[1]
            dataCal[2] = dataCal[2]
            dataCal[3] = dataCal[3]
            dataCal[4] = dataCal[4]
            dataCal[5] = dataCal[5]
        elif(resolution==720):
            dataCal[0] = dataCal[0]
            dataCal[1] = dataCal[1]
            factor = dataCal[2]
            dataCal[3] = dataCal[3]
            dataCal[4] = dataCal[4]
            dataCal[5] = dataCal[5]
        elif(resolution==800):
            dataCal[0] = dataCal[0]
            dataCal[1] = dataCal[1]
            dataCal[2] = dataCal[2]
            factor = dataCal[3]
            dataCal[4] = dataCal[4]
            dataCal[5] = dataCal[5]
        elif(resolution==999):
            dataCal[0] = dataCal[0]
            dataCal[1] = dataCal[1]
            dataCal[2] = dataCal[2]
            dataCal[3] = dataCal[3]
            factor = dataCal[4]
            dataCal[5] = dataCal[5]
        elif(resolution==0):
            dataCal[0] = dataCal[0]
            dataCal[1] = dataCal[1]
            dataCal[2] = dataCal[2]
            dataCal[3] = dataCal[3]
            dataCal[4] = dataCal[4]
            factor = dataCal[5]
        calibfactor = factor
    except:
        print("[WARN] Could not set loaded calibration values")
        dataCal = [1,1,1,1,1,1]
        calibfactor = 1
    print("[INFO] Calibration data loaded: %s" % dataCal)
        

def find_blue_pixel():
    global bluex, click_alpha
    screen.blit(rotated_imagen,rotated_rect) # if this isn't done, location is screwed up by covering
    pygame.display.update()
    click_alpha = 255
    if x<52 or x>1868:
        bluex = x
        return bluex
    for i in range(25):
        if screen.get_at((x-1+i,y)) == (0, 0, 255, 255):
            bluex=x-1+i
            break
        if screen.get_at((x+1-i,y)) == (0, 0, 255, 255):
            bluex=x+1-i
            break
        bluex = x
    return bluex

# measures a still image                    
def measuremode():
    global x1, whichline, x2, x_change, calibfactor, event, rotated_imagen, rotated_rect
    global linecolor, x, y, click_alpha, a, b, imagen, orig_cent, myfont, myfont
    global myfont, myfont, myfont, saveFrame1, usePiCameraTF
    s=pygame.Surface((50,2))
    s.fill(white)
    x = 0
    y = 0
    click_alpha = 0
    rot= 0
    rot_val=0
    if(usePiCameraTF):
        vs.capture(path + "temp.jpg")
        saveFrame1 = cv2.imread(path + "temp.jpg")
        saveFrame1=cv2.cvtColor(saveFrame1,cv2.COLOR_RGB2BGR)
        frame = get_edge_image(saveFrame1)
        os.remove(path + "temp.jpg")
        if(usePiCameraTF):
            vs.stopP()
    else:
        frame = get_edge_image(saveFrame1)
    x1 = 0
    x2 = 0

    print("[INFO] xres: %s" %xres)
    print("[INFO] yres: %s" %yres)
    print("[INFO] resolution is now: %s" % resolution)
    while True:
        screen.fill(black)
        # check for events
        if click_alpha != 0:
            click_alpha = click_alpha - 10
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # RIGHT click
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1  
                if event.button == 2: # wheel click
                    pygame.draw.rect(screen,black,((xres/16)*4,(yres/16)*7,(xres/16)*8,(yres/16)*2))
                    pygame.display.update()
                    label = myfont.render("Returning to Live Mode", 1, white)
                    screen.blit(label, ((xres/16)*5.5, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(1)
                    pygame.draw.rect(screen,black,(0,0,xres,yres))
                    pygame.display.update()
                    if(usePiCameraTF):
                        vs.start()
                    return()
                elif event.button == 1: # LEFT click
                    x, y = event.pos
                    if whichline==1:
                        x1 = find_blue_pixel()
                    elif whichline==2:
                        x2 = find_blue_pixel()
                elif event.button == 4: # wheel up
                        rot_val += .5
                        screen.fill(black)
                elif event.button == 5: # wheel down
                        rot_val -= .5
                        screen.fill(black)
  
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key ==  K_KP4:
                    x_change = -.5 
                if event.key == pygame.K_RIGHT or event.key == K_KP6:
                    x_change = .5
                elif event.key == pygame.K_c:
                    pygame.image.save(screen,"grid.jpg")
                elif event.key == pygame.K_UP or event.key == K_KP8:
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1
                elif event.key == pygame.K_KP_MINUS:
                    offsetX = 200
                    offsetY = 0
                    pygame.draw.rect(screen,black,((xres/16)*4,(yres/16)*7,(xres/16)*8,(yres/16)*2))
                    pygame.display.update()
                    label = myfont.render("Reducing Edge Detection", 1, white)
                    screen.blit(label, ((xres/16)*5.3, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(0.25)
                    hold_rot_val = rot_val
                    rot=0
                    a=a+.3
                    b=b+.3
                    auto_update_edges()
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    if(usePiCameraTF==False):
                        imagen = pygame.transform.rotate(imagen,180)
                        imagen = pygame.transform.flip(imagen,0,1)
                    else:
                        imagen = pygame.transform.rotate(imagen,90)
                    rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                    rotated_rect=rotated_imagen.get_rect()
                    orig_cent = xres/2, yres/2
                    rotated_rect.center = orig_cent
                    rot_val = hold_rot_val
                elif event.key == pygame.K_KP_PLUS:
                    pygame.draw.rect(screen,black,((xres/16)*4,(yres/16)*7,(xres/16)*8,(yres/16)*2))
                    pygame.display.update()
                    label = myfont.render("Increasing Edge Detection", 1, white)
                    screen.blit(label, ((xres/16)*5.3, (yres/16)*7.5))
                    pygame.display.update()
                    time.sleep(0.25)
                    hold_rot_val = rot_val
                    rot=0
                    a=a-.3
                    b=b-.3
                    auto_update_edges()
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    if(usePiCameraTF==False):
                        imagen = pygame.transform.rotate(imagen,180)
                        imagen = pygame.transform.flip(imagen,0,1)
                    else:
                        imagen = pygame.transform.rotate(imagen,90)
                    rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                    rotated_rect=rotated_imagen.get_rect()
                    orig_cent = xres/2, yres/2
                    rotated_rect.center = orig_cent
                    auto_update_edges()
                    rot_val = hold_rot_val
                elif event.key == pygame.K_KP_ENTER:
                    if linecolor == red:
                        linecolor = black
                    elif linecolor == black:
                        linecolor = white
                    elif linecolor == white:
                        linecolor = blue
                    elif linecolor == blue:
                        linecolor = yellow
                    elif linecolor == yellow:
                        linecolor = magenta
                    elif linecolor ==magenta:
                        linecolor = cyan
                    elif linecolor == cyan:
                        linecolor = red
            if event.type == pygame.KEYUP:
                if ( event.key == pygame.K_LEFT
                     or event.key == pygame.K_RIGHT
                     or event.key == pygame.K_KP4
                     or event.key == pygame.K_KP6
                   ):
                    x_change = 0
        screen.blit(rotated_imagen,rotated_rect)
        if rot != rot_val:
                rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                rotated_rect=rotated_imagen.get_rect()
                rotated_rect.center=orig_cent
                rot = rot_val
        if whichline==1:
            x1=x1+x_change
            pygame.draw.circle(screen, red, (int(x1),60), 10)
            pygame.draw.circle(screen, red, (int(x1),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        elif whichline==2:
            x2=x2+x_change
            pygame.draw.circle(screen, red, (int(x2),60), 10)
            pygame.draw.circle(screen, red, (int(x2),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        pygame.draw.rect(screen,linecolor,(x1,20,1,yres*.91))
        pygame.draw.rect(screen,linecolor,(x2,20,1,yres*.91))

        x = xres/16
        y = yres/16
        pygame.draw.rect(screen,black,((xres/16)*1,(yres/16)*14,(xres/8)*7,90))
        label = myfontMC.render("Measure Mode (frozen Image)                                                                                                   " + delta + " mils", 1, red)
        screen.blit(label, (x*2, y*14))
        label = myfontMC.render("Press wheel for Live Mode, Left click to position line, Right Click to switch lines, R/L arrows to adjust line", 1, white)
        screen.blit(label, (x*2, y*14.6))
        label = myfontMC.render("Rotate wheel to rotate image,   +/- to adjust Edge Detection,   ENTER to change color", 1, white)
        screen.blit(label, (x*2, y*15.2))

        
        s.set_alpha(click_alpha)
        screen.blit(s, (x-25,y))
        pygame.display.update()

# shows rectangle and label with directions
def preview_box(val):
    global screen

    # splits the screen into 32 sections
    x = xres/32
    y = yres/32

    # create second surface for semi-transparent rectangle
    s = pygame.Surface((xres,90))  # the size of your rect
    s.set_alpha(100)                # alpha level
    s.fill(black)           # this fills the entire surface
    screen.blit(s, (0,y*28))    # (0,0) are the top-left coordinates

    # create third surface for semi-transparent rectangle
    s = pygame.Surface((xres,25))  # the size of your rect
    s.set_alpha(100)                # alpha level
    s.fill(black)           # this fills the entire surface
    screen.blit(s, (0,0))    # (0,0) are the top-left coordinates
    
    # starts all text and surfaces at same spot in x direction
    xOffset = 0.5
    yOffset = 27.9
    yOffset1 = yOffset + 1.5
    yOffset2 = yOffset1 + 1.5
    # .rect(screen,color,(x,y,width,height),thickness)    
    if(val==1):
        label = myfont.render("Live Mode. Press '+' to save image.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset2))
    elif(val==2):
        text=myfont.render(imgText, 1,white)
        screen.blit(text, (x*xOffset, y*0.1))
        label = myfont.render("Live Mode.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset))
        label = myfont.render("Press number keys to view img or '+' to save image.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset1))
        label = myfont.render("Press '-' to delete saved images.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset2))
    elif(val==3):
        s.fill(black)
        s.set_alpha(255)                # alpha level
        label = myfont.render("Plese move any images you wish to keep out of the 'IMAGES' folder,", 1, white)
        screen.blit(label, (x*xOffset, y*yOffset))
        label = myfont.render("or else you will lose them.", 1, white)
        screen.blit(label, (x*xOffset, y*yOffset1))
        label = myfont.render("Press 'ENTER' to continue.", 1, white)
        screen.blit(label, (x*xOffset, y*yOffset2))
    elif(val==4):
        label = myfont.render("Image Viewer. Press '-' for Live Mode.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset2))
    else:
        label = myfont.render("Oops, this is embarassing. Something went wrong.", 1,white)
        screen.blit(label, (x*xOffset, y*yOffset2))
        
#------measure section end------
        
#------IMG section begin------

# shows rectangle and label with directions
def preview_box_img(val):
    global screen
    stext=myfont.render(str(val), 1,magenta)
    screen.blit(stext, (10, 10))

# shows saved images
def showImg(num):
    global trk, trigger, usePiCameraTF
    if(usePiCameraTF):
        vs.stopP()
    #clear old label by blacking out screen
    screen.fill(black)
    
    if(num==9):
        imag = pygame.image.load(path + "image9.jpg")
    elif(num==8):
        imag = pygame.image.load(path + "image8.jpg")
    elif(num==7):
        imag = pygame.image.load(path + "image7.jpg")
    elif(num==6):
        imag = pygame.image.load(path + "image6.jpg")
    elif(num==5):
        imag = pygame.image.load(path + "image5.jpg")
    elif(num==4):
        imag = pygame.image.load(path + "image4.jpg")
    elif(num==3):
        imag = pygame.image.load(path + "image3.jpg")
    elif(num==2):
        imag = pygame.image.load(path + "image2.jpg")
    elif(num==1):
        imag = pygame.image.load(path + "image1.jpg")

    width = imag.get_width()
    height = imag.get_height()
    
    screen.blit(imag,((mWIDTH/2)-(width/2),(mHEIGHT/2)-(height/2)))
    pygame.display.update()

    preview_box(4)
    pygame.display.update()
    trk = 4
    preview_box(trk)
    while True:
        # check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cleanQuit()
                if event.key == pygame.K_KP_MINUS:
                    trigger = True
                    if(usePiCameraTF):
                        vs.start()
                    screen.fill(black)
                    pygame.display.update()
                    run()

#search any directory for any file or file extension
def find_all(name, path):
    result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            result.append(os.path.join(root, name))
            return True
        else:
            return False

# shows message box
def msgBox():
    global screen, count
    #clear old label by blacking out screen
    screen.fill(black)
    pygame.display.update()
    preview_box(3)
    pygame.display.update()
    x = True
    while x==True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cleanQuit()
                if event.key == pygame.K_KP_ENTER:
                    remOld()
                    x=False
                if event.key == pygame.K_RETURN:
                    remOld()
                    x=False
    count = 1


#delete files
def delFiles(fpath):
    if(os.path.exists(fpath)):
        try:
            os.remove(fpath)
        except OSError as e:
            print("[ERROR] 05: %s - %s." % (e.fpath,e.strerror))
    else:
        print("[WARN] Sorry, I can not find %s file." % fpath)

#search for if images have been saved
def fnd_img():
    global imgText, count
    fnd1 = find_all('image1.jpg', path)
    fnd2 = find_all('image2.jpg', path)
    fnd3 = find_all('image3.jpg', path)
    fnd4 = find_all('image4.jpg', path)
    fnd5 = find_all('image5.jpg', path)
    fnd6 = find_all('image6.jpg', path)
    fnd7 = find_all('image7.jpg', path)
    fnd8 = find_all('image8.jpg', path)
    fnd9 = find_all('image9.jpg', path)

    
    if(fnd9):
        imgText = "Images available: 1,2,3,4,5,6,7,8,9"
        preview_box(2)
        count = 9
        return True
    elif(fnd8):
        imgText = "Images available: 1,2,3,4,5,6,7,8"
        preview_box(2)
        count = 8
        return True
    elif(fnd7):
        imgText = "Images available: 1,2,3,4,5,6,7"
        preview_box(2)
        count = 7
        return True
    elif(fnd6):
        imgText = "Images available: 1,2,3,4,5,6"
        preview_box(2)
        count = 6
        return True
    elif(fnd5):
        imgText = "Images available: 1,2,3,4,5"
        preview_box(2)
        count = 5
        return True
    elif(fnd4):
        imgText = "Images available: 1,2,3,4"
        preview_box(2)
        count = 4
        return True
    elif(fnd3):
        imgText = "Images available: 1,2,3"
        preview_box(2)
        count = 3
        return True
    elif(fnd2):
        imgText = "Images available: 1,2"
        preview_box(2)
        count = 2
        return True
    elif(fnd1):
        imgText = "Images available: 1"
        preview_box(2)
        count = 1
        return True
    else:
        imgText = "No saved images available"
        preview_box(1)
        count = 0
        return False

def remOld():
    #remove old files
    delFiles(path + 'image1.jpg')
    delFiles(path + 'image2.jpg')
    delFiles(path + 'image3.jpg')
    delFiles(path + 'image4.jpg')
    delFiles(path + 'image5.jpg')
    delFiles(path + 'image6.jpg')
    delFiles(path + 'image7.jpg')
    delFiles(path + 'image8.jpg')
    delFiles(path + 'image9.jpg')


def srchImg():
    #search for existing images
    fnd1 = find_all('image1.jpg', path)
    fnd2 = find_all('image2.jpg', path)
    fnd3 = find_all('image3.jpg', path)
    fnd4 = find_all('image4.jpg', path)
    fnd5 = find_all('image5.jpg', path)
    fnd6 = find_all('image6.jpg', path)
    fnd7 = find_all('image7.jpg', path)
    fnd8 = find_all('image8.jpg', path)
    fnd9 = find_all('image9.jpg', path)
    # check for which label to use
    fnd_img()

#------IMG section end------

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

    if(rotozoomChg):
        saveZoomData()
        
    # save frame to use in measuremode and calibration
    saveFrame1 = frame
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


# shows crosshair
def crossHair():
    global screen, crossHairShow
    radius = 100
    width = 3

    if(crossHairShow):
        # .rect(screen,color,(x,y,width,height),thickness)    
        if(crossHairDes==1):
            pygame.draw.circle(screen, green, ((xres/2),(yres/2)),radius,width)
            pygame.draw.circle(screen, green, ((xres/2),(yres/2)),radius/2,width)
            pygame.draw.line(screen, green, ((xres/2)-radius,(yres/2)),((xres/2)+radius,(yres/2)),width)
            pygame.draw.line(screen, green, ((xres/2),(yres/2)-radius),((xres/2),(yres/2)+radius),width)
        elif(crossHairDes==2):
            pygame.draw.circle(screen, magenta, ((xres/2),(yres/2)),radius,width)
            pygame.draw.circle(screen, magenta, ((xres/2),(yres/2)),radius/2,width)
            pygame.draw.line(screen, magenta, ((xres/2)-radius,(yres/2)),((xres/2)+radius,(yres/2)),width)
            pygame.draw.line(screen, magenta, ((xres/2),(yres/2)-radius),((xres/2),(yres/2)+radius),width)
        elif(crossHairDes==3):
            pygame.draw.circle(screen, cyan, ((xres/2),(yres/2)),radius,width)
            pygame.draw.circle(screen, cyan, ((xres/2),(yres/2)),radius/2,width)
            pygame.draw.line(screen, cyan, ((xres/2)-radius,(yres/2)),((xres/2)+radius,(yres/2)),width)
            pygame.draw.line(screen, cyan, ((xres/2),(yres/2)-radius),((xres/2),(yres/2)+radius),width)
    else:
        screen.fill(black)        

# shows message box
def msgBox():
    global screen, count
    #clear old label by blacking out screen
    screen.fill(black)
    pygame.display.update()
    preview_box(3)
    pygame.display.update()
    x = True
    while x==True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cleanQuit()
                if event.key == pygame.K_KP_ENTER:
                    remOld()
                    x=False
                if event.key == pygame.K_RETURN:
                    remOld()
                    x=False
    count = 1

def adjustRes():
    global screen, resolution, xres, yres, label1, mWIDTH, mHEIGHT, myfont, myfontMC, myfontHelp
    myfont = pygame.font.SysFont("Times New Roman", 20) # general info
    myfontHelp = pygame.font.SysFont("monospace", 20) # help info
    if(resolution==480): #480p -> 576p
        xres = 720
        yres = 576
        resolution = 576
        label1 = "576p"
        #adjust font for new resolution
        myfontMC = pygame.font.SysFont("Times New Roman", 12) # measuremode/calibration since there is alot of text
    elif(resolution==576): #576p -> 800x440
        xres = 800
        yres = 440
        resolution = 800
        label1 = "800x440"
        #adjust font for new resolution
        myfontMC = pygame.font.SysFont("Times New Roman", 14) # measuremode/calibration since there is alot of text
    elif(resolution==800): #800x440 -> 720p
        xres = 1280
        yres = 720
        resolution = 720
        label1 = "720p"
        #adjust font for new resolution
        myfontMC = pygame.font.SysFont("Times New Roman", 18) # measuremode/calibration since there is alot of text
    elif(resolution==720): #720p -> current screen resolution (camera may not run higher than 720p)
        getMonSize() # grab the resolution of the monitor
        xres = mWIDTH
        yres = mHEIGHT
        resolution = 999
        label1 = str(mWIDTH) + "x" + str(mHEIGHT)
        if(mHEIGHT>710):
            #adjust font for new resolution
            myfontMC = pygame.font.SysFont("Times New Roman", 18) # measuremode/calibration since there is alot of text
        else:
            #adjust font for new resolution
            myfontMC = pygame.font.SysFont("Times New Roman", 12) # measuremode/calibration since there is alot of text
    elif(resolution==000): #Pi Camera is full screen due to preview mode
        getMonSize() # grab the resolution of the monitor
        #xres = mWIDTH
        #yres = mHEIGHT
        #resolution = 000 # keep it the same in this case
        label1 = str(mWIDTH) + "x" + str(mHEIGHT)
        if(mHEIGHT>710):
            #adjust font for new resolution
            myfontMC = pygame.font.SysFont("Times New Roman", 18) # measuremode/calibration since there is alot of text
        else:
            #adjust font for new resolution
            myfontMC = pygame.font.SysFont("Times New Roman", 12) # measuremode/calibration since there is alot of text
    else: #480p
        xres = 720
        yres = 480
        resolution = 480
        label1 = "480p"
        #adjust font for new resolution
        myfontMC = pygame.font.SysFont("Times New Roman", 12) # measuremode/calibration since there is alot of text

    mWIDTH = xres
    mHEIGHT = yres
    screen.fill(black)
    pygame.display.update()
    try:
        if(usePiCameraTF):
            updateScreenSize()
        else:
            updateScreenSizePiCam()
    except:
        print("[INFO] Resolution not available...")
    val = "Resolution is now: " + label1
    label = myfont.render(val, 1, red)
    screen.blit(label, ((xres/16)*4, (yres/16)*7))
    val = "If the resolution has changed"
    label = myfont.render(val, 1, yellow)
    screen.blit(label, ((xres/16)*4, (yres/16)*8))
    val = "recalibrate for this new resolution."
    label = myfont.render(val, 1, yellow)
    screen.blit(label, ((xres/16)*4, (yres/16)*9))
    pygame.display.update()
    print("[INFO] Resolution is now: %s" % label1)
    time.sleep(1)
    screen.fill(black)
    pygame.display.update()


def saveFrame():
    global usePiCameraTF, count
    count += 1
    if(count>9):
        msgBox()
    if(usePiCameraTF==False):
        global saveFrame1
        # adjust color for saved image...
        saveFrame1 = cv2.cvtColor(saveFrame1,cv2.COLOR_BGR2RGB)
        print("[INFO] Saving frame...%s" % path)
        cv2.imwrite(path + "image%d.jpg" % count, saveFrame1)
    else:
        vs.capture(path + "image%d.jpg" % count)
        saveFrame1 = cv2.imread(path + "image%d.jpg" % count)


    screen.fill(black) # blacks out screen
    pygame.display.update()
    label = myfont.render("Capturing Image...", 1, white)    
    screen.blit(label, ((xres/16)*7, (yres/16)*8))
    label = myfont.render(path+"image" + str(count) + ".jpg", 1, white)    
    screen.blit(label, ((xres/16)*7, (yres/16)*9))
    pygame.display.update()
    time.sleep(0.5)
    screen.fill(black) # blacks out screen
    pygame.display.update()


def cleanQuit():
    global screen, usePiCameraTF, vs
    try:
        if(usePiCameraTF):
            vs.stopP()
    except:
        None
    cv2.destroyAllWindows()
    pygame.quit()    
    sys.exit()

def run():
    global screen, resolution, label1, password, calibfeature, xres, yres, myfont
    global crossHairDes, vs, rotozoomChg, zoom, usePiCameraTF, resolution, crossHairShow
    running = True
    srchImg()
    while running:
        if(usePiCameraTF==False):
            frame=getCamFrame(color,vs)
            screen=blitCamFrame(frame,screen)
        crossHair()
        fnd_img()
        pygame.display.update()
        for event in pygame.event.get(): #process events since last loop cycle
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2: # wheel button
                    #clear old label by blacking out screen
                    screen.fill(black)
                    measuremode()
                    preview_box(trk)
            if event.type == KEYDOWN:
                if event.key == pygame.K_ASTERISK or event.key == pygame.K_KP_MULTIPLY: # '*'
                    print("[INFO] 'Multply' pressed...")
                    if(usePiCameraTF):
                        vs.stopP()
                    #clear old label by blacking out screen
                    screen.fill(black)
                    password = "no"
                    checkpassword()
                    if password == "yes":
                        calibfeature = ""
                        calibfeature = name(calibfeature)
                        calibrate()
                        preview_box(trk)
                        password = "no"
                    else:
                        preview_box(trk)
                    if(usePiCameraTF):
                        vs.start()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: # '+'
                    print("[INFO] 'Plus' pressed... Save Frame")
                    saveFrame()
                    srchImg()
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS: # '-'
                    print("[INFO] 'Minus' pressed...Deleting saved pictures")
                    if(usePiCameraTF):
                        vs.stopP()
                    msgBox()
                    if(usePiCameraTF):
                        vs.start()
                    screen.fill(black)
                    pygame.display.update()
                elif event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE: # '/'
                    print("[INFO] 'Divide' pressed...resolution was: %s, %s" % (resolution, label1))
                    adjustRes()
                    loadCalData()
                elif event.key == pygame.K_KP1: #press numberpad "1" to show first image
                    try: showImg(1) #show image
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP2:
                    try: showImg(2)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP3:
                    try: showImg(3)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP4:
                    try: showImg(4)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP5:
                    try: showImg(5)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP6:
                    try: showImg(6)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP7:
                    try: showImg(7)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP8:
                    try: showImg(8)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_KP9:
                    try: showImg(9)
                    except Exception: print("[WARN] no img")
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    print("[INFO] 'Escape' pressed...quitting now...")
                    cleanQuit()
                elif event.key == pygame.K_z: # zoom
                    rotozoomChg = True
                    if(zoom):
                        zoom=False
                    else:
                        zoom=True
                    print("[INFO] zoom: %s, rotozoomChg: %s" % (zoom,rotozoomChg))
                elif event.key == pygame.K_p: # use picamera/usbcam
                    if(usePiCameraTF):
                        usePiCameraTF = False
                        print("[DEBUG] usePiCameraTF: %s" % usePiCameraTF)
                        print("[INFO] 'p' pressed...switching cameras: Usbcam")
                        vs.stopP()
                    else:
                        usePiCameraTF = True
                        print("[DEBUG] usePiCameraTF: %s" % usePiCameraTF)
                        print("[INFO] 'p' pressed...switching cameras: RPi Cam")
                        resolution=000
                    saveZoomData()
                    vs.stop()
                    gc.collect() # garbage collection
                    init() # reinitialize to use new camera
                elif event.key == pygame.K_c: # change crosshair color
                    print("[INFO] 'c' pressed...changing CrossHair color")
                    crossHairDes+=1
                    if(crossHairDes>3):crossHairDes = 1
                elif event.key == pygame.K_s: # toggle crosshair
                    print("[INFO] 's' pressed...toggling crosshair")
                    if(crossHairShow): crossHairShow = False
                    else: crossHairShow = True
                elif event.key == pygame.K_h: # toggle help screen
                    print("[INFO] 'h' pressed...toggling help")
                    screen.fill(black)
                    header = " ---------------------Help Menu---------------------"
                    hLen = len(header)
                    label = myfontHelp.render(header, 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*4))
                    label = myfontHelp.render("| Press '/' to change resolution.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*4.5))
                    label = myfontHelp.render("| Press 'Esc' to quit.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*5))
                    label = myfontHelp.render("| Press 'z' to toggle zoom function.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*5.5))
                    label = myfontHelp.render("| Press 'p' to toggle between RPi Cam and USB Cam.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*6))
                    label = myfontHelp.render("| Press 'c' to toggle CrossHair.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*6.5))
                    label = myfontHelp.render("| Press 's' to toggle CrossHair colors.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*7))
                    label = myfontHelp.render("| Press 'mouse wheel' to toggle measuremode.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*7.5))
                    label = myfontHelp.render("| Press '*' to calibrate.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*8))
                    label = myfontHelp.render("| Press '+' to save image.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*8.5))
                    label = myfontHelp.render("| Press '-' to clear all saved images.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*9))
                    label = myfontHelp.render("| Press '1-9' on the number pad to view saved images.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*9.5))
                    label = myfontHelp.render(" ".ljust(hLen,"-"), 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*10))
                    pygame.display.update()
                    time.sleep(5)
                    screen.fill(black)
                    pygame.display.update()
                print('')
                print('')
                gc.collect() # garbage collection

                    


#try:
#    init()
#    run()
#    cleanQuit()
#except:
#    print("[ERROR] Closing Program")
#    cleanQuit()
init()
run()
cleanQuit()
