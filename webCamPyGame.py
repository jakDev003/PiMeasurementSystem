#/usr/bin/python
from collections import namedtuple
import cv2, os, sys, time, pygame, shelve, picamera, picamera.array, pygame.camera
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np

# initialize
def init():    
    global myfont, myfont1, myfont2, myfont3, cam, calibfactor, screen, xres, yres, img, xFudge, yFudge, mWIDTH, mHEIGHT
    global red, blue, green, white, black, cyan, yellow, magenta, WIDTH, HEIGHT, whichline, x1, x2, x_change, passwordVal
    global linecolor, a, b, run, monSize, savePrevImagen, imagen

    run = True

    Color = namedtuple("Color","R G B")
    # define colors
    red = Color(255, 0, 0)
    blue = Color(0, 0, 255)
    green = Color(0, 255, 0)
    white = Color(255, 255, 255)
    black = Color(0, 0, 0)
    cyan = Color(0,255,255)
    magenta = Color(255,0,255)
    yellow = Color(255,255,0)

    pygame.init()
    pygame.camera.init()

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
        msgBoxTkinter("Please use 720p or 1080p monitor.")
        monSize = 720 # so program will have something to work with

    # grab list of cameras and select first on list
    cam_list = pygame.camera.list_cameras()
    print("Using camera %s ..." % cam_list[0])

    # set camera window to slightly smaller and monitor size
    cam = pygame.camera.Camera(cam_list[0],(mWIDTH-25,mHEIGHT-75))
    cam.start()

    #grab first image
    img = cam.get_image()
    savePrevImagen = img
    imagen = img

    # grab size of camera image
    WIDTH = img.get_width()
    HEIGHT = img.get_height()
    print("Camera width: %s" % WIDTH)
    print("Camera height: %s" % HEIGHT)
    

    # screen resolution to use throughout program
    xres = mWIDTH
    yres = mHEIGHT

    # measuremode variables
    whichline = 1
    x1= xres * .65
    x2= xres * .35
    x_change=0
    usl = ""
    lsl = ""
    a=3
    b=3
    linecolor = red

    # calibration variables
    d = 100
    d = shelve.open('calibration.txt')  # here you will retrieve the cal variable
    calibfactor = d['calibration']
    d.close()
    passwordVal = "7777"

    # window offsets for raspbian toolbar
    xFudge = 100
    yFudge = 100
    
    screen = pygame.display.set_mode((WIDTH,HEIGHT)) # monitor window size (full screen)
    pygame.display.set_caption("pyGame USB camera view")

    myfont = pygame.font.SysFont("Times New Roman", 25)
    myfont1 = pygame.font.SysFont("Times New Roman", 15)
    myfont2 = pygame.font.SysFont("Times New Roman", 30)
    myfont3 = pygame.font.SysFont("Times New Roman", 50)

def msgBoxTkinter(msg):
    if sys.version_info < (3,0):
        import Tkinter as tkinter
        import tkMessageBox as mbox
    else:
        import tkinter
        import tkinter.messagebox as mbox
    window = tkinter.Tk()
    window.wm_withdraw()
    mbox.showinfo('warning',msg)
    window.destroy()

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
    label = myfont.render("Capturing Image...", 1, black)
    screen.fill([0,0,0]) # blanks out screen
    if(monSize==1080):
        screen.blit(label, (xres*.42, yres*.47))
    else:
        screen.blit(label, (xres*.42, yres*.47))
    pygame.display.update()
    cam.stop()
    bgr_img = cv2.imread("/home/pi/meas.jpg")
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
    cap = bgr_img
    auto_update_edges()
    frame = cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
    imagen = pygame.surfarray.make_surface(frame)
    imagen = pygame.transform.rotate(imagen,90)
    imagen = pygame.transform.flip(imagen,0,1)
    screen.fill(black) # blanks out screen
    rotated_imagen = imagen
    rotated_rect=rotated_imagen.get_rect()
    orig_cent = xres/2, yres/2
    rotated_rect.center = orig_cent

