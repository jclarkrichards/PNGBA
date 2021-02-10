import numpy as np
#from color import *
#from bases import *
from copy import deepcopy
import utils
import color

"""                                                                                           
A Tile is 8x8 pixels.  The Input PNG image is in (8,8,3) where the 3 refers to the 3 color channels:   
(B, G, R)                                                                                              
Flatten this image into a 2D hex value array where the colors are in GBA format                        
"""

class Tile(object):
    def __init__(self, data=None):
        self.id = 0  #The index number of this tile among all the tiles
        self.raw = data
        self.gba = color.gbaColors(self.raw)
        self.tdata = np.zeros(64, dtype=int).reshape(8,8)
        self.colors = self.getColors()
        #print("COLORS = " + str(self.colors))
        #print(self.gba)
        self.masks = self.generateColorMasks()
        #print("----MASKS")
        #for mask in self.masks:
        #    print(mask)
        self.pb = 0
        self.hflip = False
        self.vflip = False
        self.tid = 0   #The index number of this tile in the master tile list

        self.othertiles = []  #Matching tiles
        #self.tileids = []  #indices of tiles that match this tile 
        #self.possibleColorDict = {self.colors: [self.id]}
        self.colorsets = []
        self.colorPaletteIndices = []


    def __eq__(self, other):
        if len(self.colors) == len(other.colors):
            return self.matchMasks(other)
        return False

    def getColors(self):
        '''Get the colors that make up this tile'''
        allcolors = list(self.gba.flatten())
        return list(set(allcolors))

    def generateColorMasks(self):
        masks = []
        for c in self.colors:
            mask = np.zeros(8*8, dtype=object).reshape(8, 8)
            for i in range(int(self.gba.shape[0])):
                for j in range(int(self.gba.shape[1])):
                    if self.gba[i, j] == c:
                        mask[i, j] = 1
            masks.append(color.ColorMask(mask, c))
        return masks

    def matchMasks(self, other):
        '''Match all of the color masks in a particular orientation.  Use Masters 0 orientation'''
        """
        print("================MASTER================")
        print(self.colors)
        for mask in self.masks:
            mask.getMaskInfo()

        print("\n================MASTER================")
        print(other.colors)
        for mask in other.masks:
            mask.getMaskInfo()
        """

        for orientation in range(4): #0=noflip, 1=hflip, 2=vflip, 3=hvflip
            matches = [0] * len(self.masks)
            colors = [0] * len(self.colors)
            orientations = [0] * len(self.colors)
            for i, mastermask in enumerate(self.masks):
                for m, othermask in enumerate(other.masks):
                    if matches[m] == 0:
                        if list(mastermask.mask[0]) == list(othermask.mask[orientation]):
                            matches[m] = 1
                            colors[i] = othermask.color
                            orientations[m] = orientation
                            break

            if 0 not in matches:           
                orientation = list(set(orientations))
                if(len(orientation) == 1):
                    other.hflip, other.vflip = self.setOrientation(orientation[0])                 
                    other.colors = colors
                    #if colors not in self.possibleColors:
                    #    self.possibleColors.append(colors)
                    return True
                print("Shouldn't happen right?????")        

        return False

    def setOrientation(self, orientation):
        if orientation == 1:
            return True, False
        elif orientation == 2:
            return False, True
        elif orientation == 3:
            return True, True
        return False, False

    def setTID(self, tid):       
        self.tid = tid
        for tile in self.othertiles:
            tile.tid = tid

    def addTile(self, other):
        self.othertiles.append(other)
        #self.tileids.append(other.id)
        
        #if other.colors in list(self.possibleColorDict.keys()):
        #    self.possibleColorDict[other.colors].append(other.id)
        #else:
        #    self.possibleColorDict[other.colors] = [other.id]

    def setPalette(self, colorset, pb):
        '''Set the palette number for master and any of the children if their colors match the colorset'''
        print(str(self.colors) + " == " + str(colorset))
        if self.colors == colorset:
            print("Master has palette " + str(pb))
            self.pb = pb
        for other in self.othertiles:
            if other.colors == colorset:
                print("Children have palette " + str(pb))
                other.pb = pb
                
    def setUniqueColorLists(self):
        self.colorsets = [self.colors]
        for other in self.othertiles:
            if other.colors not in self.colorsets:
                self.colorsets.append(other.colors)

    def setColorIndices(self, colorIndices):
        self.colorPaletteIndices = colorIndices
        
    def convertColorsToPB(self, palette):
        '''Convert the gba values to the palette indices where those colors occur.
        We only need to do this for the Master tiles'''
        #for row in range(int(self.gba.shape[0])):
        #    for col in range(int(self.gba.shape[1])):
        #        pass
        print("\nMASTER TILE INFO========================")
        print(self.gba)
        print("")
        print("Palette = " + str(palette))
        print("")
        print("Colors = " + str(self.colors))
        print("")
        print(self.colorPaletteIndices)
        print("")

        gbalist = list(self.gba.flatten())
        tdatalist = []
        for colorvalue in gbalist:
            index = self.colors.index(colorvalue)
            tdatalist.append(self.colorPaletteIndices[index])
        self.tdata = np.array(tdatalist, dtype=int).reshape(8,8)
        print(self.tdata)
        print("\n\n")
        

    def printTdataHex(self):
        '''Make tdata in a printable form'''
        fulls = "{"
        for i, row in enumerate(self.tdata):
            s = "0x"
            for j, val in enumerate(row):
                s += utils.convertHexSingle(val)
                #if j < len(row)-1:
                #    s += ", "
                #else:
                #    s += "}"
            fulls += s
            if i < len(self.tdata)-1:
                fulls += ", "
            else:
                fulls += "}"
        return fulls

    def printForSBB(self):
        h = 0
        v = 0
        if self.hflip == True:
            h = 1
        if self.vflip == True:
            v = 1
        val = self.pb<<12 | v<<11 | h<<10 | self.tid
        print(val)
        return utils.dec2hex(val, 4)
