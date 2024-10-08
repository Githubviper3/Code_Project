import sys
import math
import random

import pygame

from scripts.utils import load_image, load_images, Animation,transparent,imageload,resize
from scripts.entities import Player, Enemy,StaticEnemy
from scripts.tilemap import Tilemap,BackgroundTiles
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
pygame.init()


class Game:
    def __init__(self):

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480),pygame.RESIZABLE)
        self.display = pygame.Surface((320, 240),pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        self.screenshake = 0
        self.clock = pygame.time.Clock()
        self.level = "05"
        self.movement = [False, False]
        self.background = BackgroundTiles(self)
        self.tilemap = Tilemap(self,editor=False)
        self.extra = BackgroundTiles(self)
        self.PlayerSpawners= False
        self.Endlevel = False
        size = self.screen.get_size()[0]/3 , self.screen.get_size()[1]/3


        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            "background_grass": load_images("tiles/Background_grass"),
            "Extra_grass": load_images("tiles/Extra_grass"),
            "Ramps_dirt": load_images("tiles/Ramps_dirt"),
            "Ramps_grass": load_images("tiles/Ramps_grass"),
            "Extra": load_images("tiles/Extra"),
            "Arrows_D": load_images("tiles/Arrows_diagonal"),
            "Arrows_S": load_images("tiles/Arrows_straight"),
            "BG_grass": load_images("tiles/Background_grass"),
            "Flag": [imageload("Flag"),imageload("Flag2")],
            "LevelClear": [resize(imageload("Level_Clear"),size[0],size[1])]
        }

        self.sfx = {
            "jump": pygame.mixer.Sound("data/sfx/jump.wav"),
            "dash": pygame.mixer.Sound("data/sfx/dash.wav"),
            "hit": pygame.mixer.Sound("data/sfx/hit.wav"),
            "shoot": pygame.mixer.Sound("data/sfx/shoot.wav"),
            "ambience": pygame.mixer.Sound("data/sfx/ambience.wav"),
        }

        self.sfx["ambience"].set_volume(0.2)
        self.sfx["shoot"].set_volume(0.4)
        self.sfx["hit"].set_volume(0.8)
        self.sfx["dash"].set_volume(0.3)

        self.sfx["jump"].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50, 50), (8, 15))



    def load_level(self, map_id):
        path2 = f"Maps/016.json"
        self.tilemap.load(path2)
        self.extra.alpha = 255
        self.extra.load(base="ExtraMaps/",path=str(map_id))
        self.background.load(path=str(map_id))
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                if not self.PlayerSpawners:
                    self.player.pos = spawner['pos']
                    self.player.air_time = 0
                else:
                    self.player.pos = self.PlayerSpawners
                    self.player.air_time = 0

            elif spawner["variant"] == 1:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            else:
                self.enemies.append(StaticEnemy(self, spawner['pos'], (8, 15)))




        self.projectiles = []
        self.particles = []
        self.sparks = []
        self.transition = -30
        self.scroll = [0, 0]
        self.dead = 0

        
    def run(self):
        self.load_level(self.level)
        pygame.mixer.music.load("data/music.wav")
        pygame.mixer.music.set_volume(0.5)
        #pygame.mixer.music.play(-1)
        #self.sfx["ambience"].play(-1)

        while True:
            self.display.fill(transparent)
            self.display_2.blit(self.assets['background'], (0, 0))
            self.screenshake = max(0,self.screenshake -1)
            #if not len(self.enemies):
             #   self.transition += 1
              #  if self.transition > 30:
               #     self.load_level(self.level)
            if self.transition <0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead > 40:
                    self.load_level(self.level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            self.background.render(self.display, offset=render_scroll)
            self.extra.render(self.display,offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)




            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx["shoot"].play()
                        self.screenshake = max(16,self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)
            if self.Endlevel:
                self.display.blit(self.assets["LevelClear"][0],(0,0))
            display_mask= pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,180),unsetcolor=transparent)
            for offset in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                self.display_2.blit(display_sillhouette, offset)
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_DOWN and not self.tilemap.solid_check((self.player.rect().centerx + (-7 if self.player.flip else 7), self.player.pos[1] + 23)):
                        self.player.drop()
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx["jump"].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255),
                                   (self.display.get_width() // 2, self.display.get_height() // 2),
                                   (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf,(0,0))


            self.display_2.blit(self.display,(0,0))
            screenshake_offset = (random.random() *  self.screenshake- self.screenshake/2,random.random() *  self.screenshake- self.screenshake/2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

Game().run()