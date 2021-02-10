import numpy as np
import math


hexdict = {0:'0', 1:'1', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'a', 11:'b', 12:'c', 13:'d', 14:'e', 15:'f'}

def dec2bin(dec, pad=0):
    '''convert a decimal value to a binary value'''
    binval = ''
    if dec == 0:
        binval = '0'
    else:
        while dec > 0:
            binval += str(dec%2)
            dec = int(dec/2)
    return binval[::-1].zfill(pad)


def dec2bin_list(declist, pad=0):
    '''Same as above, but there is a list of values instead'''
    result = []
    for d in declist:
        result.append(dec2bin(d, pad))
    return result

def dec2hex(decvalue, padding):
    return '0x'+hex(decvalue).split('0x')[1].zfill(padding)

"""
def bin2dec(binary, reversed=False):
    if not reversed:
        binary = binary[::-1]
    indices = [k for k in range(len(binary)) if binary[k] == '1']
    result = 0
    for i in indices:
        result += int(math.pow(2, i))
    return result

def bin2decList(binlist, reversed=False):
    result = []
    for b in binlist:
        result.append(bin2dec(b, reversed))
    return result
"""
def getJMatrix():
    J = np.zeros(8*8, dtype=int).reshape(8,8)
    for i in range(J.shape[0]):
        J[i,7-i] = 1
    return J

def bin2decRows(M):
    '''Given a matrix, convert each row from binary to decimal and return the flattened list'''
    decvalues = []
    for row in range(M.shape[0]):
        indices = [k for k in range(len(M[row])) if M[row][k] == 1]
        result = 0
        for i in indices:
            result += int(math.pow(2, 7-i))
        decvalues.append(result)
    return decvalues

def convertHexSingle(value):
    '''Convert a single value to its hex equivalent'''
    return hexdict[int(value)]


