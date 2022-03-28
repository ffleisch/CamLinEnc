import threading
from abc import ABC, abstractmethod


#an abstrat base class as an interface for detecting shifts in an image
class ShiftDetector(ABC):

    def __init__(self,do_debug_draw):
        self.do_debug_draw=do_debug_draw
        self.debug_img_dict={}
        self.debug_plot_dict={}
        self.debug_lock=threading.Lock()

    @abstractmethod
    def set_base_image(self, base_image_roi):
        pass

    @abstractmethod
    def find_shift(self, img_roi):
        pass
