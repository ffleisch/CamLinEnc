import numpy as np

import shiftDetector as sD
import cv2

from scipy.signal import argrelextrema


class ShiftDetectorCorrelation(sD.ShiftDetector):

    def __init__(self,debug_draw=False):
        super(ShiftDetectorCorrelation, self).__init__(debug_draw)

    def set_base_image(self, base_image_roi):

        if self.do_debug_draw:
            self.debug_img_dict["Base Image"]=(0,base_image_roi.copy())
            self.debug_img_dict["Base Image Preprocessed"]=(1,self.preprocess_roi(base_image_roi.copy()))


        # find the brightness distribution of the home position
        self.base_brightness = self.find_brightness_curve(base_image_roi)

        # determine the periodicity of the rope

        # absolute spectrum of a dft
        dft = np.abs(np.fft.fft(self.base_brightness))

        # period of the signal in pixels
        # find index of the most significant peak in the FT (excluding index 0)
        # determine frequency equating to that index using np.fft.fftfreq
        # 1/freq=period
        self.period = 1 / np.fft.fftfreq(len(dft))[(np.argmax(dft[1:int(len(dft)/2)]) + 1)]

        self.shift = 0
        self.rotations = 0
        self.last_shift = None

        if self.do_debug_draw:
            self.debug_plot_dict["Base Brightness Curve"]=(0,self.base_brightness.copy())




    # find the average brightness in a column of the roi
    # preprocess that image before
    def find_brightness_curve(self,img):
        img_prep = self.preprocess_roi(img)
        # plt.imshow(img_prep,cmap="gray")
        # plt.show()
        return [sum(img_prep[:, i]) / (img_prep.shape[0] * 255) for i in range(img_prep.shape[1])]

    # do a adaptive threshold and some blurring
    # suppreses brightness variation over the image
    def preprocess_roi(self,img):
        sigma1 = 5
        sigma2 = 30
        img_blur = cv2.GaussianBlur(img, (0, 0), sigma1, sigma1)
        img_roi_flat = cv2.GaussianBlur(img, (0, 0), sigma2, sigma2)
        return cv2.absdiff(img_blur, img_roi_flat)

    def find_shift(self, img_roi):

        # get the brightness curve
        brightness = self.find_brightness_curve(img_roi)


        if self.do_debug_draw:
            self.debug_plot_dict["Brightness Curve"] = (2, brightness.copy())
            self.debug_plot_dict["Base Brightness Curve"]=(0,self.base_brightness.copy())

        l = len(brightness)



        # only take the middle of it
        # this is needed for the correlation to have no edge artifacts
        # window is what is left ot on the ends and therefore the length of the result of the correlation
        window=2
        brightness = brightness[int(self.period*window/2):int(l- self.period*window/2)]

        #check if there is enough left for the correlatiuon to be reliable
        if l<(window+3)*self.period:
            raise ValueError("not enough periods in frame")

        #brightness = brightness[int(l / 3):int(2 * l / 3)]

        # correlate the current brightness distribution and the brightness distribution of the home position
        # mode="valid" only output where the shorter brightness fits entirely onto the base_brightness
        correlation = np.correlate(self.base_brightness, brightness, mode="valid")

        if self.do_debug_draw:
            self.debug_plot_dict["Correlation"] = (4, correlation.copy())

        # clip the correlation
        #correlation = correlation[:math.ceil(period * 2.5)]

        # clip anything below the average to avoid detecting local maxima in the valleys
        correlation = np.maximum(correlation, np.average(correlation))

        # the maximum of the correlation indicates how much brightness is shifted from base_brightness
        maxima = argrelextrema(correlation, np.greater)


        if self.do_debug_draw:
            self.debug_plot_dict["Correlation Clipped"]=(5,correlation.copy())
            self.debug_img_dict["Image Raw"]=(2,img_roi.copy())
            self.debug_img_dict["Image Filtered"]=(3,self.preprocess_roi(img_roi.copy()))


        if len(maxima[0]) >= 2:
            # print(maxima)
            # print(maxima[0][0]-maxima[0][1])
            #for m in maxima[0]:
            #    axs[1].plot(m, correlation[m], "rx")
            self.shift = maxima[0][0]
            # print(shift)
        else:
            #print("oof")
            self.shift = np.argmax(correlation)

        #phase  unwrapping
        # increment a counter if shift rolls over(period)
        if self.last_shift is not None:
            if abs(self.last_shift - self.shift) > self.period / 2:
                if self.last_shift > self.shift:
                    self.rotations += 1
                else:
                    self.rotations -= 1
        self.last_shift = self.shift

        if self.do_debug_draw:
            self.debug_plot_dict["Shift"]=(6,self.shift)

        return (self.rotations+self.shift/self.period)


