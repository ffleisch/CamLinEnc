import math
import time

import imageio
from matplotlib import pyplot as plt


import linearEncoder as le
import shiftDetectorRestoration as sdr
import shiftDetectorCorrelation as sdc
import roiExtractorCanny as rec
import threading

import sendSteps



mm_per_step= 92.5 / 2048
mm_per_period=6




def mm_to_step(dist):
    return int(math.floor(dist / mm_per_step))


pos=[0]

def readPosLoop(lin_enc,pos):
    while True:
        img=img_stream.get_next_image()
        if not img is None:
            p=lin_enc.get_next_shift(img)
            #print(p)

            with pos_lock:
                pos[0]=p
        else:
            break

pos_lock=threading.Lock()





do_show_debug=True

if __name__=="__main__":


    #iio_reader=imageio.get_reader("<video0>")
    iio_reader=imageio.get_reader("./data/motor_test_8/motor_test_8.mp4")
    img_stream=le.IIOImageStream(iio_reader)


    extractor=rec.RoiExtractorCanny(debug_draw=do_show_debug)

    detector=sdr.ShiftDetectorRestoration(debug_draw=do_show_debug)
    #detector=sdc.ShiftDetectorCorrelation(debug_draw=do_show_debug)

    detector.beta=100000

    lin_enc=le.LinearEncoder(extractor,detector,img_stream,extraction_mode="dynamic")




    #debuganzeigen für initialisierung
    if do_show_debug:
        print(extractor.debug_img_dict.items())
        for name, item in sorted(extractor.debug_img_dict.items(), key=lambda x: x[1][0]):
            print(name,item[0])
            plt.title(name)
            plt.imshow(item[1])
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





    do_correct=False
    do_measure=False
    do_show_only=True

    num_show=100

    if do_show_only:
        plt.ion()
        shifts=[]
        detector.do_debug_draw=True

        if isinstance(detector,sdr.ShiftDetectorRestoration):
            fig,axs=plt.subplots(2)
        else:
            fig,axs=plt.subplots(5)


        while True:
            img = img_stream.get_next_image()
            if not img is None:
                p = lin_enc.get_next_shift(img)
                shifts.append(p)
                print(p)

                if isinstance(detector,sdr.ShiftDetectorRestoration):
                    axs[0].cla()
                    axs[1].cla()
                    axs[0].imshow(detector.debug_img_dict["Restored Filter"][1],cmap="gray",vmin=0)
                    point=detector.debug_plot_dict["Maximum"][1]
                    axs[0].plot(point[0],point[1],"rx")
                    l=len(shifts)
                    axs[1].plot(shifts[l-min(num_show,l):l])

                    plt.pause(0.01)
                    plt.draw()


                else:
                    base_brightness=detector.debug_plot_dict["Base Brightness Curve"][1]
                    brightness=detector.debug_plot_dict["Brightness Curve"][1]
                    correlation_raw=detector.debug_plot_dict["Correlation"][1]
                    correlation=detector.debug_plot_dict["Correlation Clipped"][1]
                    shift=detector.debug_plot_dict["Shift"][1]
                    img_roi=detector.debug_img_dict["Image Raw"][1]
                    img_roi_filtered=detector.debug_img_dict["Image Filtered"][1]

                    axs[0].cla()
                    axs[1].cla()
                    axs[2].cla()
                    axs[3].cla()
                    axs[4].cla()

                    axs[2].plot(brightness)
                    axs[2].plot(base_brightness)
                    axs[3].plot(correlation_raw)
                    axs[3].plot(shift,correlation_raw[shift],"rx")

                    axs[3].set_xlim(0,len(base_brightness))

                    axs[0].imshow(img_roi, cmap="gray")
                    axs[1].imshow(img_roi_filtered, cmap="gray")

                    l = len(shifts)
                    axs[4].plot(shifts[l - min(num_show, l):l])

                    plt.draw()
                    plt.pause(0.01)
                    #plt.pause(1)
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

        while True:
            with pos_lock:
                current_pos=pos[0]
            print(current_pos)
            if abs(current_pos)>0.01:
                num=mm_to_step(current_pos*mm_per_period)

                dir=0 if num ==0 else -math.copysign(1,num)
                print("moving",dir,num)
                sendSteps.do_cardinal(dir,dir,abs(num))
                time.sleep(1)


    if do_measure:

        t = threading.Thread(target=readPosLoop, args=(lin_enc, pos))
        t.start()
        sendSteps.set_speed(2000)

        with pos_lock:
            p1=pos[0]
        dist=2048
        sendSteps.do_cardinal(dist,dist,1)
        time.sleep(1)
        with pos_lock:
            p2=pos[0]
        print("Periods per Step",dist/(p2-p1))
