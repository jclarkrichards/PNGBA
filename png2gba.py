import cv2
import numpy as np
import math
import argparse
from sbb import SBB #, ScreenBlock
from palette import PaletteGroup
from copy import deepcopy

parser = argparse.ArgumentParser(description='Process image files into C++ code for GBA')
parser.add_argument('--image', '-i', help="Path and name of the image")
parser.add_argument('--out', '-o', help='Output file name placed in same location as input')
parser.add_argument('--sbb', '-s', help='The size of each sbb.  Defaults to 256')
args = parser.parse_args()

print("Image name = " + args.image)
name = args.image.split('.')[0]

class PNGBA(object):
    def __init__(self, rawimage, sbb_size=256):
        self.rawimage = cv2.imread(rawimage)
        self.sbb_size = int(sbb_size)
        self.imshape = self.rawimage.shape
        self.sbbs = []
        self.tiles = []
        self.masters = [] #Master tiles
        print("Raw Image has dimensions: " + str(self.imshape) + " with a sbb size of " + str(self.sbb_size))
        self.utiles = []  #A list of unique tiles
        self.palgroup = None
        
    def validImage(self):
        '''Return True if this is a valid image'''
        return self.imshape[0] % self.sbb_size == 0 and self.imshape[1] % self.sbb_size == 0

    def createSBB(self):
        '''Divide the image into SBBs.  Each SBB has size of sbb_size x sbb_size'''
        sbbs_x = self.imshape[0] / self.sbb_size
        sbbs_y = self.imshape[1] / self.sbb_size
        for i in range(int(sbbs_x)):
            for j in range(int(sbbs_y)):
                x0 = i * self.sbb_size
                x1 = x0 + self.sbb_size
                y0 = j * self.sbb_size
                y1 = y0 + self.sbb_size
                self.sbbs.append(SBB(self.rawimage[x0:x1, y0:y1], self.sbb_size))

    def gatherTiles(self):
        '''Gather up all of the tiles from the SBBs'''
        for sbb in self.sbbs:
            self.tiles += sbb.tiles
        for i, tile in enumerate(self.tiles):
            tile.id = i

    def getUniqueTiles(self):
        '''Continue looping through all of the tiles until we find all of the master tiles'''
        print("\nGetting the Unique tiles now")
        temp = [0] * len(self.tiles)  #only contains either 0 or None
        finished = False
        while(not finished):
            try:
                index = temp.index(0)
            except ValueError:
                finished = True
            else:
                master = self.tiles[index]
                self.masters.append(master)
                temp[index] = 1
                for i, tile in enumerate(self.tiles):
                    if temp[i] == 0:
                        if master == tile:
                            #master.tileids.append(i)
                            master.addTile(self.tiles[i])
                            temp[i] = 1



        #print("--------------------Check colors---------------------")
        #for tile in self.tiles:
        #    print(tile.colors)
        #    print("")
        #print("=====================================================\n")
        print("There are " + str(len(self.masters)) + " master tiles\n\n")
        #for master in self.masters:
        #    print("Master has " + str(len(master.tileids)) + " tiles")
        #    #print(master.tileids)
        #    for tileid in master.tileids:
        #        print("HFLIP: " + str(self.tiles[tileid].hflip) + " VFLIP: " + str(self.tiles[tileid].vflip))

    def getUniqueColorLists(self):
        for master in self.masters:
            master.setUniqueColorLists()

    def sortMasterTiles(self):
        '''Sort the master tiles so that the tiles with the most colors and the most other tiles are first'''
        unsortedlist = []
        sortedlist = []
        sorted_indices = []
        newmasters = [None] * len(self.masters)
        for i, master in enumerate(self.masters):
            master.setTID(i)
            sortedlist.append((len(master.colors), len(master.colorsets)))
            unsortedlist.append((len(master.colors), len(master.colorsets)))

        sortedlist.sort()
        sortedlist.reverse()
        for val in sortedlist:
            index = unsortedlist.index(val)
            sorted_indices.append(index)
            unsortedlist[index] = None

        for i in range(len(sorted_indices)):
            newmasters[i] = self.masters[sorted_indices[i]]
        self.masters = newmasters

        #print("\nNew Masters=========================================")
        for i, master in enumerate(self.masters):
            master.setTID(i)
            print("Master " + str(master.tid) + ",\tTile Index = " + str(master.id) + ",\t#Colors = " + str(len(master.colors)) + ",\t#Other Tiles = " + str(len(master.othertiles)) + ",\tUnique Color Sets = " + str(len(master.colorsets)))
            
    def createPalettes(self):
        self.palgroup = PaletteGroup()
        self.palgroup.createPalettes(self.masters)
        print("\n\n")

    def prepareMasterTiles(self):
        '''Loop through all master tiles and convert their gba values to
        palette indices where those colors occur'''
        for master in self.masters:
            master.convertColorsToPB(self.palgroup.palettes[master.pb])
        
        
    def showColorsTest(self):
        print("\n\n====================COLORS====================")
        for tile in self.tiles:
            print(tile.colors)
        print("\n===================END COLORS==================\n\n")

    def createCPP(self):
        '''Now that we have all of the info we need, we need to create the C++ file'''
        with open(name+".h", "w") as f:
            f.write("#ifndef " + name.upper() + "\n")
            f.write("#define " + name.upper() + "\n")
            
            f.write("\n\n//============Palettes===============\n")
            f.write("u16 palettes[16][16] = {\n")
            for i, pal in enumerate(self.palgroup.palettes):
                if i < len(self.palgroup.palettes) - 1:
                    f.write(str(pal) + ",\n")
                else:
                    f.write(str(pal)+ "\n")
            f.write("};\n")

            f.write("\n//============Master Tiles=================\n")
            f.write("u32 tiles["+str(len(self.masters))+"][8] = {\n")
            for i, master in enumerate(self.masters):
                #f.write("{\n")
                f.write(master.printTdataHex())
                #if i < len(self.masters)-1:
                #    f.write(",\n")
                #f.write("},\n\n")
                f.write(",\n")
            f.write("};\n\n")


            f.write("\n\n//==================SBB Data====================\n")
            tilesPerSBB = int((self.sbb_size*self.sbb_size)/64)
            tilesPerRow = int(self.sbb_size / 8)
        
            f.write("u16 sbb["+str(len(self.sbbs))+"]["+str(tilesPerSBB)+"] = {\n")
            for i, tile in enumerate(self.tiles):
                if i % tilesPerSBB == 0:
                    f.write("\n{")
                #if i % tilesPerRow == 0:
                #    if i != 0:
                #        f.write(",\n")
                #    #f.write("{")
                f.write(tile.printForSBB())
                if (i % tilesPerRow) < tilesPerRow-1:
                    f.write(", ")
                else:
                    f.write(",\n")
                if (i % tilesPerSBB) == tilesPerSBB-1:
                    if i < tilesPerSBB-1:
                        f.write("},\n")
                    else:
                        f.write("},\n")
            
            f.write("\n};\n\n")
            
            f.write("#endif")

            

