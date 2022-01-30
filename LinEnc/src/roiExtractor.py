from abc import ABC, abstractmethod





class RoiExtractor(ABC):

    def __init__(self):
        pass




    @abstractmethod
    def findRoiParameters(self,image):
        pass


    @abstractmethod
    def extractRoi(self,image):
        pass