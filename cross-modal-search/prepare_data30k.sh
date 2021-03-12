wget http://www.cs.toronto.edu/~faghri/vsepp/data.tar
tar -xvf data.tar
rm -rf data.tar
rm -rf data/coco*
rm -rf data/f8k*
rm -rf data/*precomp*
rm -rf data/f30k/images
mv flickr-image-dataset data/f30k/images