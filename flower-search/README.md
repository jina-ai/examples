# Build an Image Search System in 3 minutes
<p align="center">
 
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg "We fully commit to open-source")](https://jina.ai)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-hello-world-badge.svg "Run Jina 'Hello, World!' without installing anything")](https://github.com/jina-ai/jina#jina-hello-world-)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/license-badge.svg "Jina is licensed under Apache-2.0")](#license)
[![Jina Docs](https://github.com/jina-ai/jina/blob/master/.github/badges/docs-badge.svg "Checkout our docs and learn Jina")](https://docs.jina.ai)
[![We are hiring](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-corp-badge-hiring.svg "We are hiring full-time position at Jina")](https://jobs.jina.ai)
<a href="https://twitter.com/intent/tweet?text=%F0%9F%91%8DCheck+out+Jina%3A+the+New+Open-Source+Solution+for+Neural+Information+Retrieval+%F0%9F%94%8D%40JinaAI_&url=https%3A%2F%2Fgithub.com%2Fjina-ai%2Fjina&hashtags=JinaSearch&original_referer=http%3A%2F%2Fgithub.com%2F&tw_p=tweetbutton" target="_blank">
  <img src="https://github.com/jina-ai/jina/blob/master/.github/badges/twitter-badge.svg"
       alt="tweet button" title="👍Share Jina with your friends on Twitter"></img>
</a>
[![Python 3.7 3.8](https://github.com/jina-ai/jina/blob/master/.github/badges/python-badge.svg "Jina supports Python 3.7 and above")](#)
[![Docker](https://github.com/jina-ai/jina/blob/master/.github/badges/docker-badge.svg "Jina is multi-arch ready, can run on differnt architectures")](https://hub.docker.com/r/jinaai/jina/tags)

</p>

In this demo, we use the 17flowers data from [http://www.robots.ox.ac.uk/~vgg/data/flowers/17/](http://www.robots.ox.ac.uk/~vgg/data/flowers/17/) to build a flower image search system so that one can find similar images. Make sure you have gone through our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and understood the [take-home-message](https://github.com/jina-ai/examples/tree/master/urbandict-search#wrap-up) in [our bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search) before moving on. 

  


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Cotents**

- [Overview](#overview)
- [Prerequirements](#prerequirements)
- [Prepare the data](#prepare-the-data)
- [Define the Flows](#define-the-flows)
- [Run the Flows](#run-the-flows)
- [Add a Customized Executor](#add-a-customized-executor)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Stay tuned](#stay-tuned)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->




## Overview

The overall design is similar to the semantic search demo. We consider each image as a Document and put the RGB array in the Chunk. Therefore, each Document has a single Chunk. The pretrained `mobilenet_v2` model from the `torchvision` lib is used to encode the Chunks into vectors. 

In this demo, we will show how to run the Pods in the docker container and how to scale up the Pods to boost the whole procedure. Plus, you will learn how to define your own Executor in your project. Sounds interesting? Let's start coding!

<p align="center">
  <img src=".github/flower.gif?raw=true" alt="Jina banner" width="90%">
</p>

<details>
<summary>Click here to see the query outputs</summary>

<p align="center">
  <img src=".github/query-demo.png?raw=true" alt="query flow console output">
</p>

</details> 

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
    yaml_path: MinRanker
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

Let's have a look at the index Flow. As the same as in the [bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search), we define a two pathway Flow for indexing. For each image, we put the image file name in the request message and thus each image is considered as a Document. The `loader` Pod reads the image file and save the image's RGB values into the Chunk. Note that in this case, we have only one Chunk for each Document. 

Afterwards, the Flow splits into two parallel pathways. In the pathway on the left side, the `normalizer` Pod resizes and normalizes the image in the Chunks so that in the downstreaming Pods they can be properly handled. Followed by the `chunk_indexer`, the `encoder` Pod encodes the Chunks into vectors, which will be further saved into the index by the `chunk_indexer` Pod. 

In the other pathway, the `doc_indexer` Pod uses the key-value storage to save the Document IDs and the Document contents, i.e. the image file names. At the end, the `join_all` Pod merges the results from the `chunk_indexer` and the `doc_indexer`. In this case, the `join_all` Pods simply wait for the both incoming messages arrived because neither of the upstreaming Pods write into the request message.

The two-pathway Flow, as a common practice in jina, is designed to storage the vectors and the Documents independently and in parallel. Of course, one can squeeze the two pathways into one pathway by concating the `doc_indexer` after the `chunk_indexer` and removing `join_all` Pod. However, this will slow down the index process. 

As for the query Flow, it is pretty much the same as the index Flow, and thereafter we won't be too verbose to iterate. You might have notice that there is something new in the YAML files. Let's dig into them!

### Hello, Docker!🐳
In the YAML file, we add the `encoder` Pod in a different way from the other Pods. Instead of using the YAML file to config the Pods, we define the `encoder` with a Docker image with the `image` argument. By doing this, we will have the `encoder` Pod running in a Docker container. This is one key feature of jina. By wrapping the Pods into the docker image, we can safely forget about the complicated dependency and environment setting that are required to run the Pods. 


```yaml
!Flow
pods:
  encoder:
    image: jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2
```

Back to our case, here we use the docker image containing the pretrained `mobilenet_v2` model from the `torchvision` lib. So that you do **NOT** need either to install the `torchvision` lib or to download the pretrained model. Everything is packed in the docker image. As long as you have docker installed, the container Pods will run out-of-box.

### Scale up 
Another new comer is the `replicas` argument. As its name implies, `replicas` defines the number of parallel Peas in the Pod running at the same time. This is a useful argument to scale up your service. In this demo, as the encoding procedure with the deep learning models are well-known to be slow, we set the `replicas` to 4 and will start 4 Peas to encode the Chunks in parallel. This will greatly speed up the indexing process.

```yaml
!Flow
pods:
  encoder:
    image: jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2
    replicas: 4
```

## Run the Flows
### Index 
Now we start indexing with the following command.
 
```bash
python app.py -t index
```

if you run into the following `TimeoutError`, the problem is probably because the docker image is too large to be downloaded in time. Please try `docker pull jinaai/hub.executors.encoders.image.torchvision-mobilenet_v2` to download the image in before running the Flow.

```bash 
TimeoutError: <class 'jina.peapods.container.ContainerPea'> with name encoder can not be initialized after 600000 ms
```

<details>
<summary>Click here to see the console output</summary>

<p align="center">
  <img src=".github/index-demo.png?raw=true" alt="index flow console output">
</p>

</details> 

Here we use the YAML file to define a Flow and use it to index the data. The `read_data()` function load the image file names in the format of `bytes`, which will be further wrapped in an `IndexRequest` and send to the Flow. 

```python
def read_data(img_path):
    fn_list = []
    for dirs, subdirs, files in os.walk(img_path):
        for f in files:
            fn = os.path.join(img_path, f)
            if fn.endswith('.jpg'):
                fn_list.append(fn)
    for fn in fn_list:
        yield fn.encode('utf8')
        
def main():
    data_path = os.path.join('/tmp/jina/flower/jpg')
    flow = Flow().load_config('flow-index.yml')
    with flow.build() as fl:
        fl.index(raw_bytes=read_data('/tmp/jina/flower/jpg'))
```

### Query

```bash
python app.py -t query
```

<details>
<summary>Click here to see the console output</summary>

<p align="center">
  <img src=".github/query-demo.png?raw=true" alt="query flow console output">
</p>

</details> 

For querying, we randomly sample 5 images from the dataset and feed them into the Flow using the following codes. 

```python
def read_data(img_path, max_sample_size=-1):
    if not os.path.exists(img_path):
        print('file not found: {}'.format(img_path))
    fn_list = []
    for dirs, subdirs, files in os.walk(img_path):
        for f in files:
            fn = os.path.join(img_path, f)
            if fn.endswith('.jpg'):
                fn_list.append(fn)
    if max_sample_size > 0:
        random.shuffle(fn_list)
        fn_list = fn_list[:max_sample_size]
    for fn in fn_list:
        yield fn.encode('utf8')

def main(task, num_docs, top_k):
    data_path = os.path.join('/tmp/jina/flower/jpg')
        flow = Flow().load_config('flow-query.yml')
        with flow.build() as fl:
            ppr = lambda x: save_topk(x, '/tmp/jina/flower/query_results.png')
            fl.search(read_data(data_path, 5), callback=ppr, top_k=top_k)
```

We use the callback function `save_topk` to save the query results into the `/tmp/jina/flower/query_results.png`. As expected, the Top-1 results are always the query images themself.

```python
def save_topk(resp, output_fn=None):
    results = []
    for d in resp.search.docs:
        d_fn = d.meta_info.decode()
        cur_result.append(d_fn)
        for idx, kk in enumerate(d.topk_results):
            score = kk.score.value
            if score <= 0.0:
                continue
            m_fn = kk.match_doc.raw_bytes.decode()
            cur_result.append(m_fn)
        results.append(cur_result)
    if output_fn is not None:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        top_k = max([len(r) for r in results])
        num_q = len(resp.search.docs)
        f, ax = plt.subplots(num_q, top_k, figsize=(8, 20))
        for q_idx, r in enumerate(results):
            for m_idx, img in enumerate(r):
                fname = os.path.split(img)[-1]
                fname = f'Query: {fname}' if m_idx == 0 else f'top_{m_idx}: {fname}'
                ax[q_idx][m_idx].imshow(mpimg.imread(img))
                ax[q_idx][m_idx].set_title(fname, fontsize=7)
        [aa.axis('off') for a in ax for aa in a]
        plt.tight_layout()
        plt.savefig(output_fn)
```

Congratulations! Now you have an image search engine working at hand. We won't go into details of the Pods' YAML files because they are quite self explained. If you feel a bit lost when reading the YAML files, please check out the [bert-based semantic search demo](https://github.com/jina-ai/examples/tree/master/urbandict-search#dive-into-the-pods).

## Add a Customized Executor
Although we have an image search engine at hand, we still have dozens of methods to make it better. One common method is to flip the images and index the flipped versions as well as the original image. So that we can retrieve the similar images even when the query image is flipped.

We starts with add a new Pod with the name of `flipper`, to the Flow. 

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
pods:
  loader:
    yaml_path: yaml/craft-load.yml
  flipper:
    yaml_path: yaml/craft-flip.yml
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
<img align="right" height="420px" src=".github/index-flow_2.png"/>
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
  flipper:
    yaml_path: yaml/craft-flip.yml
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
<img align="right" height="420px" src=".github/query-flow_2.png"/>
</td>

</tr>
</table>

As stated in the Flow's YAML file, the `flipper` Pod is configed by the `yaml/craft-flip.yml`. Now we create this YAML file as following. For the `flipper` Pod, we use the an Executor with the name `ImageFlipper`, which we will create in the next step. 

```yaml
!ImageFlipper
metas:
  py_modules: customized_executors.py
with:
  channel_axis: 0
requests:
  on:
    [SearchRequest, IndexRequest]:
      - !ChunkCraftDriver
        with:
          method: craft
```

In the YAML file, we define the Pod to behave in the same way on both `SearchRequest` and `IndexRequest`. In both cases, the Pod will use the `ChunkCraftDriver` to prepare the request data for the `ImageFlipper` and call the `craft()` function of the `ImageFlipper` to process the data.

> `ChunkCraftDriver` craft the chunk-level information on given keys using the executor.

The `py_modules` argument under the `metas` field is used to specify in which file the Executor is implemented. Therefore we can now move on to the `customized_executors.py` and implement `ImageFlipper`.

```yaml
!ImageFlipper
metas:
  py_modules: customized_executors.py
```

In this case, we need to inherit from the `ImageChunkCrafter` because we've saved the images in the Chunks of the requests.

> `ImageChunkCrafter` provides the basic functions for processing image data on chunk-level.

Here come codes. The `load_image()` function from the `ImageChunkCrafter` will load the image array and return an `PIL.Image` object. With the `PIL.Image` object, we can simply call the `mirror()` function to flip the images. Note we need to restore the color channel by calling the `restore_channel_axis()` function. This is because the `PIL.Image` always put the color channel at the last axis. In contrast, the input images might use different axis for the color channel, which is defined in the YAML file by the `channel_axis`.

```python
import numpy as np
from jina.executors.crafters.image import ImageChunkCrafter
from PIL import ImageOps


class ImageFlipper(ImageChunkCrafter):
    def craft(self, blob, doc_id, *args, **kwargs):
        raw_img = self.load_image(blob)
        _img = ImageOps.mirror(raw_img)
        img = self.restore_channel_axis(np.asarray(_img))
        return [{'doc_id': doc_id, 'blob': img.astype('float32')}, ]
```
  
Finally, our customized Executor is ready to go. Let's check the results. Interestingly, the top1 matched image is no longer always the query image itself. The flipped image in the Chunks somehow disturbs the retrieval process.

<details>
<summary>Click here to see the console output</summary>

<p align="center">
  <img src=".github/query-demo_2.png?raw=true" alt="query flow console output">
</p>

</details> 

## Wrap up
Hooray! Now you've a pretty simple follower image search engine working. Let's wrap up what we've covered in this demo.

1. The Pods can use the docker image and run in a docker container. 
2. The `replicas` argument allow you to quickly scale up the Pods.
3. The Pods can use user defined Executors.  

## Next Steps

- Write your own executors.
- Check out the docker images at the Jina hub.

## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/main.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/main.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Stay tuned

- [Slack chanel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company
- ![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social) - follow us and interact with us using hashtag `#JinaSearch`  
- [Join Us](mailto:hr@jina.ai) - want to work full-time with us at Jina? We are hiring!
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!



## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
