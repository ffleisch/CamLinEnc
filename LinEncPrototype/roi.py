import cv2
import math
import numpy as np


def plot_line(img, rho, theta, col):
    a = math.cos(theta)
    b = math.sin(theta)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 10000 * (-b)), int(y0 + 10000 * (a)))
    pt2 = (int(x0 - 10000 * (-b)), int(y0 - 10000 * (a)))
    cv2.line(img, pt1, pt2, col, 1, cv2.LINE_AA)


class RoiParams:
    def __init__(self, rho, theta, midpoint, edge_points, size, img_debug=None):
        self.size = size
        self.midpoint = midpoint
        self.rho = rho
        self.edge_points = edge_points
        self.theta = theta
        self.img_debug = img_debug

        self.corner_upper_left = (int(midpoint[0] - size[0] / 2), int(midpoint[1] - size[1] / 2))
        self.corner_lower_right = (int(midpoint[0] + size[0] / 2), int(midpoint[1] + size[1] / 2))

        self.rotation_matrix = cv2.getRotationMatrix2D(midpoint, (theta - math.pi / 2) * (180 / math.pi), 1)


def find_roi_parameters(img, debug=False):
    found_params = False
    size = None
    midpoint = None

    img_debug = None

    if debug:
        img_debug = img.copy()

    canny = cv2.Canny(img, 70, 150, None, 3)

    lines = cv2.HoughLines(canny, 2, np.pi / 180, 150, None, 0, 0)

    # draw lines to show
    # compute average theta and rho
    # this line represents the rope
    avg_theta = 0
    avg_rho = 0
    if lines is not None:
        avg_rho = np.average(lines[:, 0, 0])
        avg_theta = np.average(lines[:, 0, 1])

        if debug:
            for i in range(0, len(lines)):
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                plot_line(img_debug, rho, theta, (0, 0, 255))

            print(avg_rho, avg_theta)

            plot_line(img_debug, avg_rho, avg_theta, (255, 0, 0))

    # filter canny edges into thick line to later exctract width
    filter = np.zeros((70, 70))

    dx = -math.sin(avg_theta)
    dy = math.cos(avg_theta)
    p1 = (int(filter.shape[1] / 2 + dx * 1000), int(filter.shape[0] / 2 + dy * 1000))
    p2 = (int(filter.shape[1] / 2 - dx * 1000), int(filter.shape[0] / 2 - dy * 1000))

    if debug:
        cv2.line(filter, p1, p2, 1, 10, cv2.LINE_AA)

    # plt.imshow(filter)
    # plt.show()

    canny_filtered = cv2.filter2D(canny, ddepth=-1, kernel=filter)

    # return the intersection points of a line shifted by offset with the coordinate axes
    def line_intersction(rho, theta, off_x=0, off_y=0):
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

    # find the intersections of the rope with the edge of the image
    width = canny_filtered.shape[1]
    height = canny_filtered.shape[0]

    top, left = line_intersction(avg_rho, avg_theta, 0, 0)
    bottom, right = line_intersction(avg_rho, avg_theta, width, height)

    points = []

    if 0 <= top < width:
        points.append((int(top), 0))

    if 0 <= right < height:
        points.append((width, int(right)))
    if 0 < bottom <= width:
        points.append((int(bottom), height))
    if 0 < left <= height:
        points.append((0, int(left)))

    if debug:
        print(len(points), points)
        for p in points:
            cv2.circle(img_debug, p, 10, (0, 255, 0), 3)

    # finde den mittelpunkt der linie zwischen den schnittpunkten mit dem bildrand
    # find the midpoint of between the edge intersections
    # represents the middle of the visible rope
    # after that extract the roi

    if len(points) == 2:
        midpoint = (int((points[0][0] + points[1][0]) / 2), int((points[0][1] + points[1][1]) / 2))

        if debug:
            cv2.circle(img_debug, midpoint, 10, (255, 255, 0), 3)

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
                    if debug:
                        cv2.circle(img_debug, (xi, yi), 2, (0, 255, 255), 2)
                        cv2.circle(img_debug, (xo, yo), 2, (0, 255, 255), 2)
                        print(i)
                    found_params = True
                    break
            except IndexError:
                print("could not determine width of rope")
                break
            i += 1

        rope_len = np.linalg.norm(points[0], points[1])
        size = (rope_len / 2, i * 2)

    if found_params:
        params = RoiParams(avg_rho, avg_theta, midpoint, points, size, img_debug)
        return params
    else:
        return None

def extract_roi(img,params):



    size_rotation = (img.shape[1], img.shape[0])
    img_roi = cv2.warpAffine(img, params.rotation_matrix, dsize=size_rotation)


    # crop the image
    img_roi = img_roi[params.corner_upper_left[0]:params.corner_lower_right[0],
              params.corner_upper_left[1]:params.corner_lower_right[1]]


    return img_roi