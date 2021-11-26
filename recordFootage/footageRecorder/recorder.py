import imageio
import shutil
import visvis as vv
import skimage.io
import os
import time





reader = imageio.get_reader('<video0>')


save_name="testvideo.mp4"
save_folder="data"

img_save_folder=os.path.join(os.path.abspath(os.curdir),save_folder,os.path.splitext(save_name)[0])
mm_per_step=86/4096

min_frame_rate = 30




if __name__=="__main__":
    #ordner vorberteiten um bilder zu speichern
    if not os.path.exists(img_save_folder):
        os.mkdir(img_save_folder)
    else:
        shutil.rmtree(img_save_folder)
        os.mkdir(img_save_folder)




    last_time=1

    #bilder aus der kamera lesen
    for frame_num,im in enumerate(reader):

        start_time=time.time()
        print("taken:",1/last_time)
        #vv.processEvents()
        #t.SetData(im)

        skimage.io.imsave(os.path.join(img_save_folder,"frame_%07d"%(frame_num))+".jpg",im,plugin="pil")
        while(time.time()-start_time<1/min_frame_rate):
            pass
        last_time=time.time()-start_time
        if frame_num>100:
            break



    #aus den gespeicherten bildern video machen
    print("done,saving video")
    fileList = []
    for file in os.listdir(img_save_folder):
        if file.startswith("frame_"):
            complete_path = os.path.join(img_save_folder , file)
            fileList.append(complete_path)

    writer = imageio.get_writer(os.path.join(os.path.abspath(os.curdir),save_folder,save_name), fps=min_frame_rate)

    for im in fileList:
        writer.append_data(imageio.imread(im))
    writer.close()

