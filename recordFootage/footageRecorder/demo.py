import math
import time

import imageio
import numpy as np
from matplotlib import pyplot as plt


import linearEncoder as le
import shiftDetectorRestoration as sdr
import shiftDetectorCorrelation as sdc
import roiExtractorCanny as rec
import threading

import sendSteps



mm_per_step= 92.5 / 2048
mm_per_period=12

steps_per_period=275



def mm_to_step(dist):
    return int(math.floor(dist / mm_per_step))


pos=[0]

run_thread=True # nicht schön, klasse wäre besser
def readPosLoop(lin_enc,pos):
    while run_thread:
        img=img_stream.get_next_image()
        if not img is None:
            p=lin_enc.get_next_shift(img)
            #print(p)

            with pos_lock:
                pos[0]=p
        else:
            break
pos_lock=threading.Lock()



def live_debug(fig,axs,num_show=100):
    shifts=detector.debug_plot_dict["All Shifts"][1]
    if isinstance(detector, sdr.ShiftDetectorRestoration):
        with detector.debug_lock:
            point = detector.debug_plot_dict["Maximum"][1]
            filt_img=detector.debug_img_dict["Restored Filter"][1]
        axs[0].cla()
        axs[1].cla()
        axs[0].imshow(filt_img, cmap="gray", vmin=0)
        axs[0].plot(point[0], point[1], "rx")
        l = len(shifts)
        axs[1].plot(shifts[l - min(num_show, l):l])

        plt.pause(0.01)
        plt.draw()


    else:
        with detector.debug_lock:
            base_brightness = detector.debug_plot_dict["Base Brightness Curve"][1]
            brightness = detector.debug_plot_dict["Brightness Curve"][1]
            correlation_raw = detector.debug_plot_dict["Correlation"][1]
            correlation = detector.debug_plot_dict["Correlation Clipped"][1]
            shift = detector.debug_plot_dict["Shift"][1]
            img_roi = detector.debug_img_dict["Image Raw"][1]
            img_roi_filtered = detector.debug_img_dict["Image Filtered"][1]
        fig.tight_layout()
        axs[0].cla()
        axs[1].cla()
        axs[2].cla()
        axs[3].cla()
        axs[4].cla()


        axs[2].plot(brightness,label="Signal")
        axs[2].plot(base_brightness,label="Referenz Signal")
        axs[2].legend(loc="upper right")

        axs[3].plot(correlation_raw,label="Korrelation roh")
        axs[3].plot(correlation,label="Korrelation geclippt")
        axs[3].legend(loc="upper right")
        axs[3].plot(shift, correlation_raw[shift], "rx")

        axs[3].set_xlim(0, len(base_brightness))
        axs[3].set_xlabel("Pixel")

        axs[0].imshow(img_roi, cmap="gray")
        axs[1].imshow(img_roi_filtered, cmap="gray")

        l = len(shifts)
        axs[4].plot(shifts[l - min(num_show, l):l],label="Verschiebung gesammelt")

        axs[4].legend(loc="upper right")
        axs[4].set_xlabel("Frames")
        axs[4].set_ylabel("Perioden")

        plt.draw()
        plt.pause(0.01)
        # plt.pause(1)


do_show_debug=False

