import cv2, os, sys, time, pygame, shelve, picamera, picamera.array
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np

# initialize 
def init():
    pygame.init()
    pygame.mouse.set_visible(True)
    global myfont, myfont1, cam, calibfactor, trk, monSize, mWIDTH, mHEIGHT, screen
    global xres, yres, x1, x2
    myfont = pygame.font.SysFont("Times New Roman", 35)
    myfont1 = pygame.font.SysFont("Times New Roman", 25)
    d = 100
    d = shelve.open('calibration.txt')  # here you will retrieve the cal variable
    calibfactor = d['calibration']
    d.close()
    trk = 1
    keys=pygame.key.get_pressed()

    # set defaults
    getMonSize() # grab the resolution of the monitor
    
    screen = pygame.display.set_mode((mWIDTH,mHEIGHT))
    xres = mWIDTH
    yres = mHEIGHT
    x1= xres * .65
    x2= xres * .35
    print("xres: %s" % xres)
    print("yres: %s" % yres)
    print("monSize: %s" % monSize)
    print("x1: %s" % x1)
    print("x2: %s" % x2)
    print('')
    print('')
    
# Define variables
def variables():
    global whichline, x_change, lsl, usl, password, red, black, white, blue
    global yellow,magenta,cyan, linecolor, a, b, path
    #xres, yres = 1920, 1080 # monitor resolution
    password = "no"
    
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
    path = "/home/pi/Images/"

def getMonSize():
    global mWIDTH, mHEIGHT, monSize
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
    else: 
        print("Please use 720p or 1080p monitor.")
        monSize = 720 # so program will have something to work with


def auto_update_edges():
    global thrs1,thrs2, vis
    # compute the median of the single channel pixel intensities
    v = np.median(gray)
    # apply automatic Canny edge detection using the computed median
    thrs1 = int(max(0, (a) * v))
    thrs2 = int(min(255, (b) * v))
    edge = cv2.Canny(gray, thrs1, thrs2, apertureSize=5, L2gradient=True)
    vis = cap.copy()
    vis[edge != 0] = (255,0,0) # blue becuase RGB is reversed?

    
def get_edge_image():
    global thrsh1, thrsh2, ex
    global rotated_imagen, rotated_rect, orig_cent, imagen, gray, cap
    ex=False
    label = myfont.render("Capturing Image...", 1, white)
    pygame.draw.rect(screen,(0,0,0),(0,0,xres,yres)) # blacks out screen
    screen.blit(label, (xres*.42, yres*.47))
    pygame.display.update()
    rawCapture = PiRGBArray(cam)
    cam.capture(rawCapture, format="bgr")
    cap = rawCapture.array
    cap = cv2.getRectSubPix(cap,(480,270),(960,540))
    cap = cv2.resize(cap,(1920,1080))
    gray = cv2.cvtColor(cap, cv2.COLOR_BGR2GRAY)
    auto_update_edges()
    cam.stop_preview()
    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
    imagen = pygame.surfarray.make_surface(frame)
    imagen = pygame.transform.rotate(imagen,90)
    imagen = pygame.transform.flip(imagen,0,1)
    rotated_imagen = imagen
    rotated_rect=rotated_imagen.get_rect()
    orig_cent = xres/2, yres/2
    rotated_rect.center = orig_cent

def checkpassword(): 
    global password
    pwnum = ""
    while True:
        #print("pwnum: %s" % pwnum)
        pygame.draw.rect(screen,white,(200,200,1520,680)) # whites out part of screen
        for evt in pygame.event.get():
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
        screen.blit(label, (xres*.2, yres*.4))
        label = myfont.render("CALIBRATION MODE", 1, yellow)
        screen.blit(label, (xres*.2, yres*.1))
        screen.blit(label, (xres*.5, yres*.1))        
        pygame.display.flip()    
    
# asks for size of calibration feature
def name(calibfeature):
    while True:
        pygame.draw.rect(screen,white,(200,200,1520,680)) # whites out part of screen
        for evt in pygame.event.get():
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
        block = myfont.render(calibfeature +" mils", True, magenta)
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        label = myfont.render("Type calibration feature size in inches, and press ENTER:", 1, black)
        screen.blit(label, (xres*.2, yres*.4))
        label = myfont.render("CALIBRATION MODE", 1, yellow)
        screen.blit(label, (xres*.2, yres*.1))
        screen.blit(label, (xres*.5, yres*.1))        
        pygame.display.flip()

