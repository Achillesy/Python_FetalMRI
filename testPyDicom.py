import pydicom
import matplotlib.pyplot as plt

filepath = './Patient_7626622/_jdeng__0215031641'
ds = pydicom.dcmread(filepath + '/ser012img00001.dcm')
plt.figure(figsize=(10,10))
plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
plt.show()
