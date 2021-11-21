
import imageio
import visvis as vv
import skimage.filters
import skimage.color
reader = imageio.get_reader('<video0>')
t = vv.imshow(reader.get_next_data(), clim=(0, 1))
for im in reader:

    #grey=skimage.color.rgb2gray(im)
    grey=im[:,:,0]/255.0
    blur=skimage.filters.gaussian(grey,20)
    img=blur-grey
    thresh=skimage.filters.threshold_otsu(img)
    img=img>0.03
    #print(grey)
    vv.processEvents()
    t.SetData(img)