# adjusts lines to size of feature
def calibrate():
    global x1, whichline, x2, x_change, calibfactor, event, rotated_imagen, rotated_rect
    global linecolor, x, y, click_alpha
    calibfeatureLast = 0
    x1Last = 0
    x2Last = 0
    whichlineLast = 0
    s=pygame.Surface((50,2))
    s.fill(white)
    x = 0
    y = 0
    click_alpha = 0
    rot= 0
    rot_val=0
    get_edge_image()
    while True:
        # check for events
        if click_alpha != 0:
            click_alpha = click_alpha - 10
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cam.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # RIGHT click
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1  
                elif event.button == 1: # LEFT click
                    x, y = event.pos
                    if whichline==1:
                        x1 = find_blue_pixel()
                    elif whichline==2:
                        x2 = find_blue_pixel()
                elif event.button == 4: # wheel up
                        rot_val += .5
                elif event.button == 5: # wheel down
                        rot_val -= .5
  
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
                elif event.key == pygame.K_KP_PLUS:
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
                elif (  event.key == K_RETURN
                        or event.key == K_KP_ENTER
                    ):
                    calibfactor = float(calibfeature)/(abs(x1-x2))
                    d = shelve.open('calibration.txt') # here you will save the cal variable   
                    d['calibration'] = calibfactor          # now it is saved on disk.
                    d.close()
                    pygame.draw.rect(screen,black,(xres*.38,yres*.50,360,45))
                    pygame.display.update()
                    label = myfont.render("Calibration Complete", 1, magenta)
                    screen.blit(label, (xres*.40, yres*.5))
                    pygame.display.update()
                    time.sleep(2)
                    pygame.draw.rect(screen,black,(0,0,xres,yres))
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
            pygame.draw.circle(screen, red, (int(x1),30), 10)
            pygame.draw.circle(screen, red, (int(x1),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        elif whichline==2:
            x2=x2+x_change
            pygame.draw.circle(screen, red, (int(x2),30), 10)
            pygame.draw.circle(screen, red, (int(x2),1010), 10)
            delta=str(round(abs(x2-x1)*calibfactor,5))
        
        row = .865
        col = .3
        print("calibfeature: %s" % calibfeature)
        print("calibfeatureLast: %s" % calibfeatureLast)
        print("x1: %s" % x1)
        print("x2: %s" % x2)
        if(calibfeature<>calibfeatureLast or x1<>x1Last or x2<>x2Last or whichline<>whichlineLast):
            pygame.draw.rect(screen,red,(x1,10,1,yres*.92))
            pygame.draw.rect(screen,red,(x2,10,1,yres*.92))
            pygame.draw.rect(screen,black,(xres*.28,yres*.85,870,80))
            pygame.display.update()
            label = myfont.render("Cal feature = " + str(calibfeature) + " inches.  Adjust lines and press ENTER", 1, yellow)
            screen.blit(label, (xres*col, yres*row))
            pygame.display.update()
            calibfeatureLast = calibfeature
            s.set_alpha(click_alpha)
            screen.blit(s, (x-25,y))
            x1Last = x1
            x2Last = x2
            whichlineLast = whichline
            pygame.display.update()


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
    global linecolor, x, y, click_alpha, a, b, imagen, orig_cent
    s=pygame.Surface((50,2))
    s.fill(white)
    x = 0
    y = 0
    click_alpha = 0
    rot= 0
    rot_val=0
    get_edge_image()
    while True:
        # check for events
        if click_alpha != 0:
            click_alpha = click_alpha - 10
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cam.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3: # RIGHT click
                    if whichline==1:
                        whichline=2
                    elif whichline==2:
                        whichline=1  
                if event.button == 2: # wheel click
                    label = myfont.render("Returning to Live Mode", 1, black)
                    screen.blit(label, (xres*.36, yres*.5))
                    pygame.display.update()
                    time.sleep(1)
                    pygame.draw.rect(screen,black,(0,0,xres,yres))
                    pygame.display.update()
                    return()
                elif event.button == 1: # LEFT click
                    x, y = event.pos
                    if whichline==1:
                        x1 = find_blue_pixel()
                    elif whichline==2:
                        x2 = find_blue_pixel()
                elif event.button == 4: # wheel up
                        rot_val += .5
                elif event.button == 5: # wheel down
                        rot_val -= .5
  
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
                    label = myfont.render("Reducing Edge Detection...", 1, black)
                    screen.blit(label, (xres*.36, yres*.5))
                    pygame.display.update()
                    hold_rot_val = rot_val
                    rot=0
                    a=a+.3
                    b=b+.3
                    auto_update_edges()
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    imagen = pygame.transform.rotate(imagen,90)
                    imagen = pygame.transform.flip(imagen,0,1)
                    rotated_imagen = pygame.transform.rotate(imagen,rot_val)
                    rotated_rect=rotated_imagen.get_rect()
                    orig_cent = xres/2, yres/2
                    rotated_rect.center = orig_cent
                    rot_val = hold_rot_val
                elif event.key == pygame.K_KP_PLUS:
                    label = myfont.render("Increasing Edge Detection...", 1, black)
                    screen.blit(label, (xres*.36, yres*.5))
                    pygame.display.update()
                    hold_rot_val = rot_val
                    rot=0
                    a=a-.3
                    b=b-.3
                    frame=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
                    imagen = pygame.surfarray.make_surface(frame)
                    imagen = pygame.transform.rotate(imagen,90)
                    imagen = pygame.transform.flip(imagen,0,1)
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
        pygame.draw.rect(screen,black,(xres*.07,yres*.84,1560,90))
        label = myfont.render(delta + " inches", 1, red)
        screen.blit(label, (xres*.79, yres*.85))
        label = myfont1.render("Measure Mode", 1, red)
        screen.blit(label, (xres*.08, yres*.85))
        label = myfont1.render("(frozen Image)", 1, red)
        screen.blit(label, (xres*.08, yres*.885))
        label = myfont1.render("Press wheel for Live Mode, Left click to position line, Right Click to switch lines, R/L arrows to adjust line", 1, white)
        screen.blit(label, (xres*.17, yres*.85))
        label = myfont1.render("Rotate wheel to rotate image,   +/- to adjust Edge Detection,   ENTER to change color", 1, white)
        screen.blit(label, (xres*.17, yres*.885))
        s.set_alpha(click_alpha)
        screen.blit(s, (x-25,y))
        pygame.display.update()

# shows rectangle and label with directions
def preview_box(val):
    rowOffset = .05
    col = .08
    # .rect(screen,color,(x,y,width,height),thickness)    
    if(val==1):
        row = .865
        label = myfont.render("Live Mode. Press '+' to save image.", 1, white)
        screen.blit(label, (xres*col, yres*row))
    elif(val==2):
        row = .795
        label = myfont.render("Live Mode.", 1, white)
        screen.blit(label, (xres*col, yres*row))
        label = myfont.render("Press number keys to view img or '+' to save image.", 1, white)
        screen.blit(label, (xres*col, yres*(row+rowOffset)))
        label = myfont.render("Press '-' to delete saved images.", 1, white)
        screen.blit(label, (xres*col, yres*(row+(rowOffset*2))))
    elif(val==3):
        row = .835            
        label = myfont.render("Please move any images you wish to keep out of the 'IMAGES' folder, or else you will lose them.", 1, white)
        screen.blit(label, (xres*col, yres*row))
        label = myfont.render("Press 'ENTER' to continue.", 1, white)
        screen.blit(label, (xres*col, yres*(row+rowOffset)))
    elif(val==4):
        row = .865
        label = myfont.render("Image Viewer. Press '-' for Live Mode.", 1, white)
        screen.blit(label, (xres*col, yres*row))
    else:
        row = .865
        label = myfont.render("Oops, this is embarassing. Something went wrong.", 1, white)
        screen.blit(label, (xres*col, yres*row))

    pygame.display.update()

# shows rectangle and label with directions
def preview_box_img(val):
    font=pygame.font.SysFont("Times New Roman", 35)
    stext=font.render(str(val), 1,white)
    screen.blit(stext, (10, 10))


# shows saved images
def showImg(num):
    global trk
    
    if(num==9):
        imag = pygame.image.load(path + "image8.jpg")
    elif(num==8):
        imag = pygame.image.load(path + "image7.jpg")
    elif(num==7):
        imag = pygame.image.load(path + "image6.jpg")
    elif(num==6):
        imag = pygame.image.load(path + "image5.jpg")
    elif(num==5):
        imag = pygame.image.load(path + "image4.jpg")
    elif(num==4):
        imag = pygame.image.load(path + "image3.jpg")
    elif(num==3):
        imag = pygame.image.load(path + "image2.jpg")
    elif(num==2):
        imag = pygame.image.load(path + "image1.jpg")
    elif(num==1):
        imag = pygame.image.load(path + "image0.jpg")

    screen.blit(imag,(0,0))
    pygame.display.update()
    trk = 4
    preview_box(trk)
    while True:
        # check for events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cam.close()
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_KP_MINUS:
                    cam.start_preview(alpha=200)
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                    mainLp()


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
def msgBox(msg):
    #clear old label by blacking out screen
    screen.fill(black)
    pygame.display.update()
    preview_box(3)
    x = True
    while x==True:
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
                if event.key == pygame.K_KP_ENTER:
                    remOld()
                    x=False
                if event.key == pygame.K_RETURN:
                    remOld()
                    x=False
    #clear old label by blacking out screen
    screen.fill(black)
    #check for which label to use
    fnd_img()


#delete files
def delFiles(fpath):
    if(os.path.exists(fpath)):
        try:
            os.remove(fpath)
        except OSError as e:
            print("Error: %s - %s." % (e.fpath,e.strerror))
    else:
        print("Sorry, I can not find %s file." % fpath)

#search for if images have been saved
def fnd_img():
    global screen
    #clear old label by blacking out screen
    screen.fill(black)
    fnd1 = find_all('image0.jpg', path)
    fnd2 = find_all('image1.jpg', path)
    fnd3 = find_all('image2.jpg', path)
    fnd4 = find_all('image3.jpg', path)
    fnd5 = find_all('image4.jpg', path)
    fnd6 = find_all('image5.jpg', path)
    fnd7 = find_all('image6.jpg', path)
    fnd8 = find_all('image7.jpg', path)
    fnd9 = find_all('image8.jpg', path)
    
    if(fnd9):
        print("9...")
        preview_box_img("Images available: 1,2,3,4,5,6,7,8,9")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd8):
        print("8...")
        preview_box_img("Images available: 1,2,3,4,5,6,7,8")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd7):
        print("7...")
        preview_box_img("Images available: 1,2,3,4,5,6,7")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd6):
        print("6...")
        preview_box_img("Images available: 1,2,3,4,5,6")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd5):
        print("5...")
        preview_box_img("Images available: 1,2,3,4,5")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd4):
        print("4...")
        preview_box_img("Images available: 1,2,3,4")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd3):
        print("3...")
        preview_box_img("Images available: 1,2,3")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd2):
        print("2...")
        preview_box_img("Images available: 1,2")
        #update screen with new label
        preview_box(2)
        return True
    elif(fnd1):
        print("1...")
        preview_box_img("Images available: 1")
        #update screen with new label
        preview_box(2)
        return True
    else:
        print("...")
        preview_box_img("No saved images available")
        #update screen with new label
        preview_box(1)
        return False

