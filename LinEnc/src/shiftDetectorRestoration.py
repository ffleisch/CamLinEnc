import numpy as np
import scipy.fft

import shiftDetector as sD

from matplotlib import pyplot as plt
import scipy.ndimage
from scipy.signal import argrelextrema



def make_fade_matrix(a,b,shape):

    def helper(x,a,w):
        #print(x,a,w)
        x=1-2*abs(x/(w-1)-0.5)
        x=1 if x>=a else x/(a+1/w)
        return x
    #print(shape)

    arr=np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            arr[i][j]=helper(i,a*2,shape[0])*helper(j,b*2,shape[1])
    plt.imshow(arr)
    plt.show()

    return arr



class ShiftDetectorRestoration(sD.ShiftDetector):

    def __init__(self):
        self.base_image_roi=None
        self.beta=100000


    def set_base_image(self, base_image_roi):
        self.edge_fade=make_fade_matrix(0,0.3,base_image_roi.shape)


        self.base_image=base_image_roi*self.edge_fade*0.5

        self.base_dft=scipy.fft.fft2(base_image_roi,norm="ortho")

        self.base_dft_conjugate=np.conjugate(self.base_dft)

        self.base_power_spectrum=self.base_dft*self.base_dft_conjugate

        self.last_shift=None
        self.rotations=0



        autocorrelation_dft=self.base_dft*self.base_dft_conjugate
        autocorrelation=scipy.fft.ifft2(autocorrelation_dft)

        slice=np.real(autocorrelation[0,:])

        slice=scipy.ndimage.gaussian_filter1d(slice,slice.shape[0]*0.03)-scipy.ndimage.gaussian_filter1d(slice,slice.shape[0]*0.1)

        slice=np.maximum(slice,np.average(slice))

        maxmima=argrelextrema(slice[1:],np.greater)
        self.period=maxmima[0][0]
        print("Period:",self.period)
        #autocorrelation=scipy.fft.fftshift(autocorrelation)
        #plt.imshow(np.real(autocorrelation))

        plt.plot(slice)
        plt.show()



    def find_shift(self, img_roi):

        img_roi=img_roi*self.edge_fade
        img_dft=scipy.fft.fft2(img_roi)

        shift_approx_dft=(img_dft*self.base_dft_conjugate)/(self.base_power_spectrum+self.beta)

        shift_approx=scipy.fft.ifft2(shift_approx_dft,norm="ortho")

        real_p=np.real(shift_approx)
        img_p=np.imag(shift_approx)

        #print(np.max(real_p),np.min(real_p))


        max_index=np.argwhere(real_p==real_p.max())

        #print(max_index)

        w=real_p.shape[1]
        h=real_p.shape[0]

        '''plt.cla()
        plt.imshow(scipy.fft.fftshift(real_p),cmap="gray",vmin=0,vmax=255)
        plt.plot((w/2+max_index[0][1])%w,(h/2+max_index[0][0])%h,"rx")
        plt.pause(0.001)
        plt.draw()
        #'''

        self.shift=(max_index[0][1]+w/2)%w-w/2

        if self.last_shift is not None:
            if abs(self.last_shift - self.shift) > self.period / 2:
                if self.last_shift > self.shift:
                    self.rotations += 1
                else:
                    self.rotations -= 1
                print(self.rotations)
        self.last_shift=self.shift
        #print(self.shift)

        return (self.period*self.rotations+self.shift)
        #return self.rotations
