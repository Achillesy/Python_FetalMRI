import pydicom
import SimpleITK as sitk

# filepath = './Patient_7626622/_jdeng__0215031641'
# data = pydicom.dcmread(filepath + '/ser012img00001.dcm')
# print(data.data_element)

def readdcm(filepath):
    series_id = sitk.ImageSeriesReader.GetGDCMSeriesIDs(filepath)
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(filepath, series_id[0])
    series_reader = sitk.ImageSeriesReader() #读取数据端口
    series_reader.SetFileNames(series_file_names)  #读取名称
    images = series_reader.Execute()#读取数据
    #print(images.GetSpacing())
    #sitk.WriteImage(images, "T2_1.nii.gz")#保存为nii
    return images

if __name__ == '__main__':
    filepath = './Patient_8586291/_jdeng__0215032152'
    dcm_images = readdcm(filepath)   #读取文件
    sitk.WriteImage(dcm_images, "Patient_8586291_152.nii.gz") #保存为nii
