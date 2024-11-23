import json
import os
import pygame

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

baseMapPath = "Main_Folder/Maps/"
baseBGPath = "Main_Folder/BgMaps/"
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

PHYSICS_TILES = {'grass', 'stone'}
RAMP_TILES = {"Ramps_dirt","Ramps_grass"}
AUTOTILE_TYPES = {'grass', 'stone'}
BgTile = {"BG_grass","stone"}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        self.alpha = 255


    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def save(self, base=baseMapPath):
        self.savedlevelssize = str(len(os.listdir(baseMapPath)) + 1)
        filename= base + self.savedlevelssize + ".json"
        f = open(filename, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path,base=baseMapPath):
        filename = base + str(path) + ".json"
        f = open(filename, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]

    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects

    def ramps_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in RAMP_TILES:
                rects.append([pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size),tile["variant"]])
        return rects


    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):

        for tile in self.offgrid_tiles:
            img = self.game.assets[tile['type']][tile['variant']]

            img.set_alpha(self.alpha)
            surf.blit(img,
                    (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]


                    img = self.game.assets[tile['type']][tile['variant']]
                    img.set_alpha(self.alpha)

                    surf.blit(img, (
                        tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

class BackgroundTiles:
    def __init__(self, game, tile_size=16,editor= True):
        self.game = game
        self.tile_size = tile_size
        self.alpha = 180
        self.tilemap = {}
        self.offgrid_tiles = []
        self.editor = editor


    def save(self,base=baseBGPath):
        self.savedlevelssize = str(len(os.listdir(base))+1)
        filename = base + self.savedlevelssize + ".json"
        f = open(filename, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    def load(self, path, base=baseBGPath):
        filename = base + str(path) + ".json"
        f = open(filename, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

        if not self.editor:
            level = list(self.game.tilemap.tilemap)
            for loc in self.tilemap.copy():
                if loc in level:
                    tile = self.tilemap[loc]
                    if tile["type"] in ["stone","grass","Extra_grass","Extra"]:
                        del tile


    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in BgTile) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            img =self.game.assets[tile['type']][tile['variant']]
            img.set_alpha(self.alpha)

            surf.blit(img,
                      (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    img = self.game.assets[tile['type']][tile['variant']]
                    
                    img.set_alpha(self.alpha)
                    surf.blit(img, (
                        tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap.copy():
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles

    def Flag_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] == "Flag":
                rects.append((pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size),tile["variant"]))
        return rects

class Editor_layers:
    def __init__(self,background,level,extra):
        self.layers = [level,background,extra]
        self.stages = ["level","BG","Extras"]
        self.currentlayer = level
        self.previouslayer = extra
        self.background = background
        self.level = level
        self.extra = extra
        self.bg = False
        self.stage = "level"
        self.nextlayer = 0


    def updateLayer(self):
        self.nextlayer = self.layers.index(self.currentlayer) + 1
        self.nextlayer %= len(self.layers)
        self.currentlayer = self.layers[self.nextlayer]
        self.stage = self.stages[self.nextlayer]
        layerlevels = [180,100]
        for count,layer in enumerate(self.layers):
            if layer != self.currentlayer:
                layer.alpha= layerlevels[count%2]
            else:
                layer.alpha = 255





    def render(self,screen,offset):
        self.background.render(screen, offset)
        self.extra.alpha = 255
        self.extra.render(screen, offset)
        self.level.render(screen, offset)


    def save(self):
        self.level.save()
        self.extra.save(base="Main_Folder/ExtraMaps/")
        self.background.save()


