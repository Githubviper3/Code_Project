import pygame
import sys
import os
sys.path.append(os.getcwd())
from Extras.MyUtils import Bordered_blit_line,blit_line
from Extras.MyColours import *
from Extras.Buttons import EasyButton,create_buttons
from Extras.Textboxes import Textbox
from Extras.Validation import paswordcheck, Lencheck
from Extras.Sqltest import *
from game import Game


class BasicPage:
    def __init__(self, name, system, returning=False):
        pygame.display.set_caption('Pages')
        self.screen = pygame.display.set_mode((700, 500))
        self.clock = pygame.time.Clock()
        self.System = system
        self.Return = EasyButton("Back", (150, 390), activecol=orange)
        self.Quit = EasyButton("Quit", (450, 390), activecol=red)
        self.Buttons = [self.Quit] if not returning else [self.Quit, self.Return]
        self.name = name
        self.Titlefont = pygame.font.SysFont("Arial", 32)
        self.Title = self.Titlefont.render(self.name, False, (0, 0, 0))
        self.Title_rect = self.Title.get_rect(center=(self.screen.get_width() / 2, 60))
        self.Menu_bar = pygame.Rect(100, 40, 3 * self.screen.get_width() / 4, self.screen.get_height() - 100)
        self.next = ""
        self.returning = returning

    def Returnhandler(self, change=-1):
        if self.Return.isClicked:
            self.System.Changepage(change)

    def Handle_Event(self, event):
        for button in self.Buttons:
            button.handle_events(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    def Quithandler(self):
        if self.Quit.isClicked:
            pygame.quit()
            sys.exit()

    def UpdateDisplay(self):
        self.screen.fill(white)
        self.screen.blit(self.Title, self.Title_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.Menu_bar, 1, 25)
        self.Quithandler()
        for button in self.Buttons:
            button.draw(self.screen)
        self.Returnhandler()

    def run(self):
        while True:
            for event in pygame.event.get():
                self.Handle_Event(event)

            self.UpdateDisplay()
            pygame.display.update()
            self.clock.tick(60)


class LoginPage(BasicPage):
    def __init__(self, system):
        super().__init__(name="Login", system=system, returning=False)
        self.Textboxes = self.Username, self.Password = [Textbox(150, 200, "Username:"),
                                                         Textbox(150, 250, "Password:", private=True)]
        self.Submit = EasyButton("Submit", (200, 390), activecol=green)
        self.Quit.rect.x = self.Submit.rect.x + 100
        self.Buttons.append(self.Submit)

    def SubmitHandler(self):
        if self.Submit.isClicked and not self.Username.alert and not self.Password.alert:
            userUname = self.Username.savetext
            userPword = self.Password.savetext
            plencheck = Lencheck(userPword)
            ulencheck = Lencheck(userUname)
            FindPassword = PasswordFind(userPword)
            FindUsername = UsernameFind(userUname)
            if FindUsername:
                if FindPassword:
                    self.Submit.isClicked = False
                    self.System.Changepage(2)
                else:
                    self.Password.alert = True
                    self.Password.alertmsg = "Incorrect Password"
                    self.Username.alert = True
                    self.Username.alertmsg = "Account name may be taken"
            elif userUname == "" or userPword == "" or plencheck[0] == False or ulencheck[0] == False:
                if userUname == "":
                    self.Username.alert = True
                    self.Username.alertmsg = "Empty"
                elif not ulencheck[0]:
                    self.Username.alert = True
                    self.Username.alertmsg = ulencheck[1]
                if userPword == "":
                    self.Password.alert = True
                    self.Password.alertmsg = "Empty"
                elif not plencheck[0]:
                    self.Password.alert = True
                    self.Password.alertmsg = plencheck[1]
            else:
                self.Submit.isClicked = False
                self.System.Changepage(1)

    def Handle_Event(self, event):
        super().Handle_Event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.Username.active,self.Password.active = self.Password.active,self.Username.active

        for box in self.Textboxes:
            box.handle_event(event)
            box.Reset_button(self.Submit)

    def UpdateDisplay(self):
        super().UpdateDisplay()
        self.SubmitHandler()
        for box in self.Textboxes:
            box.update(self.screen)


class RegisterPage(BasicPage):
    def __init__(self, system):
        super().__init__(name="Register", system=system, returning=True)
        self.Username , self.Password = self.Textboxes = self.System.Login.Textboxes
        self.Confirmbox = Textbox(150, 300, "Confirm:", private=True)
        self.Error = False
        self.ConfirmButton = EasyButton("Confirm", (300, 390), activecol=green)
        self.Buttons.append(self.ConfirmButton)
        self.timegap = 0

    def ConfirmHandler(self):
        if self.ConfirmButton.isClicked:
            userConfirm = self.Confirmbox.savetext
            userUname = self.Username.savetext
            userPword = self.Password.savetext
            self.Error = not paswordcheck(userPword)[0]
            self.Message = paswordcheck(userPword)[1]
            if self.Error:
                self.Password.alert = True
                self.Password.alertmsg = "Invalid Password:"
                self.Confirmbox.alert = True
                self.Confirmbox.alertmsg = "Invalid"
            elif userConfirm != userPword:
                self.Confirmbox.alert = True
                self.Password.alert = True
                self.Password.alertmsg = self.Password.label
                self.Confirmbox.alertmsg = "Passwords do not match"
            elif userConfirm != "" and not self.Confirmbox.alert:
                self.ConfirmButton.isClicked = False
                text = [userUname, userPword]
                NewAccount(text)
                self.ConfirmButton.isClicked = False
                self.System.Changepage(1)

    def Handle_Event(self, event):
        super().Handle_Event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self.Username.active:
                self.Password.active = True
                self.Username.active,self.Confirmbox.active = False,False
            elif self.Password.active:
                self.Confirmbox.active = True
                self.Password.active,self.Username.active = False,False
            elif self.Confirmbox.active:
                self.Username.active = True
                self.Password.active,self.Confirmbox.active = False,False


        for box in self.Textboxes:
            box.handle_event(event)
            box.Reset_button(self.ConfirmButton)

        self.Confirmbox.handle_event(event)
        self.Confirmbox.Reset_button(self.ConfirmButton)

    def UpdateDisplay(self):
        super().UpdateDisplay()
        self.ConfirmHandler()
        for box in self.Textboxes:
            box.update(self.screen)
        self.Confirmbox.update(self.screen)
        if self.Error:
            blit_line(self.screen, self.Message,
                      (self.Password.rect.x + self.Password.rect.width + 16, self.Password.rect.y),
                      self.Confirmbox.FONT)
            self.timegap += 1
            if self.timegap== 180:
                self.timegap = 0
                self.Error = False


class Gamemenu(BasicPage):
    def __init__(self, system):
        super().__init__(name="Game Menu", system=system, returning=True)
        self.Return.name = "Log Out"
        self.Start = EasyButton("Start", (350, 150), activecol=green)
        self.Leaderboards = EasyButton("Leaderboards", (350, 210))
        self.Shop = EasyButton("Shop", (350, 270))
        self.Settings = EasyButton("Settings", (350, 330))
        self.Buttons.extend([self.Start, self.Leaderboards, self.Shop, self.Settings])
        self.Quit.pos.x = 350

    def Returnhandler(self):
        if self.Return.isClicked:
            self.System.Register.Confirmbox.savetext,self.System.Register.Confirmbox.showtext = "",""
            self.System.Login.Username.showtext,self.System.Login.Password.showtext = "",""
            self.System.Login.Username.savetext,self.System.Login.Password.savetext = "",""
            self.System.Changepage(-2)


    def ButtonHandler(self):
        if self.Start.isClicked:
            self.System.Changepage(1)
        if self.Leaderboards.isClicked:
            self.DB_Data = getScores()
            self.System.Changepage(2)
        if self.Shop.isClicked:
            self.System.Changepage(3)
        if self.Settings.isClicked:
            self.System.Changepage(4)


    def UpdateDisplay(self):
        super().UpdateDisplay()
        self.Playername = self.System.Login.Username.savetext
        pagefont = pygame.font.SysFont("Arial",15,bold=True)
        blit_line(self.screen,[f"User: {self.Playername}"],(110,70),color=black,font=pagefont)
        self.ButtonHandler()


class Start(BasicPage):
    def __init__(self, system):
        super().__init__(name="Levels", system=system, returning=True)
        self.new = create_buttons()
        self.Buttons.extend(self.new)


    def Returnhandler(self):
        super().Returnhandler(-1)

    def CLicked(self):
        for button in self.new:
            if button.isClicked:
                os.environ['SDL_VIDEO_CENTERED'] = "1"
                self.System.Game.level = int(button.name[-1])
                self.System.Game.PlayerSpawners = False
                self.screen = pygame.display.set_mode((640,360))
                self.System.Game.run()

    def UpdateDisplay(self):
        super().UpdateDisplay()
        self.Playername = self.System.Login.Username.savetext
        pagefont = pygame.font.SysFont("Arial", 15, bold=True)
        blit_line(self.screen, [f"User: {self.Playername}"], (110, 70), color=black, font=pagefont)
        self.CLicked()

class LeaderBoards(BasicPage):
    def __init__(self,system):
        super().__init__(name="LeaderBoards", system=system, returning=True)
        self.Title_rect.x -= 90
        self.Menu_bar.x -= 90
        self.Quit.pos.x = 470
        self.Return.pos.x = 60
        self.L_HSc =EasyButton("Highest Score", (280, 190), toggle=True)
        self.O_HSc =EasyButton("Highest Score", (90, 290), toggle=True)
        self.O_Coins =EasyButton("Most Coins", (210, 290), toggle=True)
        self.O_Gems =EasyButton("Most Gems", (325, 290), toggle=True)
        self.Deaths =EasyButton("Least Deaths", (450, 290), toggle=True)
        self.clicked = [self.L_HSc, self.Deaths, self.O_HSc, self.O_Coins, self.O_Gems]
        self.Buttons.extend(self.clicked)



    def UpdateDisplay(self):
        super().UpdateDisplay()
        blit_line(self.screen, ["Per Level:"], (60, 140), pygame.font.Font(None, 30),
                  color=black)
        blit_line(self.screen, ["Overall:"], (60, 240), pygame.font.Font(None, 30),
                  color=black)
        self.Playername = self.System.Login.Username.savetext
        pagefont = pygame.font.SysFont("Arial", 15, bold=True)
        blit_line(self.screen, [f"User: {self.Playername}"], (20, 70), color=black, font=pagefont)


        for button in self.clicked:
            if button.isClicked:
                data = button.name

                font = pygame.font.Font(None,25)

                text = font.render(data,True, black)
                Newtextrect = text.get_rect(topleft=(545,50))
                Menu_bar = pygame.Rect(540,40,155, self.screen.get_height() - 100)
                pos = (545, 75)
                font2 = pygame.font.SysFont("Arial", 20)

                if data == "Highest Score":
                    condition = button.pos.y == 190
                    db_data = self.System.Gamemnenu.DB_Data[condition]
                    if not condition:
                        db_data = [db_data]
                    blit_line(self.screen, db_data, pos, font2, color=black)
                else:
                    lastpoint = data.index("t") + 2
                    word  = data[lastpoint:]
                    if word == "Deaths":
                        sortorder = "Asc"
                    else:
                        sortorder = "Desc"
                    db_data = Top5("Users","id",word,sortorder)

                    font2 = pygame.font.SysFont("Arial", 13)
                    blit_line(self.screen, db_data, pos, font2, color=black)

                pygame.draw.rect(self.screen, (0, 0, 0), Menu_bar, 1, 25)
                self.screen.blit(text,Newtextrect)

    def Returnhandler(self):
        super().Returnhandler(-2)

class Shop(BasicPage):
    def __init__(self, system):
        super().__init__(name="Shop", system=system, returning=True)
        self.Confirm = EasyButton("Confirm",(550,390),activecol=green)
        self.Buttons.append(self.Confirm)

    def UpdateDisplay(self):
        self.Playername = self.System.Login.Username.savetext
        super().UpdateDisplay()
        userid  = GetFromUsername(self.Playername,"id")[0]
        usercoins = Get_from_id(userid,"Coins")
        usergems = Get_from_id(userid,"Gems")
        Bordered_blit_line(self.screen, [f"Coins: {usercoins}"], (150, 120),color=black,size=(50,0))
        Bordered_blit_line(self.screen, [f"Gems: {usergems}"], (400, 120),color=black,size=(50,0))
        pagefont = pygame.font.SysFont("Arial", 15, bold=True)
        blit_line(self.screen, [f"User: {self.Playername}"], (110, 70), color=black, font=pagefont)
        blit_line(self.screen, ["Upgrades          Items        Abilities"], (150, 150), color=black)

    def Returnhandler(self):
        super().Returnhandler(-3)

class Settings(BasicPage):
    def __init__(self, system):
        super().__init__(name="Settings", system=system, returning=True)
        self.Title_rect.x -= 90
        self.Menu_bar.x -= 90
        self.Quit.pos.x = 470
        self.Return.pos.x = 60
        self.ScSize = EasyButton("Screen Size", (140, 190), toggle=True)
        self.Volume = EasyButton("Volume", (280, 190), toggle=True)
        self.Controls = EasyButton("Controls", (420, 190), toggle=True)
        self.UChange = EasyButton("Change Username", (150, 290), toggle=True)
        self.PChange = EasyButton("Change Password", (390, 290), toggle=True)
        self.Buttons.extend([self.ScSize,self.Volume ,self.Controls ,self.UChange ,self.PChange])

    def UpdateDisplay(self):
        super().UpdateDisplay()
        self.Playername = self.System.Login.Username.savetext
        pagefont = pygame.font.SysFont("Arial", 15, bold=True)
        blit_line(self.screen, [f"User: {self.Playername}"], (20, 70), color=black, font=pagefont)
        blit_line(self.screen, ["Game"], (60, 140),color=black)
        blit_line(self.screen, ["Profile"], (60, 240),color=black)



    def Returnhandler(self):
        super().Returnhandler(-4)


class PagesSystem:
    def __init__(self):
        self.Login = LoginPage(self)
        self.Register = RegisterPage(self)
        self.Gamemnenu = Gamemenu(self)
        self.Start = Start(self)
        self.Leaderboards = LeaderBoards(self)
        self.Shop = Shop(self)
        self.Settings = Settings(self)
        self.Pages = [self.Login, self.Register, self.Gamemnenu, self.Start, self.Leaderboards, self.Shop,
                      self.Settings]
        self.Game = Game(self)
        self.Pageindex = 3
        self.Current_Page = self.Pages[self.Pageindex]

    def Changepage(self, increase):
        for button in self.Current_Page.Buttons:
            if not button.toggle:
                button.isClicked = False
        self.Pageindex += increase
        self.Pageindex %= len(self.Pages)
        self.Current_Page = self.Pages[self.Pageindex]
        for button in self.Current_Page.Buttons:
            if not button.toggle:
                button.isClicked = False
        self.run()

    def run(self):
        self.Current_Page.run()



PagesSystem().run()
