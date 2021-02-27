import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pylab as plt
import nibabel as nib
from nibabel import nifti1
from nibabel.viewers import OrthoSlicer3D

example_filename = 'Patient_7626622_827_seg.nii.gz' # 文件路径

img = nib.load(example_filename)
# print(img)
# print(img.header['db_name'])  # 输出头信息

width, height, queue = img.dataobj.shape
print(img.dataobj.shape)

OrthoSlicer3D(img.dataobj).show()

# num = 1
# for i in range(0, queue, 10):
#     img_arr = img.dataobj[:, :, i]
#     plt.subplot(5, 4, num)
#     plt.imshow(img_arr, cmap='gray')
#     num += 1

# plt.show()
