import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from nibabel.affines import apply_affine
import numpy.linalg as npl

epi_img = nib.load('downloads/someones_epi.nii.gz')
epi_img_data = epi_img.get_fdata()
print(epi_img_data.shape)

def show_slices(slices):
    """ Fucntion to display row of image slices """
    fig, axes = plt.subplots(1, len(slices))
    for i, slice in enumerate(slices):
        axes[i].imshow(slice.T, cmap="gray", origin="lower")

def f(i, j, k):
    """ Return X, Y, Z coordinates for i, j, k """
    return M.dot([i, j, k]) + abc

slice_0 = epi_img_data[26, :, :]
slice_1 = epi_img_data[:, 30, :]
slice_2 = epi_img_data[:, :, 16]
show_slices([slice_0, slice_1, slice_2])
plt.suptitle("Center slices for EPI image")

anat_img = nib.load('downloads/someones_anatomy.nii.gz')
anat_img_data = anat_img.get_fdata()
anat_img_data.shape
show_slices([anat_img_data[28, :, :], \
    anat_img_data[:, 33, :], \
    anat_img_data[:, :, 28]])
plt.suptitle("Center slices for anatomical image")  

# plt.show()

# Set numpy to print 3 decimal points and suppress small values
np.set_printoptions(precision=3, suppress=True)
# Print the affine
print(epi_img.affine)

M = epi_img.affine[:3, :3]
abc = epi_img.affine[:3, 3]
epi_vox_center = (np.array(epi_img_data.shape) - 1) / 2.
print(f(epi_vox_center[0], epi_vox_center[1], epi_vox_center[2]))
print(epi_img.affine.dot(list(epi_vox_center) + [1]))
print(apply_affine(epi_img.affine, epi_vox_center))
epi_vox2anat_vox = npl.inv(anat_img.affine).dot(epi_img.affine)
print(apply_affine(epi_vox2anat_vox, epi_vox_center))
anat_vox_center = (np.array(anat_img_data.shape) - 1) / 2.
print(anat_vox_center)