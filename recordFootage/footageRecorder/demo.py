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
    iio_reader=imageio.get_reader("./data/motor_test_3/motor_test_3.mp4")
    img_stream=le.IIOImageStream(iio_reader)


    extractor=rec.RoiExtractorCanny(debug_draw=do_show_debug)

    #detector=sdr.ShiftDetectorRestoration(debug_draw=do_show_debug)
    detector=sdc.ShiftDetectorCorrelation(debug_draw=do_show_debug)

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



    if do_show_only:
        plt.ion()
        shifts=[]
        detector.do_debug_draw=True
        while True:
            img = img_stream.get_next_image()
            if not img is None:
                p = lin_enc.get_next_shift(img)
                shifts.append(p)
                print(p)

                if type(extractor)==sdr.ShiftDetectorRestoration:
                    plt.cla()
                    plt.imshow(detector.debug_img_dict["Restored Filter"][1],cmap="gray",vmin=0)
                    point=detector.debug_plot_dict["Maximum"][1]
                    plt.plot(point[0],point[1],"rx")
                    plt.pause(0.01)
                    plt.draw()


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