if __name__ == "__main__":
    if args.image is not None:
        if args.sbb is not None:
            pngba = PNGBA(args.image, args.sbb)
        else:
            pngba = PNGBA(args.image)

        if pngba.validImage():
            print("Valid image")
            pngba.createSBB()
            print("The number of SBBs is " + str(len(pngba.sbbs)))
            

            pngba.gatherTiles()
            print("There are " + str(len(pngba.tiles)) + " total tiles")
            #pngba.showColorsTest()

            pngba.getUniqueTiles()
            pngba.getUniqueColorLists()
            pngba.sortMasterTiles()
            
            #pngba.showColorsTest()
            #print("There are " + str(len(pngba.masters)) + " master tiles")
            #print(pngba.sbbs[0].tiles[0].gba)
            #print(pngba.sbbs[0].tiles[0].masks)
            pngba.createPalettes()

            """
            print("\n\n-----------__CHECKING THE MASTERS_--------------")
            for i, master in enumerate(pngba.masters):
                print("TILE ID = " + str(master.tid))
                print("HFLIP = " + str(master.hflip))
                print("VFLIP = " + str(master.vflip))
                print("PALETTE = " + str(master.pb))
                #print("Num Children = " + str(len(master.othertiles)))
                print("")
                for child in master.othertiles:
                    print("\t\tTILE ID = " + str(child.tid))
                    print("\t\tHFLIP = " + str(child.hflip))
                    print("\t\tVFLIP = " + str(child.vflip))
                    print("\t\tPALETTE = " + str(child.pb))
                    print("")
                print("")
                if i == 20:
                    break
            """
            pngba.prepareMasterTiles()
            pngba.createCPP()
        else:
            print("Image is not valid, so cannot proceed further")
