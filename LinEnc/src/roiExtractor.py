from abc import ABC, abstractmethod





class RoiExtractor(ABC):

    def __init__(self,debug_draw):

        self.debug_draw = debug_draw
        self.debug_dict={}


        pass




    @abstractmethod
    def findRoiParameters(self,image):
        pass


    @abstractmethod
    def extractRoi(self,image):
        pass