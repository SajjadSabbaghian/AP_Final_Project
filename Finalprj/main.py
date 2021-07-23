import sys
import os
import random
import numpy as np
import matplotlib.image as mpimg
from pathlib import Path
from PIL import Image, ImageFilter,ImageOps, ImageEnhance
import imageio
import time
from datetime import datetime
import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5 import QtGui
from  PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from skimage import io
import skimage


Form = uic.loadUiType(os.path.join(os.getcwd() , "prj.ui"))[0]

class IntroWindow(QMainWindow , Form ):
    def __init__(self):
        super(IntroWindow , self).__init__()
        self.setupUi(self)
        self.foldername = None
        self.filenames = None
        self.images_directory = None
        self.val = None

    
        self.open_file.clicked.connect(self.FileDialog)
        self.open_folder.clicked.connect(self.FolderDialog)
        self.Pre_Execute.clicked.connect(self.Resize_image)
        self.Aug_Execute.clicked.connect(self.choose)
        #Dtermine slider  and spin for Rotation,Brightness and Noise
        self.AngleSlider.valueChanged.connect(self.updateAngleSpin)
        self.AngleSpinbox.valueChanged.connect(self.updateAngleSlider)
        self.PercentSlider.valueChanged.connect(self.updateBrPercentSpin)
        self.BrPercentSpin.valueChanged.connect(self.updatePercentSlider)
        self.VarianceSlider.valueChanged.connect(self.updateVarianceSpin)
        self.VarianceSpin.valueChanged.connect(self.updateVarianceSlider)
        #set Progressbar zero to then update them
        self.Pbar1.setValue(0)
        self.Pbar2.setValue(0)

    #This is the slot of Aug_Execute
    def choose(self):
        if(self.images_directory==None):
            self.Error()
            return
        self.stop()
        self.val = self.Combochoose.currentText()
        if(self.val == "Flip"):
            self.Flip_image()
        elif(self.val == "Crop"):
            self.Crop_image()
        elif(self.val == "Rotation"):
            self.Rotation_image()
        elif(self.val == "Brightness"):
            self.Brightness_image()
        elif(self.val == "Noise"):
            self.Noise_image()
        self.start()
    #These are the udate function for change slider and spin simultaneously
    def updateAngleSpin(self , value):
        self.AngleSpinbox.setValue(value)
    def updateAngleSlider(self,value):
        self.AngleSlider.setValue(value)

    def updateBrPercentSpin(self , value):
        self.BrPercentSpin.setValue(value/20)
    def updatePercentSlider(self,value):
        self.PercentSlider.setValue(value*20)

    def updateVarianceSpin(self , value):
        self.VarianceSpin.setValue(value/10)
    def updateVarianceSlider(self,value):
        self.VarianceSlider.setValue(value*10)

    #Get error when folder not choose
    def Error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText('Please choose files or folder')
        msg.setWindowTitle("Error")
        msg.exec_()

    #This is the slot for reading images in file
    def FileDialog(self):
        self.images_directory = QFileDialog.getOpenFileNames(self,'open file',filter="Image Files (*.png *.jpg *.bmp)")
        self.images_directory = self.images_directory[0]
        path = Path(self.images_directory[-1]).parent.absolute()
        self.file_Edit.setText(str(path))
    #This is slot for reading image in folder
    def FolderDialog(self):
        self.foldername = QFileDialog.getExistingDirectory(self,"Select Folder","./")
        self.folder_Edit.setText(self.foldername)
        self.images_directory = self.filter_format(self.foldername)

    ####--------- slots for each acion ---------###
    def Resize_image(self):
        if(self.images_directory==None):
            self.Error()
            return
        self.stop()
        height = self.Resize_Height.value()
        width = self.Resize_Width.value()
        self.resize_image(self.images_directory,int(height),int(width))
        self.start()
    def Flip_image(self):
        self.flip_image(self.images_directory ,self.Horizontal_check.isChecked(),self.Vertical_check.isChecked())

    def Crop_image(self):
        self.crop(self.images_directory,
                  self.PositionXpx.value(),
                  self.PositionYpx.value(),
                  self.Widthpx.value(),
                  self.Heightpx.value())
                  
    def Rotation_image(self):
        self.rotate(self.images_directory,
                    self.AngleSpinbox.value(),
                    self.BackgroundComboBox.currentText(), 
                    self.DirectioncomboBox.currentText())
    def Brightness_image(self):
        self.brightness(self.images_directory, self.BrPercentSpin.value())
    def Noise_image(self):
        self.add_noise(self.images_directory,self.VarianceSpin.value(),self.ModeCombo.currentText())

    #This function for reading images in folderpath
    def filter_format(self,directory):
        self.stop()
        self.images_directory = []            # make a list to hold path of images
        format_list = ['jpg', 'png']     # filter files by formats
        for root, dirs, files in os.walk(directory, topdown=False):
           for i in files:
                for j in format_list:
                    if i[-len(j) - 1:] == "." + j:
                        self.images_directory.append(root + '\\' + i)           # append path of files with jpg and png format
        self.start()
        return self.images_directory

    def rotate(self,dataset, degree, backgroundcolor, direction='Clockwise'):
        num = 0     # define variable num to prevent making duplicate directory
        while True:
            num += 1
            try:
                os.mkdir(os.getcwd() + '/rotated' + str(degree) + "(" + str(num) + ")")    # making directory with meaningful name
                break
            except:
                continue
        if direction == 'Clockwise':
            # default direction of rotate function is anticlockwise so if we want clockwise , must change to symmetry
            real_degree = -1 * degree    
        else:
            real_degree = degree
        for i in range(0, len(dataset)):
            image_set = Image.open(dataset[i])
            rotated3 = image_set.rotate(real_degree, fillcolor=backgroundcolor, expand=True)
            # save with meaningful name
            rotated3.save(os.getcwd() + '/rotated' + str(degree) + "(" + str(num) + ")/" + str(i) + '.png')
            #Update Progressbar in each epoch    
            self.Pbar2.setValue(int(i/len(dataset))*100)
        self.Pbar2.setValue(100)

    def resize_image(self,dataset, height, width):
        if(height==0 or width==0):
            return
        num = 0    # define variable num to prevent making duplicate directory
        while True:
            num += 1
            try:
                # making directory with meaningful name
                os.mkdir(os.getcwd() + "/resize(" + str(num) + ")")
                break
            except:
                continue
        for i in range(1, len(dataset)):
            image_set = Image.open(dataset[i])
            resized = image_set.resize((width, height))
            # save with meaningful name
            resized.save(os.getcwd() + "/resize(" + str(num) + ")/" + str(i) + '.png')
            #Update Progressbar in each epoch   
            self.Pbar1.setValue(int((i/len(dataset))*100))
        self.Pbar1.setValue(100)

    def flip_image(self,dataset, vertical, horizental):
        if(vertical==0 and horizental==0):
            return
        if vertical or horizental:
            num = 0   # define variable num to prevent making duplicate directory
            while True:
                num += 1
                try:
                    # making directory with meaningful name
                    os.mkdir(os.getcwd() + "/fliped(" + str(num) + ")")
                    break
                except:
                    continue

            for i in range(0, len(dataset)):
                image_set = Image.open(dataset[i])
                if vertical:
                    fliped = ImageOps.flip(image_set)
                    # save with meaningful name , use str(i)*2 to prevent making duplicate name
                    fliped.save(os.getcwd() + "/fliped(" + str(num) + ")/" + str(i) * 2 + '.png')
                if horizental:
                    fliped = ImageOps.mirror(image_set)
                     # save with meaningful name
                    fliped.save(os.getcwd() + "/fliped(" + str(num) + ")/" + str(i) + '.png')
                #Update Progressbar in each epoch   
                self.Pbar2.setValue(int((i/len(dataset))*100))
        self.Pbar2.setValue(100)

    def crop(self,dataset, left, top, width, height):
        if(width==0 or height==0):
            return
        # define variable num to prevent making duplicate directory
        num = 0
        while True:
            num += 1
            try:
                # making directory with meaningful name
                os.mkdir(os.getcwd() + "/crop(" + str(num) + ")")
                break
            except:
                continue
        for i in range(0, len(dataset)):
            image_set = Image.open(dataset[i])
            right = left + width
            bottom = top + height
            if bottom < image_set.size[1] and right < image_set.size[0]:
                try:
                    cropped = image_set.crop((left, top, right, bottom))
                    # save with meaningful name
                    cropped.save(os.getcwd() + "/crop(" + str(num) + ")/" + str(i) + '.png')
                except:
                    continue
            #Update Progressbar in each epoch   
            self.Pbar2.setValue(int((i/len(dataset))*100))
        self.Pbar2.setValue(100)

    def brightness(self,dataset, percent):
        # define variable num to prevent making duplicate directory
        num = 0
        while True:
            num += 1
            try:
                # making directory with meaningful name
                os.mkdir(os.getcwd() + "/brightness(" + str(num) + ")")
                break
            except:
                continue

        for i in range(0, len(dataset)):
            image_set = Image.open(dataset[i])
            img_brightness_obj = ImageEnhance.Brightness(image_set)
            enhanced_img = img_brightness_obj.enhance(percent)
            # save with meaningful name
            enhanced_img.save(os.getcwd() + "/brightness(" + str(num) + ")/" + str(i) + '.png')
            #Update Progressbar in each epoch   
            self.Pbar2.setValue(int((i/len(dataset))*100))
        self.Pbar2.setValue(100)


    
   
    def add_noise(self,dataset, var,mode):
        num = 0
        while True:
            num += 1
            try:
                # making directory with meaningful name
                os.mkdir(os.getcwd() + "/noisy(" + str(num) + ")")
                break
            except:
                continue

        for i in range(0, len(dataset)):
            origin = io.imread(dataset[i])
            """var : float, optional
            Variance of random distribution. Used in 'gaussian' and 'speckle'.
            Note: variance = (standard deviation) ** 2. Default : 0.01 """
            noisy = skimage.util.random_noise(origin, mode=mode, var=var)
            # save with meaningful name
            imageio.imwrite(os.getcwd() + "/noisy(" + str(num) + ")/" + str(i) + '.png', noisy)  
            self.Pbar2.setValue(int((i/len(dataset))*100))
        self.Pbar2.setValue(100)
    

    def stop(self):
        self.Pre_Execute.setDisabled(True)
        self.Aug_Execute.setDisabled(True)
        self.open_file.setDisabled(True)
        self.open_folder.setDisabled(True)
    def start(self):
        self.Pre_Execute.setDisabled(False)
        self.Aug_Execute.setDisabled(False)
        self.open_file.setDisabled(False)
        self.open_folder.setDisabled(False)



if __name__ == "__main__":
    app  = QApplication(sys.argv)
    app.setStyle('Fusion')
    w = IntroWindow()
    w.show()
    sys.exit(app.exec_())