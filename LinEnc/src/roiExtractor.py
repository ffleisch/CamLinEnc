from abc import ABC, abstractmethod

from fontTools import configLogger





class RoiExtractor(ABC):

    def __init__(self, config):
        self.config = config




    @abstractmethod
    def findRoiParameters(self,image):
        pass


    @abstractmethod
    def extractRoi(self,image):
        pass