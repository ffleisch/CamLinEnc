# Overview
For this particular project, we constructed a linear encoder utilizing a webcam. Our objective is to precisely determine the position of a periodically marked rope, enabling closed-loop control. To achieve this, we employed the shift detection algorithm detailed in the paper titled [Shift Detection by Restoration](https://ieeexplore.ieee.org/abstract/document/797613?casa_token=6_OHe42YE9MAAAAA:ip5czK3rR5_7s-aKzd5sjOF56L6gWtHyA4jIVFEIpxuSViKlaqPCrII5cJMrLCwvyXgdndIZE8E).

The initial step involves extracting the video region containing the rope and capturing a reference frame. Now we can periodically measure the shift to this reference frame. Phase unwrapping allows us to keep track of the cumulative shift. A comprehensive overview of this project is presented in our paper, which can be accessed [here](dokumentation/AWP_Abschlussbericht.pdf).

# Possible Usecase
When trying to build a V-Plotter with stepper motors and simple rope pulleys, I encountered the problem that the rope kept loosing its positions slowly over time. I suspected this is not due to slip but due dynamic loads stretching the rope different amounts in fornt of and after the driving pulley.
Instead of using a more expensive toothed belt or a beaded chain, this project keeps track of absolute position of the rope with a computer vision method.

With this the error of the simple pulley drive can be measured an compensated for. A single camera can keep trrack of multiple drives in it field of view.
