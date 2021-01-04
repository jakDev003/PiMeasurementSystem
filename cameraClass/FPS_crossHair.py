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
    
        
#------IMG section begin------

# shows rectangle and label with directions
def preview_box_img(val):
    global screen
    stext=myfont.render(str(val), 1,magenta)
    screen.blit(stext, (10, 10))
    pygame.display.update()

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
        preview_box_img(imgText)
        count = 9
        return True
    elif(fnd8):
        imgText = "Images available: 1,2,3,4,5,6,7,8"
        preview_box_img(imgText)
        count = 8
        return True
    elif(fnd7):
        imgText = "Images available: 1,2,3,4,5,6,7"
        preview_box_img(imgText)
        count = 7
        return True
    elif(fnd6):
        imgText = "Images available: 1,2,3,4,5,6"
        preview_box_img(imgText)
        count = 6
        return True
    elif(fnd5):
        imgText = "Images available: 1,2,3,4,5"
        preview_box_img(imgText)
        count = 5
        return True
    elif(fnd4):
        imgText = "Images available: 1,2,3,4"
        preview_box_img(imgText)
        count = 4
        return True
    elif(fnd3):
        imgText = "Images available: 1,2,3"
        preview_box_img(imgText)
        count = 3
        return True
    elif(fnd2):
        imgText = "Images available: 1,2"
        preview_box_img(imgText)
        count = 2
        return True
    elif(fnd1):
        imgText = "Images available: 1"
        preview_box_img(imgText)
        count = 1
        return True
    else:
        imgText = "No saved images available"
        preview_box_img(imgText)
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
    imgText = "No saved images available"
    preview_box_img(imgText)
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
            if event.type == KEYDOWN:
                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS: # '+'
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
                    label = myfontHelp.render("| Press '+' to save image.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*7.5))
                    label = myfontHelp.render("| Press '-' to clear all saved images.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*8))
                    label = myfontHelp.render("| Press '1-9' on the number pad to view saved images.".ljust(hLen," ") + "|", 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*8.5))
                    label = myfontHelp.render(" ".ljust(hLen,"-"), 1, white)    
                    screen.blit(label, ((xres/16)*6, (yres/16)*9))
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
