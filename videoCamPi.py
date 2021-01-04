#! /usr/bin/python
import os, sys, time, pygame, picamera
from picamera import PiCamera
from time import sleep

# define space menu titles are from top of screen
menuTop = 75

# define path to save files to
imgPath = "/mnt/APACHE/videoCamPi/Images/"
videoPath = "/mnt/APACHE/videoCamPi/Videos/"

# define opposite colors
white = (255, 255, 255)
black = (0, 0, 0)

# define primary colors
bright_red = (255, 0, 0)
bright_blue = (0, 0, 255)
bright_green = (0, 255, 0)
red = (200, 0, 0)
blue = (0, 0, 200)
green = (0, 200, 0)

# define secondary colors
bright_cyan = (0,200,200)
bright_magenta = (200,0,200)
bright_yellow = (200,200,0)
cyan = (0,255,255)
magenta = (255,0,255)
yellow = (255,255,0)

# initialize pygame
pygame.init()

# grab size of monitor
infoObject = pygame.display.Info()
display_width = infoObject.current_w
display_height = infoObject.current_h
#mWIDTH = 720 # test different monitor resolutions (size)
#mHEIGHT = 480
print("Monitor width: %s" % display_width)
print("Monitor height: %s" % display_height)
print('')
print('')


#initialize pycamera
camera = PiCamera()
camera.resolution = (display_width,display_height)

# initialize pygame screen and clock
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('videoCamPi')
clock = pygame.time.Clock()


def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()
 
def message_Display(text,color):
    smallText = pygame.font.SysFont("comicsansms",50)
    TextSurf, TextRect = text_objects(text, smallText, color)
    TextRect.center = ((display_width/2),(display_height/2))
    gameDisplay.blit(TextSurf, TextRect)
 
    pygame.display.update()
 
    time.sleep(1)

def game_intro():
    # start camera
    camera.start_preview(alpha=200)

    intro = True

    while intro:
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        gameDisplay.fill(black)
        largeText = pygame.font.Font('freesansbold.ttf',115)
        TextSurf, TextRect = text_objects("videoCamPi", largeText, white)
        TextRect.center = ((display_width/2),menuTop)
        gameDisplay.blit(TextSurf, TextRect)

        bSizeX = 200
        bSizeY = 100
        bSpace = 50

        b1X = (display_width/8)*1 - bSizeX
        b2X = b1X + bSizeX + bSpace
        b3X = b2X + bSizeX + bSpace
        b4X = b3X + bSizeX + bSpace
        b5X = (display_width/8)*7

        b1Y = (display_height/8)*7 - bSpace
        b2Y = (display_height/8)*7 - bSpace
        b3Y = (display_height/8)*7 - bSpace
        b4Y = (display_height/8)*7 - bSpace
        b5Y = (display_height/8)*7 - bSpace
        
        button("Img",b1X,b1Y,bSizeX,bSizeY,cyan,bright_cyan,savePic)
        button("Rec",b2X,b2Y,bSizeX,bSizeY,green,bright_green,recordVideo)
        button("Stop",b3X,b3Y,bSizeX,bSizeY,magenta,bright_magenta,stopRecordVideo)
        button("Menu",b4X,b4Y,bSizeX,bSizeY,yellow,bright_yellow,openMenu)
        button("Quit",b5X,b5Y,bSizeX,bSizeY,red,bright_red,quitgame)

        pygame.display.update()
        clock.tick(10)
        
