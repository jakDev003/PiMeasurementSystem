# import the necessary packages
from imutils.video import VideoStream
import datetime
import numpy, imutils, time, pygame, cv2, math, sys, os
from pygame.locals import *
 

def orig():
    # initialize the video stream and allow the cammera sensor to warmup
    vs = VideoStream(usePivs=False).start()
    time.sleep(2.0)

    # loop over the frames from the video stream
    while True:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=720) 
            # draw the timestamp on the frame
            timestamp = datetime.datetime.now()
            ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.35, (0, 0, 255), 1)
     
            # show the frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
     
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                    break
     
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
 #----------------------------------------------------------

def init():
    global color, vs, camera_index, screen, screen_width, xres, yres
    global mWIDTH, mHEIGHT, monSize, resolution, label1
    pygame.init()    
    variables()

    color=False
    # initialize the video stream and allow the camera sensor to warmup
    vs = VideoStream(usePiCamera=False).start() # usePiCamera = False for webcam
    time.sleep(2.0)
    resolution = 720
    label1 = "test"

    # set defaults
    getMonSize() # grab the resolution of the monitor

    screen = pygame.display.set_mode((mWIDTH,mHEIGHT), pygame.RESIZABLE)
    print("xres: %s" % xres)
    print("yres: %s" % yres)
    print("monSize: %s" % monSize)
    print('')
    print('')

    # set title of screen
    pygame.display.set_caption("Python Camera Scope")

def updateScreenSize():
    global screen, xres, yres
    screen_width, screen_height = xres, yres
    screen=pygame.display.set_mode((screen_width,screen_height), pygame.RESIZABLE)

# Define variables
def variables():
    global red, black, white, blue
    global yellow, magenta, cyan, green, width, height
    global count, myfont, myfont1, d, trk, myfont2, myfont3, myfont4, crossHairDes
    crossHairDes = 1
    #xres, yres = 1920, 1080 # monitor resolution
    password = "no"
    myfont = pygame.font.SysFont("Times New Roman", 35)
    myfont1 = pygame.font.SysFont("Times New Roman", 25)
    myfont2 = pygame.font.SysFont("Times New Roman", 20) # previewbox
    myfont3 = pygame.font.SysFont("Times New Roman", 18) # 720p measuremode
    myfont4 = pygame.font.SysFont("Times New Roman", 10) # 480p and 576p measuremode
    
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
    
    width = 0
    height = 0
    channels= 0
    count = 0

def getMonSize():
    global mWIDTH, mHEIGHT, monSize, xres, yres
    # grab size of monitor
    infoObject = pygame.display.Info()
    mWIDTH = infoObject.current_w
    mHEIGHT = infoObject.current_h
    #mWIDTH = 720 # test different monitor resolutions (size)
    #mHEIGHT = 480
    print("Monitor width: %s" % mWIDTH)
    print("Monitor height: %s" % mHEIGHT)
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
    xres = mWIDTH
    yres = mHEIGHT
    updateScreenSize()