def remOld():
    #remove old files
    delFiles(path + 'image0.jpg')
    delFiles(path + 'image1.jpg')
    delFiles(path + 'image2.jpg')
    delFiles(path + 'image3.jpg')
    delFiles(path + 'image4.jpg')
    delFiles(path + 'image5.jpg')
    delFiles(path + 'image6.jpg')
    delFiles(path + 'image7.jpg')
    delFiles(path + 'image8.jpg')

def mainLp():
    global password, calibfeature
    while True:
        # check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cam.close()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2: # wheel button
                    #clear old label by blacking out screen
                    screen.fill(black)
                    measuremode()
                    preview_box(trk)
                    cam.start_preview(alpha=200)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cam.close()
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_KP1: #press numberpad "1" to show first image
                    cam.stop_preview() #cancel camera preview so image will appear
                    try: showImg(1) #show image
                    except Exception: print("no img")
                if event.key == pygame.K_KP2:
                    cam.stop_preview()
                    try: showImg(2)
                    except Exception: print("no img")
                if event.key == pygame.K_KP3:
                    cam.stop_preview()
                    try: showImg(3)
                    except Exception: print("no img")
                if event.key == pygame.K_KP4:
                    cam.stop_preview()
                    try: showImg(4)
                    except Exception: print("no img")
                if event.key == pygame.K_KP5:
                    cam.stop_preview()
                    try: showImg(5)
                    except Exception: print("no img")
                if event.key == pygame.K_KP6:
                    cam.stop_preview()
                    try: showImg(6)
                    except Exception: print("no img")
                if event.key == pygame.K_KP7:
                    cam.stop_preview()
                    try: showImg(7)
                    except Exception: print("no img")
                if event.key == pygame.K_KP8:
                    cam.stop_preview()
                    try: showImg(8)
                    except Exception: print("no img")
                if event.key == pygame.K_KP9:
                    cam.stop_preview()
                    try: showImg(9)
                    except Exception: print("no img")
                if event.key == pygame.K_KP_PLUS:
		    #search for existing images
                    fnd1 = find_all('image0.jpg', path)
                    fnd2 = find_all('image1.jpg', path)
                    fnd3 = find_all('image2.jpg', path)
                    fnd4 = find_all('image3.jpg', path)
                    fnd5 = find_all('image4.jpg', path)
                    fnd6 = find_all('image5.jpg', path)
                    fnd7 = find_all('image6.jpg', path)
                    fnd8 = find_all('image7.jpg', path)
                    fnd9 = find_all('image8.jpg', path)
                    #if found look for next image, use next available file name
                    if(fnd1==False):
                        cam.capture(path + 'image0.jpg', use_video_port = True)
                    elif(fnd2==False):
                        cam.capture(path + 'image1.jpg', use_video_port = True)
                    elif(fnd3==False):
                        cam.capture(path + 'image2.jpg', use_video_port = True)
                    elif(fnd4==False):
                        cam.capture(path + 'image3.jpg', use_video_port = True)
                    elif(fnd5==False):
                        cam.capture(path + 'image4.jpg', use_video_port = True)
                    elif(fnd6==False):
                        cam.capture(path + 'image5.jpg', use_video_port = True)
                    elif(fnd7==False):
                        cam.capture(path + 'image6.jpg', use_video_port = True)
                    elif(fnd8==False):
                        cam.capture(path + 'image7.jpg', use_video_port = True)
                    elif(fnd9==False):
                        cam.capture(path + 'image8.jpg', use_video_port = True)
                    else:
                        msgBox("Please remove any images you would like to keep now or they will be deleted\n Press \'Ctrl\' + \'Tab\' to switch between buttons.")
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                if event.key == pygame.K_KP_MINUS:
                    msgBox("Please remove any images you would like to keep now or they will be deleted\n Press \'Ctrl\' + \'Tab\' to switch between buttons.")
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                elif event.key == pygame.K_KP_MULTIPLY:
                    #clear old label by blacking out screen
                    screen.fill(black)
                    # stop camera
                    cam.stop_preview()
                    password = "no"
                    checkpassword()
                    if password == "yes":
                        calibfeature = ""
                        calibfeature = name(calibfeature)
                        calibrate()
                        preview_box(trk)
                        cam.start_preview(alpha=200)
                        password = "no"
                    else:
                        preview_box(trk)
                        cam.start_preview(alpha=200)
                else:
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                    #show camera preview
                    cam.start_preview(alpha=200)
                    
          
#  start here
variables()
init()
#pygame.display.toggle_fullscreen()
preview_box(trk)
cam = picamera.PiCamera(sensor_mode=1)
cam.start_preview(alpha=230)
cam.vflip = False
cam.hflip = False
mainLp()

                    
