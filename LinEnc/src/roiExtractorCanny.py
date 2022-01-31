import math

import cv2
import numpy as np

import roiExtractor as roiE


class RoiExtractorCanny(roiE.RoiExtractor):

    def __init__(self, debug_draw=False):
        super(RoiExtractorCanny, self).__init__(debug_draw)

        self.rope_len = 0
        self.size = 0
        self.rho = 0
        self.theta = 0
        self.midpoint = [0, 0]

        self.corner_upper_left = None
        self.corner_lower_right = None
        self.rotation_matrix = None

        self.found_params = False


    #plot a line using rho and theta coodinates
    def __plot_line(self, img, rho, theta, col):
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 10000 * (-b)), int(y0 + 10000 * (a)))
        pt2 = (int(x0 - 10000 * (-b)), int(y0 - 10000 * (a)))
        cv2.line(img, pt1, pt2, col, 1, cv2.LINE_AA)

    # return the intersection points of a line shifted by offset with the coordinate axes
    def __line_intersection(self, rho, theta, off_x=0, off_y=0):
        dx = -math.sin(theta)
        dy = math.cos(theta)

        sx = dy * rho - off_x
        sy = -dx * rho - off_y

        # cv2.circle(img_copy,(int(sx),int(sy)),5,(255,0,255),4)

        # cv2.circle(img_copy,(int(sx+10*dx),int(sy+10*dy)),5,(0,255,255),4)

        x_0 = float("inf")
        y_0 = float("inf")

        if dy != 0:
            x_0 = sx - (dx * sy) / dy

        if dx != 0:
            y_0 = sy - (dy * sx) / dx

        # print(dx,dy,sx,sy,x_0,y_0)
        return (x_0 + off_x, y_0 + off_y)

    def findRoiParameters(self, image):

        self.found_params = False

        if self.debug_draw:
            self.debug_dict["Raw Image"] = (0,image.copy())
            self.debug_dict["ROI Debug Markers"]=(5,image.copy())
            self.debug_dict["Hough Lines"]=(2,image.copy())

        canny = cv2.Canny(image, 70, 150, None, 3)

        lines = cv2.HoughLines(canny, 2, np.pi / 180, 150, None, 0, 0)



        if self.debug_draw:
            self.debug_dict["Canny Filter Result"]=(1,canny.copy())


        # draw lines to show
        # compute average theta and rho
        # this line represents the rope
        avg_theta = 0
        avg_rho = 0
        if lines is not None:
            avg_rho = np.average(lines[:, 0, 0])
            avg_theta = np.average(lines[:, 0, 1])

            if self.debug_draw:
                for i in range(0, len(lines)):
                    rho = lines[i][0][0]
                    theta = lines[i][0][1]
                    self.__plot_line(self.debug_dict["ROI Debug Markers"][1], rho, theta, (0, 0, 255))
                    self.__plot_line(self.debug_dict["Hough Lines"][1], rho, theta, (0, 0, 255))

                print(avg_rho, avg_theta)

                self.__plot_line(self.debug_dict["ROI Debug Markers"][1], avg_rho, avg_theta, (255, 0, 0))
                self.__plot_line(self.debug_dict["Hough Lines"][1], avg_rho, avg_theta, (255, 0, 0))

        # filter canny edges into thick line to later exctract width
        filter_mask = np.zeros((70, 70))

        dx = -math.sin(avg_theta)
        dy = math.cos(avg_theta)

        p1 = (int(filter_mask.shape[1] / 2 + dx * 1000), int(filter_mask.shape[0] / 2 + dy * 1000))
        p2 = (int(filter_mask.shape[1] / 2 - dx * 1000), int(filter_mask.shape[0] / 2 - dy * 1000))


        #draw the filter
        cv2.line(filter_mask, p1, p2, 1, 10, cv2.LINE_AA)

        # plt.imshow(filter)
        # plt.show()

        canny_filtered = cv2.filter2D(canny, ddepth=-1, kernel=filter_mask)


        if self.debug_draw:
            self.debug_dict["Canny Image Filtered"]=(4,canny_filtered.copy())
            self.debug_dict["Filter Mask"]=(3,filter_mask.copy())

        # find the intersections of the rope with the edge of the image
        width = canny_filtered.shape[1]
        height = canny_filtered.shape[0]

        top, left = self.__line_intersection(avg_rho, avg_theta, 0, 0)
        bottom, right = self.__line_intersection(avg_rho, avg_theta, width, height)

        points = []

        if 0 <= top < width:
            points.append((int(top), 0))

        if 0 <= right < height:
            points.append((width, int(right)))
        if 0 < bottom <= width:
            points.append((int(bottom), height))
        if 0 < left <= height:
            points.append((0, int(left)))

        if self.debug_draw:
            print(len(points), points)
            for p in points:
                cv2.circle(self.debug_dict["ROI Debug Markers"][1], p, 10, (0, 255, 0), 3)

        # finde den mittelpunkt der linie zwischen den schnittpunkten mit dem bildrand
        # find the midpoint of between the edge intersections
        # represents the middle of the visible rope
        # after that extract the roi

        if len(points) == 2:
            midpoint = (int((points[0][0] + points[1][0]) / 2), int((points[0][1] + points[1][1]) / 2))

            if self.debug_draw:
                cv2.circle(self.debug_dict["ROI Debug Markers"][1], midpoint, 10, (255, 255, 0), 3)

            dy = math.sin(avg_theta)
            dx = math.cos(avg_theta)

            # find the width of the rope by sampling outwards from the midpoint in the filtered canny edge image, until it finds black on btoh sides
            i = 0
            while True:
                xi = int(midpoint[0] - i * dx)
                xo = int(midpoint[0] + i * dx)

                yi = int(midpoint[1] - i * dy)
                yo = int(midpoint[1] + i * dy)
                try:
                    if canny_filtered[yi][xi] == 0 and canny_filtered[yo][xo] == 0:
                        if self.debug_draw:
                            cv2.circle(self.debug_dict["ROI Debug Markers"][1], (xi, yi), 2, (0, 255, 255), 2)
                            cv2.circle(self.debug_dict["ROI Debug Markers"][1], (xo, yo), 2, (0, 255, 255), 2)
                            print(i)
                        self.found_params = True
                        break
                except IndexError:
                    print("could not determine width of rope")
                    break
                i += 1

            if self.found_params:
                self.rope_len = np.sqrt(pow(points[0][0] - points[1][0], 2) + pow(points[0][1] - points[1][1], 2))

                self.size = (self.rope_len * 0.5, (i + 1) * 1.5)
                self.rho = avg_rho
                self.theta = avg_theta
                self.midpoint = midpoint
                self.corner_upper_left = (int(midpoint[0] - self.size[0] / 2), int(midpoint[1] - self.size[1] / 2))
                self.corner_lower_right = (int(midpoint[0] + self.size[0] / 2), int(midpoint[1] + self.size[1] / 2))

                self.rotation_matrix = cv2.getRotationMatrix2D(midpoint, (self.theta - math.pi / 2) * (180 / math.pi), 1)
        return self.found_params

    def extractRoi(self, image):

        if self.found_params:
            size_rotation = (image.shape[1], image.shape[0])
            img_roi = cv2.warpAffine(image, self.rotation_matrix, dsize=size_rotation)

            # crop the image
            img_roi = img_roi[self.corner_upper_left[1]:self.corner_lower_right[1],self.corner_upper_left[0]:self.corner_lower_right[0]]

            return img_roi
        else:
            raise ValueError("Parameters not set")
