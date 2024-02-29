# OptoDMD

Control DMD device for patterned 1P optogenetics stimulation

# Installation

## Windows

### install Arduino IDE

### Install Ximea

### Use zeromq with matlab

## Ubuntu

### LabJack USB driver

```
git clone https://github.com/labjack/exodriver.git
cd exodriver/
sudo ./install.sh   
```

### install Arduino IDE

Install AppImage from arduino's website (Ubuntu package is outdated)

### Install Ximea

```
wget https://www.ximea.com/downloads/recent/XIMEA_Linux_SP.tgz
tar xzf XIMEA_Linux_SP.tgz
cd package
./install -pcie
cp -r api/Python/v3/ximea ~/miniconda3/envs/OptoDMD/lib/python3.8/site-packages/
```

### Use zeromq with matlab

```
sudo apt install maven openjdk-8-jdk-headless
git clone https://github.com/zeromq/jeromq.git
git checkout tags/v0.6.0
cd jeromq
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/ mvn clean install -DskipTests
```

# Load Firmata Sketch on the Arduino

The sketch is available in the Arduino IDE’s built-in examples. To open it, access the File menu, then Examples, followed by Firmata, and finally StandardFirmata.
1. Plug the USB cable into the PC.  
2. Select the appropriate board and port on the IDE.  
3. Press Upload.  

Then copy target/jeromq-0.6.0.jar to the project root.