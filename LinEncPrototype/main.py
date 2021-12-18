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



def find_roi_parameters(img):



    return

def extract_roi(params):




    return




if __name__=="__main__":



    path="../recordFootage/footageRecorder/data"
    test_name="motor_test_5"

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

        img_roi=img_copy.copy()

        canny=cv2.Canny(img,70,150,None,3)

        lines = cv2.HoughLines(canny, 2, np.pi / 180, 150, None, 0, 0)




        #draw lines to show
        #compute average theta and rho
        #this line represents the rope
        avg_theta=0
        avg_rho=0
        if lines is not None:

            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                plot_line(img_copy,rho,theta,(0,0,255))

            avg_rho = np.average(lines[:, 0, 0])
            avg_theta = np.average(lines[:, 0, 1])

            print(avg_rho, avg_theta)
            plot_line(img_copy, avg_rho, avg_theta, (255, 0, 0))



        #filter canny edges into thick line to later exctract width
        filter=np.zeros((70,70))

        dx=-math.sin(avg_theta)
        dy=math.cos(avg_theta)
        p1=(int(filter.shape[1]/2+dx*1000),int(filter.shape[0]/2+dy*1000))
        p2=(int(filter.shape[1]/2-dx*1000),int(filter.shape[0]/2-dy*1000))

        cv2.line(filter, p1, p2, 1, 10, cv2.LINE_AA)

        #plt.imshow(filter)
        #plt.show()

        canny_filtered=cv2.filter2D(canny,ddepth=-1,kernel=filter)



        #give the intersection points of a line shifted by offset with the coordinate axes
        def line_intersction(rho,theta,off_x=0,off_y=0):
            dx = -math.sin(theta)
            dy = math.cos(theta)

            sx=dy*rho-off_x
            sy=-dx*rho-off_y

            #cv2.circle(img_copy,(int(sx),int(sy)),5,(255,0,255),4)

            #cv2.circle(img_copy,(int(sx+10*dx),int(sy+10*dy)),5,(0,255,255),4)

            x_0=float("inf")
            y_0=float("inf")

            if dy!=0:
                x_0=sx-(dx*sy)/dy

            if dx!=0:
                y_0=sy-(dy*sx)/dx

            #print(dx,dy,sx,sy,x_0,y_0)
            return (x_0+off_x,y_0+off_y)



        # find the intersections of the rope with the edge of the image
        width=canny_filtered.shape[1]
        height=canny_filtered.shape[0]

        top,left=line_intersction(avg_rho,avg_theta,0,0)
        bottom,right=line_intersction(avg_rho,avg_theta,width,height)

        points=[]

        if 0<=top <width:
            points.append((int(top),0))

        if 0<=right <height:
            points.append((width,int(right)))
        if 0<bottom <=width:
            points.append((int(bottom),height))
        if 0<left <=height:
            points.append((0,int(left)))

        print(len(points),points)
        for p in points:
            cv2.circle(img_copy, p, 10, (0, 255, 0), 3)



        #finde den mittelpunkt der linie zwischen den schnittpunkten mit dem bildrand
        #find the midpoint of between the edge intersections
        #represents the middle of the visible rope
        #after that extract the roi
        if len(points)==2:
            midpoint=(int((points[0][0]+points[1][0])/2),int((points[0][1]+points[1][1])/2))

            cv2.circle(img_copy, midpoint, 10, (255, 255, 0), 3)


            dy = math.sin(avg_theta)
            dx = math.cos(avg_theta)


            #find the width of the rope by sampling outwards from the midpoint in the filtered canny edge image, until it finds black on btoh sides
            i=0
            while True:
                xi=int(midpoint[0]-i*dx)
                xo=int(midpoint[0]+i*dx)

                yi=int(midpoint[1]-i*dy)
                yo=int(midpoint[1]+i*dy)
                if canny_filtered[yi][xi]==0 and canny_filtered[yo][xo]==0:
                    cv2.circle(img_copy,(xi,yi),2,(0,255,255),2)
                    cv2.circle(img_copy,(xo,yo),2,(0,255,255),2)
                    print(i)
                    break

                i+=1


            #rotate the image, such that the rope is horizontal
            rotationmatrix=cv2.getRotationMatrix2D(midpoint,(avg_theta-math.pi/2)*(180/math.pi),1)

            size_tf=(img_roi.shape[1],img_roi.shape[0])
            img_roi=cv2.warpAffine(img_roi,rotationmatrix,dsize=size_tf)


            cv2.circle(img_roi, midpoint, 10, (255, 255, 0), 3)


            #crop it to size
            size=(int(width/3),int(2*i))



            #crop the image
            corner_upper_left=(int(midpoint[0]-size[0]/2),int(midpoint[1]-size[1]/2))
            img_roi=img_roi[corner_upper_left[1]:corner_upper_left[1]+size[1],corner_upper_left[0]:corner_upper_left[0]+size[0]]


            '''dx = -math.sin(avg_theta)
            dy = math.cos(avg_theta)

            sx=dy*avg_rho
            sy=-dx*avg_rho

            rho2=np.sqrt(pow(sx-midpoint[0],2)+pow(sy-midpoint[1],2))
            theta2=avg_theta-math.pi/2
            plot_line(img_copy,rho2,theta2,(0,255,255))'''

        '''p1=(int(inner[0]),0)
        p2=(0,int(inner[1]))
        p3=(int(outer[0]),canny_filtered.shape[0])
        p4=(canny_filtered.shape[1],int(outer[1]))

        #p1=(100,0)
        #print(p1,p2,p3,p4)
        print(p1,p2)

        cv2.circle(img_copy,p1,10,(255,0,0),3)
        cv2.circle(img_copy,p2,10,(0,255,0),3)
        cv2.circle(img_copy,p3,10,(0,0,255),3)
        cv2.circle(img_copy,p4,10,(255,255,0),3)'''


        #img_copy=cv2.morphologyEx(img_copy,kernel_close)

        #plt.imshow(img_copy)
        #plt.show()

        #if diff==[]:
        t.SetData(img_copy)
        #else:
        #    t.SetData(diff)
        t2.SetData(canny)

        t3.SetData(img_roi)
        vv.processEvents()


        while(time.time()-start_time<0):
            vv.processEvents()
