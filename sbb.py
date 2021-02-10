import numpy as np
from tile import Tile

"""
An SBB has 32x32 = 1024 tiles 
Each tile is 8x8 pixels
We store these tiles as a flat 1D array

"""
class SBB(object):
    def __init__(self, img=None, sbb_size=256):
        self.img = img
        dim = int(sbb_size / 8)
        self.tiles = []
        #self.tiles = np.empty(ntile*ntile, dtype=object).reshape(ntile,ntile)
        self.splitIntoTiles(dim)
        print("The number of tiles in this SBB is " + str(len(self.tiles)))
    
    def splitIntoTiles(self, dim):
        '''Divide this SBB into tiles'''
        for i in range(dim):
            for j in range(dim):
                x0 = i*8
                x1 = x0 + 8
                y0 = j*8
                y1 = y0 + 8
                self.tiles.append(Tile(self.img[x0:x1, y0:y1]))
                #print("")
