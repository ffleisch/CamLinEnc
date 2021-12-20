import math
import os
import time

import imageio

import visvis as vv
import numpy as np
import cv2
import roi

from matplotlib import pyplot as plt

from scipy.signal import argrelextrema
import datetime

# find the average brightness in a column of the roi
# preprocess that image before
def find_brightness_curve(img):
    img_prep = preprocess_roi(img)
    # plt.imshow(img_prep,cmap="gray")
    # plt.show()
    return [sum(img_prep[:, i]) / (img_prep.shape[0] * 255) for i in range(img_prep.shape[1])]


# do a adaptive threshold and some blurring
# suppreses brightness variation over the image
def preprocess_roi(img):
    sigma1 = 5
    sigma2 = 30
    img_blur = cv2.GaussianBlur(img, (0, 0), sigma1, sigma1)
    img_roi_flat = cv2.GaussianBlur(img, (0, 0), sigma2, sigma2)
    return cv2.absdiff(img_blur, img_roi_flat)


# use visvis to show images
# visvis doesent play nicely with pyplot
show_img = False

if __name__ == "__main__":

    path = "../recordFootage/footageRecorder/data"
    test_name = "motor_test_5"

    video_path = os.path.abspath(os.path.join(path, test_name, test_name + ".mp4"))
    print(video_path)


    #from what image should the roi be extracted?
    #if you give it a differential image while the rope is moving, all background distractions will be ignored
    reader = imageio.get_reader(video_path)
    for i in range(360):
        reader.get_next_data()

    img0 = reader.get_next_data()
    img0 = cv2.absdiff(img0,reader.get_next_data())
    img0=img0
    plt.imshow(img0)
    plt.show()

    if show_img:
        a1 = vv.subplot(131);
        a2 = vv.subplot(132);
        a3 = vv.subplot(133);
        t = vv.imshow(img0, axes=a1)
        t2 = vv.imshow(img0.copy(), axes=a2)
        t3 = vv.imshow(img0.copy(), axes=a3)

    # graphs_plots=vv.figure()

    # img_last=[]
    # diff=[]

    # find the roi
    # doesent change throughout the video
    roi_params = roi.find_roi_parameters(img0, debug=True)
    print(roi_params)
    print(roi_params.size)
    print(roi_params.rho, roi_params.theta)

    # find the brightness distribution of the home position
    base_brightness = find_brightness_curve(roi.extract_roi(img0[:, :, 0], roi_params))

    # determine the periodicity of the rope

    # absolute spectrum of a dft
    dft = np.abs(np.fft.fft(base_brightness))

    # period of the signal in pixels
    # find index of the most significant peak in the FT (excluding index 0)
    # determine frequency equating to that index using np.fft.fftfreq
    # 1/freq=period
    period = 1 / np.fft.fftfreq(len(dft))[(np.argmax(dft[1:]) + 1)]
    print(period)

    #fig, axs = plt.subplots(2)

    #axs[0].plot(base_brightness)
    #axs[1].plot(dft)
    #plt.show()

    fig, axs = plt.subplots(2)
    plt.ion()

    all_shifts = []
    rotations = 0
    all_shifts_summed = []
    last_shift = None

    for num,frame in enumerate(reader):
        start_time = time.time()

        img_copy = frame.copy()
        img = frame[:, :, 0]
        # img_copy=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        # extract roi from image
        img_roi = roi.extract_roi(img, roi_params)

        # get the brightness curve
        brightness = find_brightness_curve(img_roi)

        # axs[1].plot(brightness)
        # axs[1].plot(base_brightness)

        l = len(brightness)
        # only take the middle of it
        # this is needed for the correlation to have no adge artifacts
        brightness = brightness[int(l / 3):int(2 * l / 3)]

        # correlate the current brightness distribution and the brightness distribution of the home position
        # mode="valid" only output where the shorter brightness fits entirely onto the base_brightness
        correlation = np.correlate(base_brightness, brightness, mode="valid")




        # clip the correlation
        correlation = correlation[:math.ceil(period * 2.5)]

        # center it around 0
        # not necessary I think
        correlation = correlation - np.average(correlation)
        correlation = np.maximum(correlation, 0)
        # the maximum of the correlation indicates how much brightness is shifted from base_brightness
        maxima = argrelextrema(correlation, np.greater)
        shift = 0
        if len(maxima[0]) >= 2:
            # print(maxima)
            # print(maxima[0][0]-maxima[0][1])
            #for m in maxima[0]:
            #    axs[1].plot(m, correlation[m], "rx")
            shift = maxima[0][0]
            # print(shift)
        else:
            #print("oof")
            shift = np.argmax(correlation)

        '''#clip the correlation
        correlation=correlation[:math.ceil(period)]
        #center it around 0
        #not necessary I think
        correlation=correlation-np.average(correlation)
        #the maximum of the correlation indicates how much brightness is shifted from base_brightness
        shift=np.argmax(correlation)'''


        print(str(datetime.timedelta(seconds=num/30)),shift)


        # increment a counter if shift rolls over(period)
        if last_shift is not None:
            if abs(last_shift - shift) > period / 2:
                if last_shift > shift:
                    rotations += 1
                else:
                    rotations -= 1
        last_shift = shift
        all_shifts.append(shift)
        all_shifts_summed.append(rotations * period + shift)

        # print(correlation)
        # print(brightness)
        #'''
        print(shift)
        axs[1].plot(correlation)
        # axs[1].scatter(period*phase,0)

        # axs[1].set_ylim((0,1))

        axs[0].imshow(img_roi, cmap="gray")
        
        plt.draw()
        plt.pause(0.001)
        plt.cla()
        axs[0].cla()
        axs[1].cla()

        # plt.imshow(img_copy)
        # plt.show()'''

        if show_img:
            # if diff==[]:
            t.SetData(img_copy)
            # else:
            #    t.SetData(diff)
            t2.SetData(roi_params.img_debug)

            t3.SetData(img_roi)
            vv.processEvents()

        while (time.time() - start_time < 0):
            if show_img:
                vv.processEvents()
            pass
    plt.ioff()
    fig, axs = plt.subplots(2)
    axs[0].plot(all_shifts)
    axs[1].plot(all_shifts_summed)
    plt.show()