# shows rectangle and label with directions
def preview_box(val):
    global screen
    # create second surface for semi-transparent rectangle
    s = pygame.Surface(((xres/8)*7,90))  # the size of your rect
    s.set_alpha(128)                # alpha level
    s.fill(white)           # this fills the entire surface
    screen.blit(s, ((xres/16)*1,(yres/16)*14))    # (0,0) are the top-left coordinates
    
    # .rect(screen,color,(x,y,width,height),thickness)    
    if(val==1):
        label = myfont2.render("Live Mode. Press '+' to save image.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*14.35))
    elif(val==2):
        stext=myfont2.render(imgText, 1,magenta)
        screen.blit(stext, (10, 10))
        label = myfont2.render("Live Mode.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*14.1))
        label = myfont2.render("Press number keys to view img or '+' to save image.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*14.6))
        label = myfont2.render("Press '-' to delete saved images.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*15.1))
    elif(val==3):
        s.fill(black)
        s.set_alpha(255)                # alpha level
        screen.blit(s, ((xres/16)*1,(yres/16)*14))    # (0,0) are the top-left coordinates
        label = myfont2.render("Please move any images you wish to keep out of the 'IMAGES' folder,", 1, white)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*7.5))
        label = myfont2.render("or else you will lose them.", 1, white)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*8))
        label = myfont2.render("Press 'ENTER' to continue.", 1, white)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*8.5))
    elif(val==4):
        label = myfont2.render("Image Viewer. Press '-' for Live Mode.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*14.35))
    else:
        label = myfont2.render("Oops, this is embarassing. Something went wrong.", 1, black)
        screen.blit(label, ((xres/16)*2.8, (yres/16)*14.35))

# shows rectangle and label with directions
def preview_box_img(val):
    global screen
    stext=myfont2.render(str(val), 1,magenta)
    screen.blit(stext, (10, 10))



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



def getCamFrame(color,vs):
    global height, width, channels, img, saveFrame
    # grab the frame from the threaded video stream and resize it
    # to have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=720) 
    # adjust color
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    #rotate image
    frame=numpy.rot90(frame)

    # save frame to use in measuremode and calibration
    saveFrame = frame
    # make into pygame surface
    frame=pygame.surfarray.make_surface(frame)
    frame = pygame.transform.flip(frame,True,False)
    return frame

def blitCamFrame(frame,screen):
    global width, height
    width = frame.get_width()
    height = frame.get_height()
    screen.blit(frame,((mWIDTH/2)-(width/2),(mHEIGHT/2)-(height/2)))
    return screen


# shows crosshair
def crossHair():
    global screen
    radius = 100
    width = 3
   # # create second surface for semi-transparent rectangle
   # s = pygame.Surface(((xres/8)*7,90))  # the size of your rect
   # s.set_alpha(128)                # alpha level
   # s.fill(white)           # this fills the entire surface
   # screen.blit(s, ((xres/16)*1,(yres/16)*14))    # (0,0) are the top-left coordinates
    
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
    global screen, resolution, xres, yres, myfont, myfont1, label1
    if(resolution==480): #480p -> 576p
        xres = 720
        yres = 576
        resolution = 576
        label1 = "576p"
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 10) # 'inches' label
        myfont1 = pygame.font.SysFont("Times New Roman", 10) # other stuff label
    elif(resolution==576): #576p -> 800x440
        xres = 800
        yres = 440
        resolution = 800
        label1 = "800x440"
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 12)
        myfont1 = pygame.font.SysFont("Times New Roman", 16)
    elif(resolution==800): #800x440 -> 720p
        xres = 1280
        yres = 720
        resolution = 720
        label1 = "720p"
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 35)
        myfont1 = pygame.font.SysFont("Times New Roman", 25)
    elif(resolution==720): #720p -> current screen resolution (camera may run higher than 720p)
        xres = mWIDTH
        yres = mHEIGHT
        resolution = 999
        label1 = str(mWIDTH) + "x" + str(mHEIGHT)
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 35)
        myfont1 = pygame.font.SysFont("Times New Roman", 25)
    elif(resolution==999):
        xres = 720
        yres = 480
        resolution = 480
        label1 = "480p"
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 10)
        myfont1 = pygame.font.SysFont("Times New Roman", 10)
    else:
        xres = 720
        yres = 480
        resolution = 480
        label1 = "480p"
        #adjust font for new resolution
        myfont = pygame.font.SysFont("Times New Roman", 10)
        myfont1 = pygame.font.SysFont("Times New Roman", 10)

    screen.fill(black)
    pygame.display.update()
    try:
        updateScreenSize()
    except:
        print("Resolution not available...")
    val = "Resolution is now: " + label1
    label = myfont2.render(val, 1, red)
    screen.blit(label, ((xres/16)*4, (yres/16)*7))
    val = "If the resolution has changed"
    label = myfont2.render(val, 1, yellow)
    screen.blit(label, ((xres/16)*4, (yres/16)*8))
    val = "recalibrate for this new resolution."
    label = myfont2.render(val, 1, yellow)
    screen.blit(label, ((xres/16)*4, (yres/16)*9))
    pygame.display.update()
    print("Resolution is now: %s" % label1)
    time.sleep(1)
    screen.fill(black)
    pygame.display.update()

def cleanQuit():
    global screen
    pygame.quit()
    cv2.destroyAllWindows()
    sys.exit()

def run():
    global screen, resolution, label1, password, calibfeature, xres, yres, myfont, myfont1, crossHairDes, vs
    running = True
    adjustRes()
    while running:
        frame=getCamFrame(color,vs)
        screen=blitCamFrame(frame,screen)
        crossHair()
        pygame.display.update()
        for event in pygame.event.get(): #process events since last loop cycle
            if event.type == pygame.QUIT:
                cleanQuit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE: # '/'
                    print("'Divide' pressed...")
                    crossHairDes+=1
                    if(crossHairDes>3):crossHairDes=1
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    print("'Escape' pressed...quitting now...")
                    cleanQuit()

init()
run()
cleanQuit()

