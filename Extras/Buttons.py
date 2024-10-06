import pygame
from  Extras.MyColours import *

class EasyButton:
    def __init__(self,text,pos,width= 85, height=50,border =2,bordercolor=black, activecol=cyan, passivecol=lightgray,text_color=black,toggle = False):
        x,y = pos
        self.pos = pygame.math.Vector2(pos)
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.rect.center = x, y
        self.name = text
        self.color = bordercolor
        self.defaultcolor = text_color
        self.text_color = self.defaultcolor
        self.active = False
        self.activecol = activecol
        self.passivecol = passivecol
        self.colors = self.passivecol,self.activecol
        self.border = border
        self.isClicked = False
        self.drawn = False
        self.toggle = toggle
        self.sorted = False

    def colorcheck(self):
        if not self.toggle:
            if self.activecol in [red, green, orange]:
                self.text_color = white if self.active else self.defaultcolor
            return self.colors[self.active]
        else:
            return self.passivecol

    def draw(self, screen):
        self.drawn = True
        if self.border == 0:
            pygame.draw.rect(screen, self.colorcheck(), self.rect, 0, 10)
        else:
            pygame.draw.rect(screen, self.colorcheck(), self.rect, 0, 10)
        pygame.draw.rect(screen, self.color, self.rect, self.border, 10)

        font = pygame.font.Font(None, 25)
        text = font.render(self.name, False, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        if not self.sorted:
            textwidth = text_rect.width
            newwidth = textwidth + 10 if textwidth > self.width else self.width
            self.rect.width = newwidth
            self.rect.center = self.pos
            self.sorted = True

        screen.blit(text, text_rect)



    def handle_events(self, player_action):
        if self.drawn:
            if player_action.type == pygame.MOUSEMOTION:
                if self.rect.collidepoint(player_action.pos):
                    self.active = True
                else:
                    self.active = False
            if player_action.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(player_action.pos):
                if self.toggle:
                    self.isClicked = not self.isClicked
                    self.activecol,self.passivecol = self.passivecol,self.activecol
                else:
                    self.isClicked = True

def create_buttons():
    Buttonset = []
    button_width, button_height = 75, 60
    margin = 20
    start_x, start_y =180, 150
    for i in range(15):
        x = start_x + (button_width + margin) * (i % 5)
        y = start_y + (button_height + margin) * (i // 5)
        button = EasyButton(f"Level {i+1}",(x,y),75,60)
        Buttonset.append(button)
    return Buttonset