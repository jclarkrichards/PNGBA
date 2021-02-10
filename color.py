import numpy as np
from utils import *
import math

def color15(color32):
    '''Convert 32-bit colors 0-255 to gba 15-bit colors 0-31'''
    r = int((color32[0]/256.0)*32)
    g = int((color32[1]/256.0)*32)
    b = int((color32[2]/256.0)*32)
    return (r, g, b)


def color15hex(color15):
    '''Convert 15-bit color to hex formatted gba 15-bit color'''
    bincolor = dec2bin_list(color15, 5)
    binvalue = ''
    for color in bincolor:
        binvalue += color[::-1]
    decvalue = 0
    for i, c in enumerate(binvalue):
        if c == '1':
            decvalue += int(math.pow(2, i))
    hexval = hex(decvalue)
    return '0x' + hexval.split('0x')[1].zfill(4)


def color32hex(color32):
    '''Convert a 32bit tuple into a 15bit hex'''
    gbacolor = color15(color32)
    return color15hex(gbacolor)


def gbaColors(image):
    '''Convert a 3 channel (RGB) image into 1 channel hex'''
    result = np.empty(8*8, dtype=object).reshape(8, 8)
    for	i in range(image.shape[0]):
        for j in range(image.shape[1]):
            r =	image[i, j, 2]
            g =	image[i, j, 1]
            b =	image[i, j, 0]
            result[i, j] = color32hex((r, g, b))
    return result


class ColorMask(object):
    def __init__(self, mask, color):
        #print("\nColor mask for color " + str(color))
        self.M = mask
        #print(self.M)
        #print(bin2decRows(self.M))
        #print("")
        
        self.mask = np.zeros(4*8, dtype=object).reshape(4,8)
        self.norm_mask = self.mask[0]

        self.color = color
        self.generateFlippedMasks()
        #print(getJMatrix())
        #temp = self.generateBinaryMask()
        #print(temp)
        #temp = self.generateDecMask(temp)
        #print(self.maskDict)
        
    def __str__(self):
        return "COLOR: " + str(self.color) + "\n" + str(self.M) + "\n"

    def generateFlippedMasks(self):
        '''Take the self.M color mask which is in binary, and generate all of the flipped versions'''
        J = getJMatrix()
        HF = self.M.dot(J)
        VF = J.dot(self.M)
        HVF = J.dot(self.M).dot(J)
        #print("--------------------------")
        self.mask[0] = bin2decRows(self.M)
        self.mask[1] = bin2decRows(HF)
        self.mask[2] = bin2decRows(VF)
        self.mask[3] = bin2decRows(HVF)
        #print(self.mask)
        #print("")

    def getMaskInfo(self):
        print(self.color)
        print(self.mask)
        print("")

   




