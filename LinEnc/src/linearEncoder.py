import os

import cv2

import roiExtractorCanny
import shiftDetectorCorrelation
import shiftDetectorRestoration
from abc import ABC, abstractmethod
import imageio
from matplotlib import pyplot as plt

class ImageStream(ABC):
    @abstractmethod
    def get_next_image(self):
        pass

class IIOImageStream(ImageStream):

    def __init__(self,stream):
        self.stream=stream

    def get_next_image(self):
        try:
            return self.stream.get_next_data()
        except IndexError:
            return None

class LinearEncoder:



    def __init__(self, extractor, detector, image_stream, extraction_mode="static"):
        """

        :param extractor: a roiExtractor instance to crop the ROI from the input image
        :param detector: a shift Detector to calculate and compound the shift from,
         subsequent given images

        :param extraction_mode: determine the roi from an image alone "static" or
         the difference between two subsequent ones "dynamic"

        :param image_stream: a stream of images to initalize the roiExtractor and
         get the base image for the detector from
        """
        self.extractor=extractor
        self.detector=detector
        self.extraction_mode=extraction_mode

        if extraction_mode=="dynamic":
            base_img=self.find_roi_dynamic(image_stream)
        else:
            if extraction_mode =="static":
                base_img=self.find_roi_static(image_stream)
            else:
                raise ValueError("Not a valid extraction mode")
        base_img_roi=self.extractor.extractRoi(base_img)

        #plt.imshow(base_img_roi)
        #plt.show()
        self.detector.set_base_image(self.preprocess(base_img_roi))
        self.zero_shift=0
        self.shift=0

    def preprocess(self,img):
        """
        Do preprocessing on all Images given i.e. RGB to Greyscale
        :param img:
        :return:
        """

        #the current algorithm needs a single color channel
        #with the red and blue pattern in our test footage it is adventageous
        #to use only the red channel

        #return cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
        return img[:,:,0]


    #find the roi by using the image directly
    def find_roi_static(self, image_stream):
        """
        Find the Roi using the images directly
        Background has to be very flat
        Stops if parameters are found or stream runs out
        :param image_stream:
        :return:
        """
        while True:
            img=image_stream.get_next_image()
            if img is None:
                raise ValueError("No Image given")
            res=self.extractor.findRoiParameters(img)
            if res:
                return img


    #Todo reject bad diff images
    #

    def find_roi_dynamic(self, image_stream):
        """
        Find the Roi using the difference of two subsequent images
        Needs movement in between the images to work
        Stops if parameters are found or stream runs out
        :param image_stream:
        :return:
        """
        img_last=image_stream.get_next_image()
        while True:
            img=image_stream.get_next_image()
            if img is None:
                raise ValueError("No Image given")

            diff_img=cv2.absdiff(img_last,img)
            res=self.extractor.findRoiParameters(2*diff_img)
            if res:
                return img
            img_last=img

    def get_next_shift(self,image):
        """
        Process a single input image
        :param image: Input image
        :return: The total shift in pixels relative to the base image
        """
        roi=self.extractor.extractRoi(self.preprocess(image))
        self.shift=self.detector.find_shift(roi)-self.zero_shift
        return self.shift

    def set_zero(self):
        """
        set the current shift as zero
        """
        self.zero_shift=self.shift




#some testing of the class
if __name__=="__main__":

    path = "./recordFootage/footageRecorder/data"
    test_name = "motor_test_6"

    video_path = os.path.abspath(os.path.join(path, test_name, test_name + ".mp4"))
    print(video_path)

    reader = imageio.get_reader(video_path)
    my_stream=IIOImageStream(reader)

    extr=roiExtractorCanny.RoiExtractorCanny()
    #detec=shiftDetectorCovariance.ShiftDetectorCovariance()
    detec=shiftDetectorRestoration.ShiftDetectorRestoration()

    lin_enc=LinearEncoder(extr, detec, my_stream, "dynamic")


    plt.ion()
    shifts=[]
    for img in reader:
        d=lin_enc.get_next_shift(img)
        #print(d)
        shifts.append(d)

    plt.ioff()
    plt.clf()
    plt.plot(shifts)
    plt.show()


