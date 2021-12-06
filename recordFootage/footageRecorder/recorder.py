import threading

import imageio
import shutil
import visvis as vv
import skimage.io
import os
import time


class Recorder:

    def __init__(self, save_name="testvideo", save_path="data", frame_rate=30, source="<video0>"):
        """
        A Class to record a video/ image sequence from a webcam/other osurce
        :param save_name:
        Name for the recording/folder to save the images to
        :param save_path:
        Path under which to create/replace a folder with the save_name for the results
        :param frame_rate:
        At what frajmerate are the images to be taken
        (limit of about 50 on my setup)
        :param source:
        What source to take the video from
        Look up imageio.get_reader(str) for more information
        """
        self.source=source
        self.save_name=os.path.splitext(save_name)[0]
        self.save_path = os.path.join(os.path.abspath(save_path), save_name)

        self.is_local_path=os.path.realpath(self.save_path).startswith(os.path.abspath(os.curdir))
        print(os.path.abspath(os.curdir))
        print(os.path.realpath(self.save_path))
        print(self.is_local_path)


        self.frame_rate = frame_rate


        self.recording=False
        self.do_stop=False
        self.my_thread=None


    def start_recording(self):
        self.my_thread=threading.Thread(target=self.record,daemon=True)

        self.my_thread.start()
        while self.recording==False:
            pass
        time.sleep(2)

    def record(self):
        # ordner vorbereiten um bilder zu speichern


        if self.is_local_path:
            if not os.path.exists(self.save_path):
                os.mkdir(self.save_path)
            else:
                shutil.rmtree(self.save_path)
                os.mkdir(self.save_path)
        else:
            raise Exception("Trying to create directory outside of local path. Are you sure about that? It may override some other folder.")

        # bilder aus der kamera lesen


        times=[]
        print("starting to record")
        #begin_time=time.time()
        interval=1/self.frame_rate
        print(interval)
        self.recording=True
        self.reader = imageio.get_reader(self.source)
        for frame_num, im in enumerate(self.reader):

            start_time = time.time()
            times.append(start_time)

            # vv.processEvents()
            # t.SetData(im)

            skimage.io.imsave(os.path.join(self.save_path, "frame_%07d" % (frame_num)) + ".jpg", im, plugin="pil")
            while (time.time() - start_time < 1.0 / self.frame_rate):
               pass
            #time.sleep(interval-(time.time()-begin_time)%interval)

            if self.do_stop:
                break
        self.recording=False
        '''print("stopping recording")
        print(times)
        for i,t in enumerate(times):
            print(times[i]-times[i-1])'''

        # aus den gespeicherten bildern video machen
        print("done,saving video")
        fileList = []
        for file in os.listdir(self.save_path):
            if file.startswith("frame_"):
                complete_path = os.path.join(self.save_path, file)
                fileList.append(complete_path)

        writer = imageio.get_writer(os.path.join( self.save_path, self.save_name+".mp4"),
                                    fps=self.frame_rate)

        for im in fileList:
            writer.append_data(imageio.imread(im))
        writer.close()


    def stop_recording(self):
        self.do_stop=True
        self.my_thread.join()

if __name__ == "__main__":
    testRecorder = Recorder(save_name="test3")

    testRecorder.start_recording()
    time.sleep(10)
    testRecorder.stop_recording()


    print("done")