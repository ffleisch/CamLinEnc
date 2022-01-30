import numpy as np
import scipy.fft

import shiftDetector as sD

from matplotlib import pyplot as plt
import scipy.ndimage
from scipy.signal import argrelextrema


def make_fade_matrix(a, b, shape):
    """
    Create an image of a given size with the edges fading to 0
    Multiplying by it allows to eliminate edge effects created during the IFFT
    :param a: How many Percent of the width too fade out
    :param b: How many percent of the height to fade out
    :param shape: Shape of the fade matrix
    :return: A matrix containing values form 0 to 1
    """
    def helper(x, a, w):
        # print(x,a,w)
        x = 1 - 2 * abs(x / (w - 1) - 0.5)
        x = 1 if x >= a else x / (a + 1 / w)
        return x

    # print(shape)

    arr = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            arr[i][j] = helper(i, b * 2, shape[0]) * helper(j, a * 2, shape[1])
    plt.imshow(arr)
    plt.show()

    return arr


class ShiftDetectorRestoration(sD.ShiftDetector):

    def __init__(self):
        """
        Extract a shift from an Image with respect to a single base image using the Shift Detection by Restoration
        Shifts of subsequent Images are added up using phase unwrapping
        """
        self.base_image_roi = None
        self.beta = 10000

    def set_base_image(self, base_image_roi):
        """
        Set the base image to be referenced for position
        Calculate the period of the signal using autocorrelation
        Precalculate conjugate and power spectrum of the base image for later use
        :param base_image_roi: Base image to be used, already cropped
        """
        self.edge_fade = make_fade_matrix(0.3, 0, base_image_roi.shape)

        self.base_image = base_image_roi * self.edge_fade * 0.5

        self.base_dft = scipy.fft.fft2(base_image_roi, norm="ortho")

        self.base_dft_conjugate = np.conjugate(self.base_dft)

        self.base_power_spectrum = self.base_dft * self.base_dft_conjugate

        self.last_shift = None
        self.rotations = 0


        #because we already need the dft and conjugate we can easily calculate the autocorrelation by the folding theorem
        autocorrelation_dft = self.base_dft * self.base_dft_conjugate
        autocorrelation = scipy.fft.ifft2(autocorrelation_dft)

        slice = np.real(autocorrelation[0, :])

        slice = scipy.ndimage.gaussian_filter1d(slice, slice.shape[0] * 0.03) - scipy.ndimage.gaussian_filter1d(slice,
                                                                                                                slice.shape[
                                                                                                                    0] * 0.1)

        slice = np.maximum(slice, np.average(slice))

        maxmima = argrelextrema(slice[1:], np.greater)
        self.period = maxmima[0][0]
        print("Period:", self.period)
        # autocorrelation=scipy.fft.fftshift(autocorrelation)
        # plt.imshow(np.real(autocorrelation))

        plt.plot(slice)
        plt.show()

    def find_shift(self, img_roi):
        """
        Determine the shift of a given image with respect to the base image and tally it up for a total shift
        :param img_roi: Cropped input image
        :return: Total shift with respect to the base image in pixels
        """


        #fade the edges of the input image to black
        #this eliminates edge effects by making the border continuos without sudden jumps
        img_roi = img_roi * self.edge_fade
        img_dft = scipy.fft.fft2(img_roi)


        #heart of the shift detection by restoration
        shift_approx_dft = (img_dft * self.base_dft_conjugate) / (self.base_power_spectrum + self.beta)

        #get the actaul filter mask by inverse fft
        shift_approx = scipy.fft.ifft2(shift_approx_dft, norm="ortho")


        #there only should be a real part but due to numerical issues an imgainary part on the order of 1e13 has to be discarded
        real_p = np.real(shift_approx)

        #find the brightest coordinate
        #it describes the shift contributing most to matching the current image up to the original
        max_index = np.argwhere(real_p == real_p.max())




        #some optional plotting for debugging
        #the image is shifted such that (0,0) lays in the center for ease of understanding
        w = real_p.shape[1]
        h = real_p.shape[0]

        plt.cla()
        plt.imshow(scipy.fft.fftshift(real_p),cmap="gray",vmin=0)
        plt.plot((w/2+max_index[0][1])%w,(h/2+max_index[0][0])%h,"rx")
        plt.pause(0.01)
        plt.draw()
        #'''

        #image coordinates wrap below zero around to width
        #make so they are centered aorund 0
        self.shift = (max_index[0][1] + w / 2) % w - w / 2


        #phase unwrapping
        #needs an accurate period
        if self.last_shift is not None:
            if abs(self.last_shift - self.shift) > self.period / 2:
                if self.last_shift > self.shift:
                    self.rotations += 1
                else:
                    self.rotations -= 1
                print(self.rotations)
        self.last_shift = self.shift
        # print(self.shift)


        #return the total shift
        #needs an accurate period
        return -(self.period * self.rotations + self.shift)
        # return self.rotations
