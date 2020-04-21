# Build an Image Search System in 3 minutes

This demo build an image search system so that one can search similar images. We use the 17flowers data from [http://www.robots.ox.ac.uk/~vgg/data/flowers/17/](http://www.robots.ox.ac.uk/~vgg/data/flowers/17/). In total, there are 1360 images in 17 categories. We consider each image as a Document and generate Chunks by moving a slidding window on the image. If you are not familiar with these concepts, we highly suggest to go through our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and [Jina "Hello, World!"👋🌍](https://github.com/jina-ai/jina#jina-hello-world-) before moving forward. 

## Contents

[TOC]


## Overview

The overall design is similar to the semantic search demo. We use the pretrained `mobilenet_v2` model from the `torchvision` lib to encode the Chunks. In this demo, we will show how to run the Pods in the dockers and how to scale up the Pods to boost the indexing procedure. Furthermore, we will define a customized Executor.

<p align="center">
  <img src=".github/urbandict.gif?raw=true" alt="Jina banner" width="90%">
</p>

## Prerequirements

This demo requires Python 3.7.

```bash
pip install -r requirements.txt
```


## Prepare the data
The data will be saved at `/tmp/jina/flower/jpg`.

```bash
cd flower-search
bash ./get_data.sh
```

## Define the Flows
### define a Pod in Container

## Run the Flows


## Use a Customized Executor

## Use a Customized Driver