def checkpassword(): 
    global password
    password = ""
    pwnum = ""
    while True:
        screen.fill(white) # blanks out screen
        for evt in pygame.event.get():
            if evt.type == KEYDOWN:
                if evt.key == K_BACKSPACE:
                    pwnum = pwnum[:-1]
                elif (  evt.key == K_RETURN
                        or evt.key == K_KP_ENTER
                    ):
                    if pwnum == passwordVal:
                        password="yes"
                    else:
                        password="no"
                        label = myfont.render("Password Incorrect. Returning to Live Mode", 1, red)
                        if(monSize==1080):
                            screen.blit(label, (xres*.25, yres*.5))
                        else:
                            screen.blit(label, (xres*.25, yres*.5))
                        pygame.display.update()
                        time.sleep(3)
                        screen.fill(black) # blanks out screen
                        pygame.display.update()
                    return()
                elif (  evt.unicode.isdigit()
                     or evt.key == K_PERIOD
                     or evt.key == K_KP_PERIOD
                    ):
                    pwnum += evt.unicode                    
        label = myfont.render("Type Password and press ENTER:", 1, black)
        if(monSize==1080):
            screen.blit(label, (xres*.35, yres*.2))
        else:
            screen.blit(label, (xres*.35, yres*.2))
        label = myfont.render("CALIBRATION MODE", 1, yellow)
        if(monSize==1080):
            screen.blit(label, (xres*.38, yres*.1))
        else:
            screen.blit(label, (xres*.38, yres*.1))
        pygame.display.flip()    
    
# asks for size of calibration feature
def name(calibfeature):
    while True:
        screen.fill(white) # blanks out screen
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
        block = myfont.render(calibfeature +" mils", True, black)
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        label = myfont.render("Type calibration feature size in inches, and press ENTER:", 1, black)
        if(monSize==1080):
            screen.blit(label, (xres*.26, yres*.4))
        else:
            screen.blit(label, (xres*.26, yres*.4))
        label = myfont.render("CALIBRATION MODE", 1, yellow)
        if(monSize==1080):
            screen.blit(label, (xres*.5, yres*.1))
        else:
            screen.blit(label, (xres*.5, yres*.1))
        pygame.display.flip()

