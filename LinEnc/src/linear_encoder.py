import os

import cv2

import roiExtractorCanny
import shiftDetectorCovariance
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
        return self.stream.get_next_data()


class LinearEncoder:

    '''def __init__(self):
        self.extractor=None
        self.detector=None'''


    def __init__(self,extractor,detector,image_stream):
        self.extractor=extractor
        self.detector=detector

        base_img=self.find_roi_static(image_stream)
        base_img_roi=self.extractor.extractRoi(base_img)

        self.detector.set_base_image(self.preprocess(base_img_roi))


    def preprocess(self,img):
        return img[:,:,0]

    def find_roi_static(self,image_stream):
        while True:
            img=image_stream.get_next_image()
            if img is None:
                raise ValueError("No Image given")
            res=self.extractor.findRoiParameters(img)
            if res:
                return img

    def find_roi_dynamic(self,image_stream):
        img_last=image_stream.get_next_image()
        while True:
            img=image_stream.get_next_image()
            if not img:
                raise ValueError("No Image given")

            diff_img=img_last-img
            res=self.extractor.findRoiParameters(diff_img)
            if res:
                return img
            img_last=img

    def get_next_shift(self,image):
        roi=self.extractor.extractRoi(self.preprocess(image))
        return self.detector.find_shift(roi)



    def initalize(self):

        pass



if __name__=="__main__":

    path = "../../recordFootage/footageRecorder/data"
    test_name = "motor_test_1"

    video_path = os.path.abspath(os.path.join(path, test_name, test_name + ".mp4"))
    print(video_path)

    reader = imageio.get_reader(video_path)
    my_stream=IIOImageStream(reader)

    extr=roiExtractorCanny.RoiExtractorCanny()
    detec=shiftDetectorCovariance.ShiftDetectorCovariance()

    lin_enc=LinearEncoder(extr,detec,my_stream)



    shifts=[]
    for img in reader:
        d=lin_enc.get_next_shift(img)
        print(d)
        shifts.append(d)


    plt.plot(shifts)
    plt.show()



