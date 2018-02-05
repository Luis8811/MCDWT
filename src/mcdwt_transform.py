import cv2
import numpy as np
import pywt
import math

import image_io
import pyramid_io
import motion_compensation
import color_dwt

def forward(input = '../images/', output='/tmp/', n=5, l=2):
    '''A Motion Compensated Discrete Wavelet Transform.

    Compute the 1D-DWT along motion trajectories. The input video (as
    a sequence of images) must be stored in disk (<input> directory)
    and the output (as a sequence of DWT coefficients that are called
    pyramids) will be stored in disk (<output> directory). So, this
    MCDWT implementation does not transform the video on the fly.

    Arguments
    ---------

        input : str

            Path where the input images are. Example:
            "../input/image".

        output : str

            Path where the (transformed) pyramids will be. Example:
            "../output/pyramid".

         n : int

            Number of images to process.

         l : int

            Number of leves of the MCDWT (temporal scales). Controls
            the GOP size. Examples: `leves`=0 -> GOP_size = 1, `leves`=1 ->
            GOP_size = 2, `levels`=2 -> GOP_size = 4. etc.

    Returns
    -------

        None.

    '''
    
    import ipdb; ipdb.set_trace()
    ir = image_io.ImageReader()
    iw = image_io.ImageWritter()
    pw = pyramid_io.PyramidWritter()
    x = 2
    for j in range(l): # Number of temporal scales
        A = ir.read(0, input)
        tmpA = color_dwt._2D_DWT(A)
        L_y = tmpA[0].shape[0]
        L_x = tmpA[0].shape[1]
        pw.write(tmpA, 0, output)        
        zero_L = np.zeros(tmpA[0].shape, np.float64)
        zero_H = (zero_L, zero_L, zero_L)
        AL = color_dwt._2D_iDWT(tmpA[0], zero_H)
        iw.write(AL, 1)
        AH = color_dwt._2D_iDWT(zero_L, tmpA[1])
        iw.write(AH, 1)
        i = 0
        while i < (n//x):
            B = ir.read(x*i+x//2, input)
            tmpB = color_dwt._2D_DWT(B)
            BL = color_dwt._2D_iDWT(tmpB[0], zero_H)
            BH = color_dwt._2D_iDWT(zero_L, tmpB[1])
            C = ir.read(x*i+x, input)
            tmpC = color_dwt._2D_DWT(C)
            pw.write(tmpC, x*i+x, output)
            CL = color_dwt._2D_iDWT(tmpC[0], zero_H)
            CH = color_dwt._2D_iDWT(zero_L, tmpC[1])
            BHA = motion_compensation.motion_compensation(BL, AL, AH)
            BHC = motion_compensation.motion_compensation(BL, CL, CH)
            iw.write(BH, x*i+x//2, output+'predicted')
            prediction = (BHA + BHC) / 2
            iw.write(prediction+128, x*i+x//2, output+'prediction')
            rBH = BH - prediction
            iw.write(rBH, x*i+x//2, output+'residue')
            rBH = color_dwt._2D_DWT(rBH)
            #import ipdb; ipdb.set_trace()
            pw.write(rBH, x*i+x//2 + 1000)
            rBH[0][0:L_y,0:L_x,:] = tmpB[0]
            pw.write(rBH, x*i+x//2, output)
            AL = CL
            AH = CH
            i += 1
            print('i =', i)
        x *= 2

def backward(input = '/tmp/', output='/tmp/', n=5, l=2):
    '''A (Inverse) Motion Compensated Discrete Wavelet Transform.

    iMCDWT is the inverse transform of MCDWT. Inputs a sequence of
    pyramids and outputs a sequence of images.

    Arguments
    ---------

        input : str

            Path where the input pyramids are. Example:
            "../input/image".

        output : str

            Path where the (inversely transformed) images will
            be. Example: "../output/pyramid".

         n : int

            Number of pyramids to process.

         l : int

            Number of leves of the MCDWT (temporal scales). Controls
            the GOP size. Examples: `l`=0 -> GOP_size = 1, `l`=1 ->
            GOP_size = 2, `l`=2 -> GOP_size = 4. etc.

    Returns
    -------

        None.

    '''
    
    #import ipdb; ipdb.set_trace()
    ir = image_io.ImageReader()
    iw = image_io.ImageWritter()
    pr = pyramid_io.PyramidReader()
    x = 2**l
    for j in range(l): # Number of temporal scales
        #import ipdb; ipdb.set_trace()
        A = pr.read(0, input)
        zero_L = np.zeros(A[0].shape, np.float64)
        zero_H = (zero_L, zero_L, zero_L)
        AL = color_dwt._2D_iDWT(A[0], zero_H)
        AH = color_dwt._2D_iDWT(zero_L, A[1])
        A = AL + AH
        iw.write(A, 0)
        i = 0
        while i < (n//x):
            B = pr.read(x*i+x//2, input)
            BL = color_dwt._2D_iDWT(B[0], zero_H)
            rBH = color_dwt._2D_iDWT(zero_L, B[1])
            C = pr.read(x*i+x, input)
            CL = color_dwt._2D_iDWT(C[0], zero_H)
            CH = color_dwt._2D_iDWT(zero_L, C[1])
            C = CL + CH
            iw.write(C, x*i+x, output)
            BHA = motion_compensation.motion_compensation(BL, AL, AH)
            BHC = motion_compensation.motion_compensation(BL, CL, CH)
            BH = rBH + (BHA + BHC) / 2
            B = BL + BH
            iw.write(B, x*i+x//2, output)
            AL = CL
            AH = CH
            i += 1
            print('i =', i)
        x //=2