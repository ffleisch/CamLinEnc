import math
import os
import time

import imageio

import visvis as vv
import numpy as np
import cv2


from matplotlib import pyplot as plt




def plot_line(img,rho,theta,col):
    a = math.cos(theta)
    b = math.sin(theta)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 10000 * (-b)), int(y0 + 10000 * (a)))
    pt2 = (int(x0 - 10000 * (-b)), int(y0 - 10000 * (a)))
    cv2.line(img, pt1, pt2, col, 1, cv2.LINE_AA)


if __name__=="__main__":



    path="../recordFootage/footageRecorder/data"
    test_name="motor_test_6"

    video_path=os.path.abspath(os.path.join(path,test_name,test_name+".mp4"))
    print(video_path)


    reader=imageio.get_reader(video_path)
    img0=reader.get_next_data()


    a1 = vv.subplot(131);
    a2 = vv.subplot(132);
    a3 = vv.subplot(133);
    t = vv.imshow(img0,axes=a1)
    t2 = vv.imshow(img0.copy(),axes=a2)
    t3 = vv.imshow(img0.copy(),axes=a3)
    #img_last=[]
    #diff=[]
    for frame in reader:
        start_time=time.time()

        img_copy=frame.copy()
        img=frame[:,:,0]
        img_copy=cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

        #if not img_last==[]:
        #    diff=cv2.absdiff(img_last,img_copy)
        #img_last=img_copy.copy()


        canny=cv2.Canny(img,70,150,None,3)


        #kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        #kernel_close=cv2.getStructuringElement(cv2.MORPH_CLOSE,(3,3))


        #canny=cv2.dilate(canny,kernel)

        #canny=cv2.morphologyEx(canny,kernel_close)


        lines = cv2.HoughLines(canny, 2, np.pi / 180, 150, None, 0, 0)




        #draw lines to show



        avg_theta=0

        if lines is not None:

            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                plot_line(img_copy,rho,theta,(0,0,255))

            avg_rho = np.average(lines[:, 0, 0])
            avg_theta = np.average(lines[:, 0, 1])

            print(avg_rho, avg_theta)
            plot_line(img_copy, avg_rho, avg_theta, (255, 0, 0))




        #print(frame)
        #plt.imshow(dft)
        #plt.show()
        #img_copy+=cv2.cvtColor(canny,cv2.COLOR_GRAY2RGB)


        #filter canny edges into width

        filter=np.zeros((70,70))

        dx=-math.sin(avg_theta)
        dy=math.cos(avg_theta)
        p1=(int(filter.shape[1]/2+dx*1000),int(filter.shape[0]/2+dy*1000))
        p2=(int(filter.shape[1]/2-dx*1000),int(filter.shape[0]/2-dy*1000))

        cv2.line(filter, p1, p2, 1, 10, cv2.LINE_AA)

        #plt.imshow(filter)
        #plt.show()


        canny_filtered=cv2.filter2D(canny,ddepth=-1,kernel=filter)



        #img_copy=cv2.morphologyEx(img_copy,kernel_close)

        #plt.imshow(img_copy)
        #plt.show()

        #if diff==[]:
        t.SetData(img_copy)
        #else:
        #    t.SetData(diff)
        t2.SetData(canny)

        t3.SetData(canny_filtered)
        vv.processEvents()


        while(time.time()-start_time<0):
            vv.processEvents()