if __name__=="__main__":


    #iio_reader=imageio.get_reader("<video0>")
    iio_reader=imageio.get_reader("./data/motor_test_2/motor_test_2.mp4")
    img_stream=le.IIOImageStream(iio_reader)


    extractor=rec.RoiExtractorCanny(debug_draw=do_show_debug)

    #detector=sdr.ShiftDetectorRestoration(debug_draw=True)
    detector=sdc.ShiftDetectorCorrelation(debug_draw=True)

    detector.beta=10000

    sendSteps.do_cardinal(-1, -1, 500)
    lin_enc=le.LinearEncoder(extractor,detector,img_stream,extraction_mode="dynamic")

    sendSteps.do_cardinal(1, 1, 500)



    #debuganzeigen für initialisierung
    if do_show_debug:
        print(extractor.debug_img_dict.items())
        for name, item in sorted(extractor.debug_img_dict.items(), key=lambda x: x[1][0]):
            print(name,item[0])
            plt.title(name)
            plt.imshow(item[1],cmap="gray")
            plt.show()


        for name,item in sorted(detector.debug_img_dict.items(),key=lambda x:x[1][0]):

            print(name,item[0])
            plt.title(name)
            plt.imshow(item[1],cmap="gray")
            plt.show()

        for name,item in sorted(detector.debug_plot_dict.items(),key=lambda x:x[1][0]):

            print(name,item[0])
            plt.title(name)
            plt.plot(item[1])
            plt.show()




    do_show_only=True

    do_correct=False
    do_measure=False
    do_live=False
    do_experiment=False

    num_show=100

    if do_show_only:
        plt.ion()
        shifts=[]
        detector.do_debug_draw=True

        if isinstance(detector,sdr.ShiftDetectorRestoration):
            fig,axs=plt.subplots(2)
        else:
            fig,axs=plt.subplots(5)
            axs[0].get_shared_x_axes().join(axs[0],axs[3])
            axs[0].get_shared_x_axes().join(axs[0],axs[2])


        while True:
            img = img_stream.get_next_image()
            if not img is None:
                p = lin_enc.get_next_shift(img)
                shifts.append(p)
                print(p)
                live_debug(fig,axs)
            else:
                break
        plt.ioff()
        plt.clf()
        plt.plot(shifts)
        plt.show()

    if do_correct:
        t = threading.Thread(target=readPosLoop, args=(lin_enc, pos))
        t.start()
        sendSteps.set_speed(2000)
        if isinstance(detector, sdr.ShiftDetectorRestoration):
            fig, axs = plt.subplots(2)
        else:
            fig, axs = plt.subplots(5)
        time.sleep(0.5)

        while True:
            with pos_lock:
                current_pos=pos[0]
            print(current_pos)
            if abs(current_pos)>0.01:
                #num=mm_to_step(current_pos*mm_per_period)
                num=int(steps_per_period*current_pos)
                dir=0 if num ==0 else math.copysign(1,num)
                print("moving",dir,num)
                sendSteps.do_cardinal(dir,dir,abs(num))

                time.sleep(1)
            live_debug(fig,axs,2000)

    if do_measure:


        t = threading.Thread(target=readPosLoop, args=(lin_enc, pos),daemon=True)
        t.start()
        sendSteps.set_speed(2000)
        time.sleep(1)
        with pos_lock:
            p1=pos[0]
        dist=2048
        sendSteps.do_cardinal(-1,-1,dist)
        time.sleep(1)
        with pos_lock:
            p2=pos[0]
        print("Steps per Period",dist/(p2-p1))

    if do_live:
        t = threading.Thread(target=readPosLoop, args=(lin_enc, pos))
        t.start()
        # sendSteps.set_speed(2000)
        if isinstance(detector, sdr.ShiftDetectorRestoration):
            fig, axs = plt.subplots(2)
        else:
            fig, axs = plt.subplots(5)
        time.sleep(1)
        while True:
            with pos_lock:
                current_pos = pos[0]
            print(current_pos)
            live_debug(fig, axs, 2000)
    if do_experiment:
        def move_to_zero(current_pos):
            num=int(steps_per_period*current_pos)
            dir=0 if num ==0 else math.copysign(1,num)
            print("moving",dir,num)
            sendSteps.do_cardinal(dir,dir,abs(num))

        def do_cycle(cycle):
            for c in cycle:
                num=int(steps_per_period*c)
                dir=0 if num ==0 else math.copysign(1,num)
                sendSteps.do_cardinal(dir,dir,abs(num))
                time.sleep(1)


        t = threading.Thread(target=readPosLoop, args=(lin_enc, pos),daemon=True)
        t.start()
        sendSteps.set_speed(600)
        if isinstance(detector, sdr.ShiftDetectorRestoration):
            fig, axs = plt.subplots(2)
        else:
            fig, axs = plt.subplots(5)


        print("ready")
        time.sleep(10)
        with pos_lock:
            current_pos=pos[0]
            print(current_pos)
        lin_enc.set_zero()
        time.sleep(1)
        with pos_lock:
            current_pos=pos[0]
            print(current_pos)
        print("starting")



        num_cycles=1
        cycle=[.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,-5]

        distances_measured=[]
        distances_measured_after_correction=[]

        plt.ion()
        for i in range(num_cycles):
            do_cycle(cycle)
            time.sleep(2)
            with pos_lock:
                current_pos=pos[0]
            print(current_pos)
            distances_measured.append(current_pos)
                #num=mm_to_step(current_pos*mm_per_period)
            move_to_zero(current_pos)
            time.sleep(0.5)
            with pos_lock:
                current_pos=pos[0]
            distances_measured_after_correction.append(current_pos)

            live_debug(fig,axs,2000)
        print("done")
        plt.ioff()
        run_thread=False
        plt.clf()

        plt.plot(detector.debug_plot_dict["All Shifts"][1])
        plt.xlabel("Frames")
        plt.ylabel("Perioden")
        plt.show()
        print(threading.enumerate())
        np.savetxt("measured.csv",np.asarray(distances_measured),delimiter=",")
        np.savetxt("measured_cor.csv",np.asarray(distances_measured_after_correction),delimiter=",")
