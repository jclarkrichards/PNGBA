from color import *
from copy import deepcopy

"""
A Palette contains 16 colors.  The first color is always a transparent color, so there are only 15 visible colors per palette.
All colors are in hex 15bit format
"""

class Palette(object):
    def __init__(self):
        self.colors = [None] * 16
        self.transparent = color32hex((255, 0, 255))
        self.colors[0] = self.transparent

    def __str__(self):
        s = ''
        for i, color in enumerate(self.colors):
            if color is None:
                color = '0x0000'
            if i < len(self.colors)-1:
                s += color + ', '
            else:
                s += color
        return '{' + s + '}'
        
    def __eq__(self, other):
        return self.colors == other

    def contains(self, colors):
        '''Check to see if the colors are contained in this palette'''
        pass

    def canPlaceColors(self, colors, indices=[]):
        '''Check to see if able to place the colors in this palette without changing order.
        If a list of indices is provided, then you only need to check if those colors can be placed at those indices'''
        if len(indices) == 0:
            test = [k for k in self.colors if k is not None]
            test += colors
            
            if len(list(set(test))) > len(self.colors):
                return False
        else:
            print("COLOR INDICES: " + str(indices))
            for i, index in enumerate(indices):
                if self.colors[index] != None and self.colors[index] != colors[i]:
                    return False
        
        return True

    def indexList(self, colorset):
        '''Given the colors, return a list of indices where those colors appear in this palette'''
        indices = []
        colors = deepcopy(self.colors)
        for color in colorset:
            try:
                index = colors.index(color)
            except ValueError:
                index = colors.index(None)
                colors[index] = -1
            finally:
                indices.append(index)
        return indices

    def addColors(self, colorset, indices):
        for i in range(len(colorset)):
            self.colors[indices[i]] = colorset[i]

    
    
"""
A PaletteGroup is a group of 16 Palette objects.
"""
class PaletteGroup(object):
    def __init__(self):
        self.palettes = []
        for i in range(16):
            self.palettes.append(Palette())

        print("")
        print(self)
        #for palette in self.palettes:
        #    print(palette)

    def __str__(self):
        s = ""
        for palette in self.palettes:
            s += str(palette) + "\n"
        return s
            
    def createPalettes(self, masters):
        '''The master tiles are already in order.  Check to see if their colors exist in a palette.  All of their children have to have their colors in different palettes'''
        for master in masters:
            print("\n\n============NEW MASTER==============================")
            ignorelist = [] #contains indices of Palettes to ignore
            colorIndices = [] #contains indices of where to place colors in a palette (masters with more than 1 colorset have to place all colorsets in the same indices of different palettes
            for colorset in master.colorsets:
                print("\nCOLORSET: " + str(colorset))
                for p, palette in enumerate(self.palettes):
                    print("Checking palette " + str(p) + " :: " + str(palette))
                    if p not in ignorelist:
                        if palette.canPlaceColors(colorset, colorIndices):
                            print("Can place the colors")
                            #print("COLOR INDICES: " + str(colorIndices))
                            if len(colorIndices) == 0:
                                colorIndices = palette.indexList(colorset)
                            palette.addColors(colorset, colorIndices)
                            ignorelist.append(p)
                            print("Placed colorset in palette " + str(p))
                            master.setPalette(colorset, p)
                            master.setColorIndices(colorIndices)
                            break
                        else:
                            print("Cannot place the colors in this palette, NEXT!!!")
                    else:
                        print(str(p) + " is being ignored, NEXT!!!")

        print("\n============FINISHED PALETTES====================")
        for palette in self.palettes:
            print(palette)






