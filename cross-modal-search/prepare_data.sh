#!/bin/sh
unzip flickr8k.zip
rm flickr8k.zip
mv Images data/f8k/images
mv captions.txt data/f8k/captions.txt