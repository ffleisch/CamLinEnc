from abc import ABC, abstractmethod


class ShiftDetector(ABC):

    def __init__(self, baseImage):
        self.baseImage = baseImage

    @abstractmethod
    def findShift(self, img_roi):
        pass
