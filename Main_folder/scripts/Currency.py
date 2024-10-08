import pygame


class Currency:
    def __init__(self, game, c_type, pos):
        self.game = game
        self.type = c_type
        self.pos = list(pos)
        self.animation = self.game.assets[self.type].copy()
        self.kill = False
        self.rect = self.animation.img().get_rect()

    def update(self):
        self.animation.update()


    def render(self, surf, offset=(0, 0)):
        self.update()
        img = self.animation.img()
        position = self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2
        self.rect = self.animation.img().get_rect()
        self.rect.topleft = position
        pos = self.game.player.pos
        pos = pos[0] - offset[0],pos[1] - offset[1]
        playerrect = pygame.Rect(pos,(8,15))
        if playerrect.colliderect(self.rect):
            self.kill = True
            if self.type == "Coin":
                self.game.player.Coins += 1
                self.game.player.score += 15
            else:
                self.game.player.Gems += 1
                self.game.player.score += 20

        surf.blit(img,(position))
