


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

mm_per_cycle=56/5

measured_corr_before=pd.read_csv("measured_cor_before.csv", header=None).to_numpy()*mm_per_cycle
measured_corr_after=pd.read_csv("measured_cor.csv", header=None).to_numpy()*mm_per_cycle
measured_no_corr=pd.read_csv("measured_no_corr.csv", header=None).to_numpy()*mm_per_cycle

plt.plot(measured_corr_before,label="Gemessen nach Bewegungszyklus")
plt.plot(measured_corr_after,label="Gemessen nach Korrektur")
plt.plot(measured_no_corr,label="Ohne Korrektur")
plt.grid(True, axis='y')
plt.ylabel("mm")
plt.xlabel("Zyklen")
plt.legend(loc="upper left")
plt.show()




