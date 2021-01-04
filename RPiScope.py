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
    global myfont, myfont1, cam, calibfactor
    myfont = pygame.font.SysFont("Times New Roman", 50)
    myfont1 = pygame.font.SysFont("Times New Roman", 25)
    d = 100
    d = shelve.open('calibration.txt')  # here you will retrieve the cal variable
    calibfactor = d['calibration']
    d.close()

    keys=pygame.key.get_pressed() 

# Define variables
def variables():
    global xres, yres, screen, whichline, x1, x2, x_change, lsl, usl, password, red, black, white, blue
    global yellow,magenta,cyan, linecolor,screen, a, b
    xres, yres = 1920, 1080 # monitor resolution
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
    screen = pygame.display.set_mode((1920,1080))

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
    label = myfont.render("Capturing Image...", 1, (255,255,255))
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
        label = myfont.render("Type Password and press ENTER:", 1, (0,0,0))
        screen.blit(label, (xres*.2, yres*.4))
        label = myfont.render("CALIBRATION MODE", 1, (255,255,0))
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
        block = myfont.render(calibfeature +" mils", True, (0,0,0))
        rect = block.get_rect()
        rect.center = screen.get_rect().center
        screen.blit(block, rect)
        label = myfont.render("Type calibration feature size in inches, and press ENTER:", 1, (0,0,0))
        screen.blit(label, (xres*.2, yres*.4))
        label = myfont.render("CALIBRATION MODE", 1, (255,255,0))
        screen.blit(label, (xres*.2, yres*.1))
        screen.blit(label, (xres*.5, yres*.1))        
        pygame.display.flip()

# adjusts lines to size of feature
def calibrate():
    global x1, whichline, x2, x_change, calibfactor, event, rotated_imagen, rotated_rect
    global linecolor, x, y, click_alpha
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
##        for (xx) in range(50,1900,50):                              #draws a grid
##            pygame.draw.rect(screen,(255,255,0),(xx,10,1,yres*.92))
##        for (yy) in range(50,1080,50):
##            pygame.draw.rect(screen,(255,255,255),(10,yy,xres*.92, 2))
        pygame.draw.rect(screen,red,(x1,10,1,yres*.92))
        pygame.draw.rect(screen,red,(x2,10,1,yres*.92))
        pygame.draw.rect(screen,black,(xres*.13,yres*.86,xres*.75,70))
        label = myfont.render("Cal feature = " + str(calibfeature) + " inches.  Adjust lines and press ENTER", 1, (255,255,0))
        screen.blit(label, (400, 940))
        s.set_alpha(click_alpha)
        screen.blit(s, (x-25,y))
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
                    label = myfont.render("Returning to Live Mode", 1, (0,0,0))
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
                    label = myfont.render("Reducing Edge Detection...", 1, (0,0,0))
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
                    label = myfont.render("Increasing Edge Detection...", 1, (0,0,0))
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
##        for (xx) in range(50,1900,50):                              #draws a grid
##            pygame.draw.rect(screen,(255,255,0),(xx,10,1,yres*.92))
##        for (yy) in range(50,1080,50):
##            pygame.draw.rect(screen,(255,255,255),(10,yy,xres*.92, 2))
        pygame.draw.rect(screen,linecolor,(x1,20,1,yres*.91))
        pygame.draw.rect(screen,linecolor,(x2,20,1,yres*.91))
        pygame.draw.rect(screen,black,(xres*.07,yres*.86,xres*.85,70))
        label = myfont.render(delta + " inches", 1, red)
        screen.blit(label, (xres*.76, yres*.865))
        label = myfont1.render("Measure Mode", 1, red)
        screen.blit(label, (xres*.08, yres*.865))
        label = myfont1.render("(frozen Image)", 1, red)
        screen.blit(label, (xres*.08, yres*.89))
        label = myfont1.render("Press wheel for Live Mode, Left click to position line, Right Click to switch lines, R/L arrows to adjust line", 1, white)
        screen.blit(label, (xres*.17, yres*.865))
        label = myfont1.render("Rotate wheel to rotate image,   +/- to adjust Edge Detection,   ENTER to change color", 1, white)
        screen.blit(label, (xres*.17, yres*.89))
        s.set_alpha(click_alpha)
        screen.blit(s, (x-25,y))
        pygame.display.update()
def preview_box():
    pygame.draw.rect(screen,(255,255,255),(480,200,960,2)) # top
    pygame.draw.rect(screen,(255,255,255),(480,740,960,2)) # bot
    pygame.draw.rect(screen,(255,255,255),(480,200,1,540)) # left
    pygame.draw.rect(screen,(255,255,255),(1440,200,1,540)) # right
    label = myfont.render("Live Mode. Press Wheel for Measure Mode.", 1, (255,255,255))
    screen.blit(label, (xres*.27, yres*.62))
    pygame.display.update()

          
#  start here
variables()
init()
pygame.display.toggle_fullscreen()
preview_box()
cam = picamera.PiCamera(sensor_mode=1)
cam.start_preview(alpha=230)
cam.vflip = False
cam.hflip = False
while True:
    # check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cam.close()
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2: # wheel button
                measuremode()
                preview_box()
                cam.start_preview(alpha=200)
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
            elif event.key == pygame.K_KP_MULTIPLY:
                cam.stop_preview()
                checkpassword()
                if password == "yes":
                    calibfeature = ""
                    calibfeature = name(calibfeature)
                    calibrate()
                    preview_box()
                    cam.start_preview(alpha=200)
                    password = "no"
                else:
                    preview_box()
                    cam.start_preview(alpha=200)
                    