# adjusts lines to size of feature
def calibrate():
    global x1, whichline, x2, x_change, calibfactor, event, rotated_imagen, rotated_rect
    global linecolor, x, y, click_alpha, a, b, imagen, orig_cent
    screen.fill(white) # blanks out screen
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
                cam.stop()
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
                elif event.key == pygame.K_KP_MINUS:
                    label = myfont.render("Reducing Edge Detection...", 1, (0,0,0))
                    if(monSize==1080):
                        screen.blit(label, (xres*.33, yres*.5))
                    else:
                        screen.blit(label, (xres*.33, yres*.5))
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
                    label = myfont.render("Increasing Edge Detection...", 1, (0,0,0))
                    if(monSize==1080):
                        screen.blit(label, (xres*.33, yres*.5))
                    else:
                        screen.blit(label, (xres*.33, yres*.5))
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
##                elif event.key == pygame.K_KP_PLUS:
##                    if linecolor == red:
##                        linecolor = black
##                    elif linecolor == black:
##                        linecolor = white
##                    elif linecolor == white:
##                        linecolor = blue
##                    elif linecolor == blue:
##                        linecolor = yellow
##                    elif linecolor == yellow:
##                        linecolor = magenta
##                    elif linecolor ==magenta:
##                        linecolor = cyan
##                    elif linecolor == cyan:
##                        linecolor = red
                elif (  event.key == K_RETURN or event.key == K_KP_ENTER ):
                    calibfactor = float(calibfeature)/(abs(x1-x2))
                    d = shelve.open('calibration.txt') # here you will save the cal variable   
                    d['calibration'] = calibfactor          # now it is saved on disk.
                    d.close()
                    label = myfont.render("Calibration Complete", 1, (0,0,0))
                    screen.blit(label, (xres*.36, yres*.5))
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
        pygame.draw.rect(screen,red,(x1,10,1,yres*.92))
        pygame.draw.rect(screen,red,(x2,10,1,yres*.92))
        if(monSize==1080):
            pygame.draw.rect(screen,black,(xres*.10,yres*.82,xres*.65,yres*.10)) # top left x, top left y, length, width
        else:
            pygame.draw.rect(screen,black,(xres*.10,yres*.82,xres*.78,yres*.10)) # top left x, top left y, length, width
        msg = "Cal feature = " + str(calibfeature) + " inches.  Adjust lines and press ENTER"
        label = myfont.render(msg, 1, yellow)
        if(monSize==1080):
            screen.blit(label, (xres*.30, yres*.85))
        else:
            screen.blit(label, (xres*.28, yres*.84))
        label = myfont1.render("Press '+' or '-' to increase/decrease Edge Detection.", 1, green)
        if(monSize==1080):
            screen.blit(label, (xres*.38, yres*.88))
        else:
            screen.blit(label, (xres*.36, yres*.87))
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
    screen.fill(black) # blanks out screen
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
                    label = myfont3.render("Returning to Live Mode", 1, red)
                    if(monSize==1080):
                        screen.blit(label, (xres*.33, yres*.5))
                    else:
                        screen.blit(label, (xres*.33, yres*.5))
                    pygame.display.update()
                    time.sleep(1)
                    screen.fill(black) # blanks out screen
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
                    label = myfont.render("Reducing Edge Detection...", 1, (0,0,0))
                    if(monSize==1080):
                        screen.blit(label, (xres*.33, yres*.5))
                    else:
                        screen.blit(label, (xres*.33, yres*.5))
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
                    label = myfont.render("Increasing Edge Detection...", 1, (0,0,0))
                    if(monSize==1080):
                        screen.blit(label, (xres*.33, yres*.5))
                    else:
                        screen.blit(label, (xres*.33, yres*.5))
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
        if(monSize==1080):
            pygame.draw.rect(screen,black,(xres*.10,yres*.82,xres*.65,yres*.10)) # top left x, top left y, length, width
        else:
            pygame.draw.rect(screen,black,(xres*.10,yres*.82,xres*.75,yres*.10)) # top left x, top left y, length, width
        label = myfont.render(delta + " inches", 1, red)
        if(monSize==1080):
            screen.blit(label, (xres*.65, yres*.84))
        else:
            screen.blit(label, (xres*.70, yres*.87))
        label = myfont2.render("Measure Mode", 1, red)
        if(monSize==1080):
            screen.blit(label, (xres*.11, yres*.84))
        else:
            screen.blit(label, (xres*.11, yres*.84))
        label = myfont1.render("(frozen Image)", 1, red)
        if(monSize==1080):
            screen.blit(label, (xres*.11, yres*.88))
        else:
            screen.blit(label, (xres*.11, yres*.88))
        label = myfont1.render("Press wheel for Live Mode, Left click to position line, Right Click to switch lines, R/L arrows to adjust line", 1, cyan)
        if(monSize==1080):
            screen.blit(label, (xres*.26, yres*.84))
        else:
            screen.blit(label, (xres*.26, yres*.84))
        label = myfont1.render("Rotate wheel to rotate image.", 1, yellow)
        if(monSize==1080):
            screen.blit(label, (xres*.26, yres*.86))
        else:
            screen.blit(label, (xres*.26, yres*.86))
        label = myfont1.render("Press '+' or '-' to increase/decrease Edge Detection.", 1, green)
        if(monSize==1080):
            screen.blit(label, (xres*.26, yres*.88))
        else:
            screen.blit(label, (xres*.26, yres*.88))
        pygame.display.update()    

def preview_box():
    if(monSize==1080):
        x = xres * .16 # position of top right corner
        y = yres * .26 # position of top rignt corner
        xV = xres - (xres * .5) # height
        yV = yres - (yres * .5) # width
    else:
        x = xres * .24 # position of top right corner
        y = yres * .26 # position of top rignt corner
        xV = xres - (xres * .5) # height
        yV = yres - (yres * .5) # width

    pygame.draw.rect(screen,white,(x,y,xV,yV),2)
    label = myfont3.render("Live Mode. Press Wheel for Measure Mode.", 1, red)
    if(monSize==1080):
        screen.blit(label, (xres*.18, yres*.76))
    else:
        screen.blit(label, (xres*.16, yres*.76))
    pygame.display.update()


# main code here
init()
while(run == True):
    preview_box()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cam.stop()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cam.stop()
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_KP_MULTIPLY:
                pygame.image.save(img,"/home/pi/meas.jpg")
                checkpassword()
                if password == "yes":
                    calibfeature = ""
                    calibfeature = name(calibfeature)
                    calibrate()
                    preview_box()
                    cam.start()
                    password = "no"
            if event.key == pygame.K_KP_DIVIDE:
                pygame.display.toggle_fullscreen()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2: # wheel button
                pygame.image.save(img,"/home/pi/meas.jpg")
                measuremode()
                cam.start()
    img = cam.get_image()
    img = pygame.transform.scale(img,(mWIDTH,mHEIGHT))
    screen.blit(img,(0,0))
