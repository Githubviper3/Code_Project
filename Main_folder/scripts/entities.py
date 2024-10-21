import math
import random
import pygame
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.utils import xflip

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.onground = True
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        if not (self.game.Paused or self.game.Endlevel) :
            self.onground = tilemap.solid_check((self.rect().x, self.pos[1] + 23))
            self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

            frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

            self.pos[0] += frame_movement[0]
            entity_rect = self.rect()
            for rect in tilemap.physics_rects_around(self.pos):
                if entity_rect.colliderect(rect):
                    if frame_movement[0] > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True
                    if frame_movement[0] < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = True
                    self.pos[0] = entity_rect.x





            self.pos[1] += frame_movement[1]
            entity_rect = self.rect()
            for rect in tilemap.physics_rects_around(self.pos):
                if entity_rect.colliderect(rect):
                    if frame_movement[1] > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                    if frame_movement[1] < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                    self.pos[1] = entity_rect.y




            if movement[0] > 0:
                self.flip = False
            if movement[0] < 0:
                self.flip = True

            self.last_movement = movement

            self.velocity[1] = min(5, self.velocity[1] + 0.1)




            if self.collisions['down'] or self.collisions['up']:
                self.velocity[1] = 0

            self.animation.update()

    def render(self, surf, offset=(0, 0)):
        surf.blit(xflip(self.animation.img(), self.flip), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if not self.game.Paused:
            if self.walking:
                if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                    if (self.collisions['right'] or self.collisions['left']):
                        self.flip = not self.flip
                    else:
                        movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
                else:
                    self.flip = not self.flip

                self.walking = max(0, self.walking - 1)
                if not self.walking:
                    dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                    if (abs(dis[1]) < 16):
                        if (self.flip and dis[0] < 0):
                            self.game.sfx["shoot"].play()
                            self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                            for i in range(4):
                                self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                        if (not self.flip and dis[0] > 0):
                            self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                            for i in range(4):
                                self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
            elif random.random() < 0.01:
                self.walking = random.randint(30, 120)


        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if abs(self.game.player.dashing) >= 50 or self.game.player.droping:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.player.score += 50
                self.game.sfx["hit"].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2
        self.wall_slide = False
        self.dashing = 0
        self.droping = 0
        self.score,self.Coins , self.Gems = 0,0,0



    def update(self, tilemap, extra,  movement=(0, 0)):
        super().update(tilemap, movement=movement)

        if not (self.game.Paused or self.game.Endlevel):
            self.air_time += 1
        if self.wall_slide:
            self.jumps =1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2
            self.droping = 0
        if self.air_time >= 180:
            self.game.dead += 1
        if self.droping:
            self.jumps = 0
        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions["right"]:
                self.flip = False
            else:
                self.flip = True

            self.set_action("wall_slide")




        tilesize  = tilemap.tile_size
        entity_rect = self.rect()
        for rect, variant in tilemap.ramps_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                relx = entity_rect.x - rect.x
                if variant in [0, 2]:
                    posheight = relx + entity_rect.width if variant == 0 else tilesize - relx
                    targety = rect.y + tilesize - posheight
                    if entity_rect.bottom > targety:
                        entity_rect.bottom = targety
                        self.pos[1] = entity_rect.y
                        self.collisions["down"] = True
                        self.onground = True
                        self.air_time = 0  # Reset air_time when colliding with ground
                        self.jumps =2
                elif variant in [1, 3]:
                    posheight = tilesize + relx - 9 if variant == 1 else tilesize - relx
                    targety = rect.y + tilesize + posheight
                    if entity_rect.bottom < targety:
                        entity_rect.bottom = targety
                        self.pos[1] = entity_rect.y
                        self.collisions["top"] = True
                        self.velocity[1] = 0.5

        entity_rect =self.rect()
        for rect,variant in extra.Flag_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if variant == 0:
                    self.game.PlayerSpawners = [rect.x, rect.y]
                else:
                    self.game.Endlevel = rect.topleft

        Keys = pygame.key.get_pressed()
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        # dashing
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * .5 + .5
                pvelocity = [(math.cos(angle)) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, "particle", (self.rect().centerx, self.rect().centery - 3), pvelocity,
                             frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(
                Particle(self.game, "particle", (self.rect().centerx, self.rect().centery - 3), pvelocity,
                         frame=random.randint(0, 7)))

        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

        if self.droping > 0:
            self.droping = max(0, self.droping - 1)

        if self.droping > 50 and not self.collisions["down"]:
            self.velocity[1] = self.droping / self.droping * 8
            if abs(self.droping) == 51:
                self.velocity[1] *= 0.1
            pvelocity = [0, abs(self.droping) / self.droping * random.random() * 3]
            self.game.particles.append(
                Particle(self.game, "particle", (self.rect().centerx, self.rect().centery - 3), pvelocity,
                         frame=random.randint(0, 7)))


    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)


    def jump(self):
    
        if self.jumps ==1 and not self.wall_slide:
            for i in range(7):
                self.game.particles.append(
                    Particle(self.game, "particle", (self.rect().centerx, self.rect().centery - 3), (0,random.random()*2),
                            frame=i))
        
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        
    def drop(self):
        if not self.droping and not self.onground:
            self.game.sfx["dash"].play()
            self.droping = 70

    def dash(self):
        if not self.dashing:
            self.game.sfx["dash"].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
