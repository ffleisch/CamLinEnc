from abc import ABC, abstractmethod


class ShiftDetector(ABC):


    @abstractmethod
    def set_base_image(self,base_image):
        pass

    @abstractmethod
    def find_shift(self, img_roi):
        pass