def button(msg,x,y,w,h,ic,ac,action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    #print(click)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(gameDisplay, ac,(x,y,w,h))

        if click[0] == 1 and action != None:
            action()         
    else:
        pygame.draw.rect(gameDisplay, ic,(x,y,w,h))

    smallText = pygame.font.SysFont("comicsansms",50)
    textSurf, textRect = text_objects(msg, smallText, black)
    textRect.center = ( (x+(w/2)), (y+(h/2)) )
    gameDisplay.blit(textSurf, textRect)

def openMenu():
    print("openMenu pressed!")
    while True:
        intro = True

        while intro:
            for event in pygame.event.get():
                #print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    
            gameDisplay.fill(black)
            largeText = pygame.font.Font('freesansbold.ttf',115)
            TextSurf, TextRect = text_objects("Menu", largeText, white)
            TextRect.center = ((display_width/2),menuTop)
            gameDisplay.blit(TextSurf, TextRect)

            bSizeX = (display_width/3)
            bSizeY = 100
            bSpace = 50

            b1X = (display_width/2) - (bSizeX/2)
            b2X = (display_width/2) - (bSizeX/2)
            b3X = (display_width/2) - (bSizeX/2)
            b4X = (display_width/2) - (bSizeX/2)

            b1Y = (display_height/8)*2 - bSpace
            b3Y = (display_height/8)*3 - bSpace
            b4Y = (display_height/8)*4 - bSpace
            
            button("Play last saved Video",b1X,b1Y,bSizeX,bSizeY,cyan,bright_cyan,playVideo)
            button("Open last saved Image",b3X,b3Y,bSizeX,bSizeY,magenta,bright_magenta,openImg)
            button("Back",b4X,b4Y,bSizeX,bSizeY,red,bright_red,game_intro)

            pygame.display.update()
            clock.tick(10)

def play(movie):
    os.system("sudo omxplayer -o hdmi " + movie)

def playVideo():
    print("playVideo pressed!")
    camera.stop_preview()
    i = 0
    while os.path.exists(videoPath + "videoCamPi%s.h264" % i):
        i += 1
        if(os.path.exists(videoPath + "videoCamPi%s.h264" % i)):
            i += 1
        else:
            i -= 1
            break
    fileName = (videoPath + "videoCamPi%s" % i)
    print(fileName + ".h264")
    if os.path.exists(fileName + ".mp4"):
        print(fileName + ".mp4 WAS FOUND!")
    else:
        gameDisplay.fill(black)
        message_Display("Converting File...", white)
        msg = "sudo MP4Box -add " + fileName + ".h264 " + fileName + ".mp4"
        os.system(msg)
    movie = fileName + ".mp4"

    # Check if movie is accessible
    if not os.access(movie, os.R_OK):
        i -= 1
        fileName = (videoPath + "videoCamPi%s" % i)
        print(fileName + ".h264")
        if os.path.exists(fileName + ".mp4"):
            print(fileName + ".mp4 WAS FOUND!")
        else:
            gameDisplay.fill(black)
            message_Display("Converting File...", white)
            msg = "sudo MP4Box -add " + fileName + ".h264 " + fileName + ".mp4"
            os.system(msg)
        movie = fileName + ".mp4"
    # show some text
    gameDisplay.fill(black)
    message_Display("Opening File...", white)
    play(movie)
    # go back to main menu
    game_intro()

def showImg(fileName):
    img = pygame.image.load(fileName)
    x = 0
    y = 0
    
    while True:
        intro = True

        while intro:
            for event in pygame.event.get():
                #print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                    
            gameDisplay.fill(black)

            bSizeX = 200
            bSizeY = 100

            b4X = ((display_width/16)*14) - (bSizeX/2)

            b4Y = ((display_height/16)*13)
            # Show image
            gameDisplay.blit(img,(x,y))
            # Show back button
            button("Back",b4X,b4Y,bSizeX,bSizeY,red,bright_red,openMenu)

            pygame.display.update()
            clock.tick(10)

def openImg():
    print("openImg pressed!")
    camera.stop_preview()
    i = 0
    while os.path.exists(imgPath + "videoCamPi%s.jpg" % i):
        i += 1
        if(os.path.exists(imgPath + "videoCamPi%s.jpg" % i)):
            i += 1
            if(os.path.exists(imgPath + "videoCamPi%s.jpg" % i)):
                i += 1
            else:
                i -= 1
                break
        else:
            i -= 1
            break
    fileName = imgPath + "videoCamPi%s" % i
    print(fileName + ".jpg")
    # show some text
    gameDisplay.fill(black)
    message_Display("Opening File...", white)
    try:
        showImg(fileName + ".jpg")
    except:
        i -= 1
        fileName = (imgPath + "videoCamPi%s.jpg" % i)
        showImg(fileName)
    # go back to main menu
    game_intro()


def savePic():
    print("savePic pressed!")
    i = 0
    while os.path.exists(imgPath + "videoCamPi%s.jpg" % i):
        i += 1
    camera.capture(imgPath + "videoCamPi%s.jpg" % i)

def recordVideo():
    print("recordVideo pressed!")
    i = 0
    while os.path.exists(videoPath + "videoCamPi%s.h264" % i):
        i += 1
    camera.start_recording(videoPath + "videoCamPi%s.h264" % i)
    while True:
        intro = True

        while intro:
            for event in pygame.event.get():
                #print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            gameDisplay.fill(black)
            smallText = pygame.font.SysFont("comicsansms",50)
            TextSurf, TextRect = text_objects("Recording in progress...", smallText, white)
            TextRect.center = ((display_width/16)*2,(display_width/16)*1)
            gameDisplay.blit(TextSurf, TextRect)
                    
            bSizeX = 200
            bSizeY = 100
            bSpace = 50

            b1X = (display_width/8)*1 - bSizeX
            b2X = b1X + bSizeX + bSpace
            b3X = b2X + bSizeX + bSpace
            b4X = (display_width/8)*7

            b1Y = (display_height/8)*7 - bSpace
            b3Y = (display_height/8)*7 - bSpace
            b4Y = (display_height/8)*7 - bSpace
            
            button("Img",b1X,b1Y,bSizeX,bSizeY,cyan,bright_cyan,savePic)
            button("Stop",b3X,b3Y,bSizeX,bSizeY,magenta,bright_magenta,stopRecordVideo)
            button("Quit",b4X,b4Y,bSizeX,bSizeY,red,bright_red,quitgame)

            pygame.display.update()
            clock.tick(10)
            

def stopRecordVideo():
    print("stopRecordVideo pressed!")
    camera.stop_recording()
    camera.stop_preview()
    game_intro()

def quitgame():
    print("quitgame pressed!")
    try:
        camera.stop_preview()
        camera.stop()
        pygame.quit()
        sys.exit()
    except:
        pygame.quit()
        sys.exit()
    
    

# main code here
game_intro()
while(run == True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitgame()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quitgame()
