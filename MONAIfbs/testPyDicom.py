import numpy as np
# import pydicom
import nibabel as nib
import matplotlib.pyplot as plt
import imageio

seg_file = '/home/achilles/Workspace/Python/FetalData/monaifbs_seg/000048_Normal000048/5_COR_160x89/seg/5_COR_160x89_seg.nii.gz'
seg_img = nib.load(seg_file)
seg_img_data = seg_img.get_fdata()

nii_file = '/home/achilles/Workspace/Python/FetalData/monaifbs_seg/000048_Normal000048/5_COR_160x89/nifti/5_COR_160x89.nii.gz'
nii_img = nib.load(nii_file)
nii_img_data = nii_img.get_fdata()

board = np.nonzero(seg_img_data)
(X, Y, Z, Tmp) = seg_img_data.shape
minX, maxX = min(board[0])-10, max(board[0])+10
minY, maxY = min(board[1])-10, max(board[1])+10
minZ, maxZ = min(board[2]), max(board[2])
if minX<0:
    minX = 0
if maxX>X:
    maxX = X
if minY<0:
    minY = 0
if maxY>Y:
    maxY = Y
seg_img_data[minX:maxX+1, minY:maxY+1, minZ:maxZ+1, :] = 1
a = [1,2,3,4]
print(a[0:4])

brain_img_data = nii_img_data * seg_img_data[:,:,:,0]
brain_slice = brain_img_data[:,:,4].T
brain_slice = brain_slice[::-1]
imageio.imwrite('4_COR_160x112_6.png', brain_slice)

# raw_file = '/mnt/Storage/Xuchu_Liu/orthanc/db-v6/7e/62/7e6221e8-8700-4afe-842b-89c0335da2ee'
# ds = pydicom.dcmread(raw_file)
# arr = ds.pixel_array
# arr[:,:] = brain_slice[:,:]
# ds.PixelData = arr.tobytes()
# plt.figure(figsize=(10,10))
# plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
# plt.show()
# ds.save_as("temp.dcm")
