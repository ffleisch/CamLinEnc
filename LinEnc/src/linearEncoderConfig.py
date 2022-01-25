import numpy as np


class LinearEncoderConfig():
    """
    Default configuration for the linear encoder.

    """

    def __init__(self):
        # LinearEncoder parameters
        # path of the input video file
        self.footage = "./recordFootage/footageRecorder/data/motor_test_6/motor_test_6.mp4"
        # can be either 'static' or 'dynamic'
        self.mode = "dynamic"
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

        # filter canny edges into thick line to later exctract width
        self.cannyEdgesFilterMask = np.zeros((70, 70))
        # added to the denominator for calculating the points of the lines
        self.pointBaseAdd = 2
        # added to the denominator for calculating the points of the lines
        self.pointBaseFactor = 1000
        # color of the line 
        self.lineColor = 1
        # thickness of the line 
        self.lineThickness = 10
        # offset for calculating the intersection (x coordinate)
        self.intersectionOffsetX = 0
        # offset for calculating the intersection (y coordinate)        
        self.intersectionOffsetY = 0 

        # (debug mode) circle radius for finding the rope with
        self.RoiCenterCircleRadius = 2
        # (debug mode) circle thickness for finding the rope with
        self.RoiCenterCircleThickness = 2
        # (debug mode) circle color for finding the rope with
        self.RoiCenterCircleColor = (0, 255, 255)

        # (debug mode) circle radius for finding the rope with
        self.findRopeWidthCircleRadius = 2
        # (debug mode) circle thickness for finding the rope with
        self.findRopeWidthCircleThickness = 2
        # (debug mode) circle color for finding the rope with
        self.findRopeWidthCircleColor = (0, 255, 255)

        # multiplier for calculating the length of the roi window 
        self.RoiLengthMultiplier = 0.5
        # multiplier for calculating the width of the roi window 
        self.RoiWidthMultiplier = 1.5


        # ShiftDetectorRestoration
        # beta for shift detector restoration
        self.ShiftDetectorRestorationBeta = 1000
        # Create an image of a given size with the edges fading to 0
        # Multiplying by it allows to eliminate edge effects created during the IFFT
        # How many percent of the width too fade out
        self.ShiftDetectorRestorationPercentWidthFadeout = 0.3
        # How many percent of the length too fade out 
        self.ShiftDetectorRestorationPercentLengthFadeout = 0
        # factor for calculation the base image
        self.ShiftDetectorRestorationBaseImageMultiplier = 2
        # applying gaussina filtering to slice (interval upper bound) 
        self.ShiftDetectorRestorationBaseImageGaussianFilterMultiplierUpper = 0.03
        # applying gaussina filtering to slice (interval lower bound)
        self.ShiftDetectorRestorationBaseImageGaussianFilterMultiplierLower  = 0.01


        #ShiftDetectorCovariance
        # sigma for gaussian ShiftDetectorRestoration image blur
        self.ShiftDetectorRestorationPrepRoiSigma1 = 5
        # sigma for gaussian ShiftDetectorRestoration image roi flat blur
        self.ShiftDetectorRestorationPrepRoiSigma2 = 30
        # window length of the result of the correlation
        self.ShiftDetectorRestorationWindow = 2
        # correlation mode
        self.ShiftDetectorRestorationCorrelationMode = "valid"
        #
        self.ShiftDetectorRestorationCorrelationBound = 2