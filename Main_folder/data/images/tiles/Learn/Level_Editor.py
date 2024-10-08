import sys

import pygame
from scripts.utils import load_images,lightgray,blit_line,imageload
from scripts.tilemap import Tilemap,BackgroundTiles,Editor_layers

RENDER_SCALE = 2


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()


        self.assets = {
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            "spawners": load_images("tiles/spawners"),
            "Extra_grass": load_images("tiles/Extra_grass"),
            "Ramps_dirt": load_images("tiles/Ramps_dirt"),
            "Ramps_grass": load_images("tiles/Ramps_grass"),
            "Extra": load_images("tiles/Extra"),
            'decor': load_images('tiles/decor'),
            'large_decor': load_images('tiles/large_decor'),
            "Arrows_D": load_images("tiles/Arrows_diagonal"),
            "Arrows_S": load_images("tiles/Arrows_straight"),
            "BG_grass": load_images("tiles/Background_grass"),
             "Flag": [imageload("Flag"),imageload("Flag2")],

        }
        levelassets = ['grass', 'stone', "spawners", "Extra_grass", "Ramps_dirt", "Ramps_grass", "Extra", 'decor',
                            'large_decor',"spawners"]

        bgassets= ["BG_grass",'stone', "spawners", "Extra_grass", "Ramps_dirt", "Ramps_grass", "Extra", 'decor',
                            'large_decor']
        extraassets = ["Arrows_D","Arrows_S","Flag"]
        self.assetslist = [levelassets,bgassets,extraassets]
        self.movement = [False, False, False, False]

        tilemap = Tilemap(self,editor=True)
        Extra = BackgroundTiles(self)
        Background = BackgroundTiles(self)
        self.Layer = Editor_layers(Background,tilemap,Extra)

        self.scroll = [0, 0]


        self.tile_list= []
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True



    def run(self):
        while True:
            self.display.fill(lightgray)


            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))



            self.tile_list = self.assetslist[self.Layer.nextlayer]


            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) //  self.Layer.currentlayer.tile_size),
                        int((mpos[1] + self.scroll[1]) //  self.Layer.currentlayer.tile_size))


            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] *  self.Layer.currentlayer.tile_size - self.scroll[0],
                                                     tile_pos[1] *  self.Layer.currentlayer.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)
            message = str(self.tile_list[self.tile_group])

            if self.clicking and self.ongrid:
                 self.Layer.currentlayer.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {
                    'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}

            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in  self.Layer.currentlayer.tilemap:
                    del  self.Layer.currentlayer.tilemap[tile_loc]

                for tile in  self.Layer.currentlayer.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1],
                                         tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                         self.Layer.currentlayer.offgrid_tiles.remove(tile)

            self.display.blit(current_tile_img, (5, 5))
            self.Layer.render(self.display, offset=render_scroll)
            blit_line(self.display,[self.Layer.stage, message],(30,5),15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                             self.Layer.currentlayer.offgrid_tiles.append(
                                {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant,
                                 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})

                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_e:
                        self.tile_group,self.tile_variant = 0,0
                        self.Layer.updateLayer()
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                         self.Layer.currentlayer.autotile()
                    if event.key == pygame.K_o:
                        self.Layer.save()
                        sys.exit()

                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False


            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
Editor().run()