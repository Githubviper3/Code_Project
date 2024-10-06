import string

import pygame

from Extras.MyColours import black as active, lightgray as passive, red as alertcolor
pygame.init()

class Textbox:
    def __init__(self, xpos, ypos,label, width=220, height =20,private= False):
        self.rect = pygame.Rect(xpos, ypos, width, height)
        self.active = False
        self.colors = [passive,active]
        self.color = self.colors[self.active]
        self.width = width
        self.showtext = ""
        self.savetext = ""
        self.FONT = pygame.font.Font(None, 20)
        self.PasswordFont = pygame.font.Font(None, 32)
        self.txt_surface = self.FONT.render(self.showtext, True, self.color)
        self.border = 2
        self.private = private
        self.label = label
        self.label_surface = self.FONT.render(self.label, True, "#000000")
        self.alert = False
        self.alertmsg = ""




    def AlterBorder(self):
        #color
        if self.alert:
            self.color = alertcolor
        else:
            self.color = self.colors[self.active]

        #border thickness
        if self.active:
            self.border = 4
        else:
            self.border = 1


    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = passive if self.active else active
        if event.type == pygame.KEYDOWN:
            if self.active:
                acceptable = string.punctuation + string.digits + string.ascii_letters
                acceptable = list(acceptable)
                if event.key == pygame.K_ESCAPE:
                    self.active = False
                elif event.key == pygame.K_BACKSPACE and event.mod & pygame.KMOD_CTRL:
                    self.savetext = ''
                    self.showtext = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.showtext = self.showtext[:-1]
                    self.savetext = self.showtext[:-1]
                elif event.unicode in acceptable:
                    self.changetext(event.unicode)
                self.txt_surface = self.FONT.render(self.showtext, True, self.color)

        if len(self.showtext) > 28:
            self.showtext = self.showtext[:-1]
            self.savetext = self.savetext[:-1]

    def update(self,screen):
        self.AlterBorder()
        self.rect.w = max(self.width, self.txt_surface.get_width() + 10)
        if self.alert:
            self.label_surface = self.FONT.render(self.alertmsg, True, alertcolor)
        else:
            self.label_surface = self.FONT.render(self.label, True, active)
        screen.blit(self.label_surface, (self.rect.x, self.rect.y - 15))

        if self.private:
            self.txt_surface = self.PasswordFont.render(self.showtext, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y+5))
        else:
            self.txt_surface = self.FONT.render(self.showtext, True, self.color)
            screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 3))

        pygame.draw.rect(screen, self.color, self.rect, self.border)





    def changetext(self,letter):
        if self.private:
            self.showtext += "*"
        else:
            self.showtext += letter
        self.savetext += letter


    def Reset_button(self, button):
        if self.active:
            button.isClicked = False
            self.alert = False

