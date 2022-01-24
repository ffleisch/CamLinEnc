from abc import ABC, abstractmethod


#an abstrat base class as an interface for detecting shifts in an image
class ShiftDetector(ABC):
    @abstractmethod
    def set_base_image(self, base_image_roi):
        pass

    @abstractmethod
    def find_shift(self, img_roi):
        pass
