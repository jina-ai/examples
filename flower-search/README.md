# Build an Image Search System in 3 minutes

In this demo, we use the 17flowers data from [http://www.robots.ox.ac.uk/~vgg/data/flowers/17/](http://www.robots.ox.ac.uk/~vgg/data/flowers/17/) to build a flower image search system so that one can find similar images. Make sure you have gone through our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and understood the [take-home-message](https://github.com/jina-ai/examples/tree/master/urbandict-search#wrap-up) in [our bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search) before moving on. 

  

## Contents

[TOC]


## Overview

The overall design is similar to the semantic search demo. We consider each image as a Document and generate Chunks by moving a slidding window on the image. The pretrained `mobilenet_v2` model from the `torchvision` lib is used to encode the Chunks into vectors. 

In this demo, we will show how to run the Pods in the dockers and how to scale up the Pods to boost the whole procedure. Plus, you will learn how to define your own Executor in your project. Sounds interesting? Let's start coding!

<p align="center">
  <img src=".github/flower.gif?raw=true" alt="Jina banner" width="90%">
</p>

## Prerequirements

This demo requires Python 3.7.

```bash
pip install -r requirements.txt
```


## Prepare the data
In total, there are 1360 images in 17 categories in the [17flowers](http://www.robots.ox.ac.uk/~vgg/data/flowers/17/) dataset. The following script will download the data and uncompress it into `/tmp/jina/flower/jpg`.

```bash
cd flower-search
bash ./get_data.sh
```

## Define the Flows

We start with defining the index and the query Flows  with the YAML files as following. If you found a bit confusing with the YAML files, we highly suggest to go through our [bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search) before moving forward.

<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> </td>
<td> YAML</td>
<td> Dashboard </td>

</tr>
<tr>
<td> Index Flow </td>
<td>
  <sub>

```yaml
!Flow
with:
  prefetch: 10
pods:
  loader:
    yaml_path: yaml/craft-load.yml
  normalizer:
    yaml_path: yaml/craft-normalize.yml
    read_only: true
  encoder:
    image: jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2
    replicas: 4
    timeout_ready: 60000
  chunk_indexer:
    yaml_path: yaml/index-chunk.yml
  doc_indexer:
    yaml_path: yaml/index-doc.yml
    needs: loader
  join_all:
    yaml_path: _merge
    needs: [doc_indexer, chunk_indexer]
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/index-flow.png"/>
</td>
</tr>
<tr>
<td> Query Flow </td>
<td>
  <sub>

```yaml
!Flow
with:
  read_only: true
pods:
  loader:
    yaml_path: yaml/craft-load.yml
  normalizer:
    yaml_path: yaml/craft-normalize.yml
  encoder:
    image: jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2
    timeout_ready: 60000
  chunk_indexer:
    yaml_path: yaml/index-chunk.yml
  ranker:
    yaml_path: BiMatchRanker
  doc_indexer:
    yaml_path: yaml/index-doc.yml
```

</sub>

</td>
<td>
<img align="right" height="420px" src=".github/query-flow.png"/>
</td>

</tr>
</table>

As the same as in the [bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search), we define a two pathway Flow for indexing. The 
### Scale up

## Run the Flows

## Add a Customized Executor


