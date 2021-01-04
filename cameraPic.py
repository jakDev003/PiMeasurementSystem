import cv2, os, sys, time, pygame, shelve, picamera, picamera.array
from pygame.locals import *
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np

# initialize 
def init():
    pygame.init()
    pygame.mouse.set_visible(True)
    global myfont, myfont1, cam, calibfactor, trk
    trk = 1
    myfont = pygame.font.SysFont("Times New Roman", 35)
    myfont1 = pygame.font.SysFont("Times New Roman", 25)
    d = 100
    keys=pygame.key.get_pressed() 

# Define variables
def variables():
    global xres, yres, whichline, x1, x2, x_change, lsl, usl, password, red, black, white, blue
    global yellow,magenta,cyan, linecolor,screen, a, b, path
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
    # screen = pygame.display.set_mode((xres,yres))
    path = "/home/pi/Images/"
    
# shows rectangle and label with directions
def preview_box(val):
    # .rect(screen,color,(x,y,width,height),thickness)    
    if(val==1):
        label = myfont.render("Live Mode. Press '+' to save image.", 1, white)
        screen.blit(label, (700, 950))
    elif(val==2):
        label = myfont.render("Live Mode.", 1, white)
        screen.blit(label, (840, 900))
        label = myfont.render("Press number keys to view img or '+' to save image.", 1, white)
        screen.blit(label, (550, 950))
        label = myfont.render("Press '*' to delete saved images.", 1, white)
        screen.blit(label, (690, 1000))
    elif(val==3):
        label = myfont.render("Please move any images you wish to keep out of the 'IMAGES' folder, or else you will lose them.", 1, white)
        screen.blit(label, (50, 900))
        label = myfont.render("Press 'ENTER' to continue.", 1, white)
        screen.blit(label, (50, 950))
    elif(val==4):
        label = myfont.render("Image Viewer. Press '-' for Live Mode.", 1, white)
        screen.blit(label, (700, 950))
    else:
        label = myfont.render("Oops, this is embarassing. Something went wrong.", 1, white)
        screen.blit(label, (700, 950))

    pygame.display.update()

# shows rectangle and label with directions
def preview_box_img(val):
    font=pygame.font.SysFont("Times New Roman", 50)
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
#starts camera
def startCam():
    global cam
    preview_box(trk)
    cam = picamera.PiCamera(sensor_mode=1)
#    cam.resolution = (2592, 1944)
    cam.start_preview(alpha=230)
    cam.vflip = False
    cam.hflip = False

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

# main loop
def mainLp():
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
                if event.key == pygame.K_KP_MULTIPLY:
                    msgBox("Please remove any images you would like to keep now or they will be deleted\n Press \'Ctrl\' + \'Tab\' to switch between buttons.")
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                else:
                    #clear old label by blacking out screen
                    screen.fill(black)
                    #check for which label to use
                    fnd_img()
                    #show camera preview
                    cam.start_preview(alpha=200)
              
#  start here
global screen
variables()
init()
screen = pygame.display.set_mode()
pygame.display.toggle_fullscreen()
screen.fill(black)
remOld()
#start camera preview
startCam()
#check for which label to use
fnd_img()
#go to main loop
mainLp()

                    
                                                                                                                                                                                                                                                                                                                                                                                                   
