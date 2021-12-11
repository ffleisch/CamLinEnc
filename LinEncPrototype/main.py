import math
import os
import time

import imageio

import visvis as vv
import numpy as np
import cv2


from matplotlib import pyplot as plt




if __name__=="__main__":



    path="../recordFootage/footageRecorder/data"
    test_name="motor_test_5"

    video_path=os.path.abspath(os.path.join(path,test_name,test_name+".mp4"))
    print(video_path)


    reader=imageio.get_reader(video_path)
    img0=reader.get_next_data()


    a1 = vv.subplot(121);
    a2 = vv.subplot(122);
    t = vv.imshow(img0,axes=a1)
    t2 = vv.imshow(img0.copy(),axes=a2)
    for frame in reader:
        start_time=time.time()

        img_copy=frame.copy()
        img=frame[:,:,0]
        img_copy=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        canny=cv2.Canny(img,70,150,None,3)


        #kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        #kernel_close=cv2.getStructuringElement(cv2.MORPH_CLOSE,(3,3))


        #canny=cv2.dilate(canny,kernel)

        #canny=cv2.morphologyEx(canny,kernel_close)


        lines = cv2.HoughLines(canny, 1, np.pi / 180, 150, None, 0, 0)






        if lines is not None:
            #print(lines)

            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho
                pt1 = (int(x0 + 10000 * (-b)), int(y0 + 10000 * (a)))
                pt2 = (int(x0 - 10000 * (-b)), int(y0 - 10000 * (a)))
                cv2.line(img_copy, pt1, pt2, (0, 0, 255), 1, cv2.LINE_AA)

            avg_rho = np.average(lines[:, 0, 0])
            avg_theta = np.average(lines[:, 0, 1])

            print(avg_rho, avg_theta)
            a = math.cos(avg_theta)
            b = math.sin(avg_theta)
            x0 = a * avg_rho
            y0 = b * avg_rho
            pt1 = (int(x0 + 10000 * (-b)), int(y0 + 10000 * (a)))
            pt2 = (int(x0 - 10000 * (-b)), int(y0 - 10000 * (a)))
            cv2.line(img_copy, pt1, pt2, (0, 255, 0), 1, cv2.LINE_AA)




        #print(frame)
        #plt.imshow(dft)
        #plt.show()
        #img_copy+=cv2.cvtColor(canny,cv2.COLOR_GRAY2RGB)

        t.SetData(img_copy)
        t2.SetData(canny)
        vv.processEvents()


        while(time.time()-start_time<0):
            vv.processEvents()
