#!/bin/sh

DATA_DIR=/tmp/jina/celeb/
mkdir -p ${DATA_DIR}
cd ${DATA_DIR}


#Download Celeb with only name starting with A
wget http://vis-www.cs.umass.edu/lfw/lfw-a.tgz
tar zxf lfw-a.tgz

#Uncomment below to download entire LFW Dataset
#wget http://vis-www.cs.umass.edu/lfw/lfw.tgz
#tar zxf lfw.tgz


# You can download the checkpoint files directly
# from here and upload it in FaceNetTorchEncoder.py if link isn't working

#MODEL_DIR=facenet
#mkdir ${MODEL_DIR}
#cd $MODEL_DIR
#wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1TDZVEBudGaEd5POR5X4ZsMvdsh1h68T1' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1TDZVEBudGaEd5POR5X4ZsMvdsh1h68T1" -O pretrained.pt && rm -rf /tmp/cookies.txt
#cd ..

