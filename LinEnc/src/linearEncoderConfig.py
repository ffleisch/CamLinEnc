import numpy as np


class Class LinearEncoderConfig():
    """
    Default configuration for the linear encoder.

    """

    def __init__(self):
        # LinearEncoder parameters
        # path of the input video file
        self.footage = "./recordFootage/footageRecorder/data/motor_test_6/motor_test_6.mp4"
        # can be either 'static' or 'dynamic'
        self.mode = "static"
        # can be  0,1,2 for the RGB channels of the colored image 
        self.image_color_channel = 0 
        # subtracting the shift for finding next shift in LinearEncoder
        self.zero_shift = 0
        # for resetting shift LinearEncoder
        self.shift = 0
        
        # RoiExtractor

        # RoiExtractorCanny parameters
        self.debug_draw = False
        # lower threshold value in hysteresis thresholding
        self.cannyLowerThreshold = 70
        # upper threshold value in hysteresis thresholding
        self.cannyUpperThreshold = 150
        # aperture size for the Sobel operator
        self.cannyApertureSize = 3
        # distance resolution of the accumulator in pixels
        self.HoughLinesRho = 2
        # angle resolution of the accumulator in radians
        self.HoughLinesTheta = np.pi / 180
        # accumulator threshold parameter so only those lines are returned that get more votes than 'threshold'
        self.HoughLinesThreshold = 150
        #
        self.HoughLinesLines = None 
        # multi-scale Hough transform, it is a divisor for the distance resolution rho
        self.HoughLinesSRN = 0
        #multi-scale Hough transform it is a divisor for the distance resolution theta
        # SRN = 0  and STN = 0 represents classical Hough transfromation
        self.HoughLinesSTN = 0





        


