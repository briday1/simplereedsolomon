import numpy as np

def bin2dec( bits, length ):

    rows = int(len(bits)/length)
    bits = np.reshape( bits, (rows, length) )
    return [int(x, 2) for x in (''.join(str(i) for i in b) for b in bits)]


def dec2bin( decimals, digits ):

    aa = np.array([list(format(d,'0'+str(digits)+'b')) for d in
        decimals]).reshape(-1)

    return np.array([int(x) for x in aa])

def char2dec( chars ):
    
    return [ord(x) for x in chars]


def dec2char( decimals ):

    return ''.join(chr(x) for x in decimals)
