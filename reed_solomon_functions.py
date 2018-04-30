import numpy as np
import unireedsolomon as rs
import conversions as co
'''
RS_ENCODE encodes an input bit stream with an (n,k) Reed Solomon code

INPUTS:
- in_bits: (N,1) array of binary data
- n: number of output bytes per codeword
- k: number of input bytes per codeword


'''


def rs_encode(in_bits, n, k, **kwargs):

    byte_len = 8

    coder = rs.RSCoder(n, k)

    # Add 0s to end of in_bits to make multiple of k bytes (if necessary)
    in_bits = pad_to_multiple(in_bits, byte_len * k)
    # Convert to Decimal
    dec_array = np.array(co.bin2dec(in_bits, byte_len))
    # reshape for coder input
    dec_array = dec_array.reshape(-1, k)

    cc_str = ''.join(coder.encode_fast(x) for x in dec_array)

    # Convert to decimal
    cc_dec = co.char2dec(cc_str)
    # convert to binary
    cc_bits = co.dec2bin(cc_dec, byte_len)

    # Interleave
    if ('bInterleave' in kwargs):
        bIntlv = kwargs['bInterleave']
    else:
        bIntlv = False

    intlv = np.arange(len(cc_bits))
    if bIntlv:
        np.random.shuffle(intlv)

    cc_bits = cc_bits[intlv]

    # return cc_bits, dec_array, cc_str, in_bits, intlv
    return cc_bits, intlv


def rs_decode(cc_bits, n, k, **kwargs):

    byte_len = 8
    coder = rs.RSCoder(n, k)

    # determine number of codewords that have been passed given an RS(n,k)
    # encoder
    numWords = len(cc_bits) / n / byte_len

    # de-interleave
    if ('intlv' in kwargs):
        intlv = kwargs['intlv']
    else:
        intlv = np.arange(len(cc_bits))

    cc_bits_deintlv = np.zeros(cc_bits.shape, dtype='uint8')
    cc_bits_deintlv[intlv] = cc_bits.astype('uint8')

    # convert to decimal
    cc_dec = co.bin2dec(cc_bits_deintlv, byte_len)


    # convert to str
    cc_str = co.dec2char(cc_dec)

    # reshape uncoded decimal in case you can't decode
    cc_dec =  np.array(cc_dec).reshape( -1, n )

    # Pre-Allocate
    ii_str = []
    ii_dec = []
    for x in range(numWords):
        ii_str.append([])
        ii_dec.append([])
        ii_str[x] = ('\x00', '\x00')

    # Try-Catch (use RS built in checker)
    for x in range(numWords):
        thisMsg = cc_str[x * n:(x + 1) * n]
        # Will this message get decoded?
        if coder.check_fast(thisMsg):
            ii_str[x] = coder.decode_fast(thisMsg, nostrip=True)
            ii_dec[x] = co.char2dec(ii_str[x][0])
            # Left Pad with zeros (punctured RS -- expected by decoder)
            missZero = k - len(ii_dec[x])
            ii_dec[x] = np.concatenate(
                (ii_dec[x], np.zeros(missZero))).astype('uint8')

        else:
            # Just truncate the uncoded decimal values (right most k bytes)
            ii_dec[x] = cc_dec[x][-k:].astype('uint8') 




    ii_bits = np.array([list(co.dec2bin(ii_dec[x], byte_len).astype('uint8'))
                        for x in range(numWords)])

    ii_bits = np.reshape(ii_bits, (byte_len * k * numWords, ))

    # return ii_bits, ii_dec, ii_dec_old, cc_bits_deintlv, cc_dec, cc_str, ii_str
    return ii_bits


def pad_to_multiple(in_bits, k):

    numInBits = len(in_bits)
    if numInBits % k > 0:
        zeroAdd = k - (numInBits % k)
    else:
        zeroAdd = 0

    # Left zero-pad (punctured RS)
    return np.concatenate(([int(x) for x in list('0' * zeroAdd)],
                           in_bits)).astype('uint8')
