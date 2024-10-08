import os

import pygame

BASE_IMG_PATH = 'Main_Folder/data/images/'
transparent = (0,0,0,0)
lightgray = (90,90,90)
black   = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
gray = (60,60,60)
lightblue = (173, 216, 230)
white = (255,255,255)
cyan = (140, 191, 200)


def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def imageload(image):
   if ".png" not in image:
       img = pygame.image.load(f"{BASE_IMG_PATH+image}.png").convert()
       img.set_colorkey((0,0,0))
       return img
   else:
       img = pygame.image.load(f"{BASE_IMG_PATH + image}").convert()
       img.set_colorkey((0, 0, 0))
       return img

def blit_line(surface, words, pos, size , color='red'):
   x, y = pos
   font = pygame.font.Font(None,size)
   for line in words:
       line_surface = font.render(line, 0, color)
       word_height = line_surface.get_height()
       surface.blit(line_surface, (x, y))
       x = pos[0]  # Reset the x.
       y += word_height  # Start on new row.


def xflip(image, xbool=True):
    return pygame.transform.flip(image, xbool, False)


def resize(image,width,height):
   return pygame.transform.scale(image,(width,height))

def load_images(path):
    images = []
    for img_name in (os.listdir(BASE_IMG_PATH + path)):
        if img_name.endswith(".png"):
            images.append(imageload(path + '/' + img_name))
    return images


class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]