#!/bin/python
import pygame, sys, pygame.camera
from pygame.locals import *

pygame.init()
pygame.camera.init()

#screen = pygame.display.set_mode((640,480),0)
screen = pygame.display.set_mode((640,480),pygame.FULLSCREEN)

cam_list = pygame.camera.list_cameras()
webcam = pygame.camera.Camera(cam_list[0],(32,24))
webcam.start()
img = pygame.webcam.getImage() #grab image

while True:
        imagen = webcam.get_image()
        imagen = pygame.transform.scale(imagen,(640,480))
        screen.blit(imagen,(0,0))
        pygame.display.update()

        for event in pygame.event.get():
                if event.type == KEYDOWN:
			if event.key == K_ESCAPE:
				img = pygame.webcam.getImage() #grab image
			if event.key == K_ESCAPE:
				screen.img.show() #show image
			if event.key == K_ESCAPE:
				pygame.display.quit()
	                        pygame.quit()
	                        sys.exit()
