import pygame


pygame.init()
def resize(image,width,height):
   return pygame.transform.scale(image,(width,height))


def xflip(image,xbool=True):
   return pygame.transform.flip(image,xbool,False)

def imageload(image):
   if ".png" not in image:
       return pygame.image.load(f"{image}.png").convert()
   else:
       return pygame.image.load(f"{image}").convert()




def blit_line(surface, words, pos, font=pygame.font.Font(None, 30), color=pygame.Color('red')):
   x, y = pos
   for line in words:
       line = str(line)
       line_surface = font.render(line, 0, color)
       word_height = line_surface.get_height()
       surface.blit(line_surface, (x, y))
       x = pos[0]  # Reset the x.
       y += word_height  # Start on new row.


def Bordered_blit_line(surface, words, pos, font=pygame.font.Font(None, 30), color=pygame.Color('red'),size = False):
    x, y = pos
    for line in words:
        line = str(line)
        line_surface = font.render(line, 0, color)
        word_height = line_surface.get_height()
        surface.blit(line_surface, (x, y))
        if size:
            borderrect = pygame.Rect((x-2, y-2),size)
        else:
            borderrect = pygame.Rect(x-2, y-2,line_surface.get_width() + 4,line_surface.get_height() + 4)

        pygame.draw.rect(surface,color,borderrect,2)
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

