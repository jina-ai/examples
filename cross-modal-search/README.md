<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Build a CrossModal Search System to look for Images from Captions and viceversa](#build-a-crossmodal-search-system-to-look-for-images-from-captions-and-viceversa)
  - [Prerequisites](#prerequisites)
  - [Prepare the data](#prepare-the-data)
  - [Build the docker images](#build-the-docker-images)
  - [Run the Flows](#run-the-flows)
  - [Results](#results)
  - [Documentation](#documentation)
  - [Community](#community)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Build a CrossModal Search System to look for Images from Captions and viceversa
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

In this example, `jina` is used to implement a Cross-modal search system. This example allows the user to search for images given a caption description and to look for a caption description given an image. We encode images and its captions (any descriptive text of the image) in separate indexes, which are later queried in a `cross-modal` fashion. It queries the `text index` using `image embeddings` and query the `image index` using `text embeddings`. 

**Motive behind Cross Modal Retrieval**

Cross-modal retrieval tries to effectively search for documents in a set of documents of a given modality by querying with documents from a different modality.

Modality is an attribute assigned to a document in Jina in the protobuf Document structure. It is possible that documents may be of the same mime type, but come from different distributions, for them to have different modalities. **Example**: In a an article or web page,  the body text and the title are from the same mime type (text), but can be considered of different modalities (distributions).

Different encoders map different modalities to a common embedding space. They need to extract semantic information from the documents. 

In this embedding space, documents that are semantically relevant to each other from different modalities are expected to be close to another -  Metric Learning

In the example, we expect images embeddings to be nearby their captions’ embeddings.

**Research for Cross Modal Retrieval**

The models used for the example are cited from the paper _Improving Visual-Semantic Embeddings with Hard Negatives_ (https://arxiv.org/pdf/1707.05612.pdf).

To make this search system retrieve good results, we have used the models trained in [https://github.com/fartashf/vsepp](https://github.com/fartashf/vsepp) . A model has been trained that encodes `text` and `images` in a common embedding space trying to put together the embedding of images and its corresponding captions.

We use one network per modality:

- VGG19 for images, pretrained on ImageNet.
- A Gated Recurrent Unit (GRU) for captions.

Last layers of these networks are removed and they are used as feature extractors. A Fully Connected Layer is added on top of each one that actually maps the extracted features to the new embedding space.

They are trained on `Flickr30k` dataset with ContrastiveLoss (Tries to put positive matches close in the embedding space and separate negative samples).

**VSE Encoders in Jina for Cross Modal Search**

Two encoders have been created for this example, namely VSEImageEncoder and VSETextEncoder

Process followed is as below:

- Load the weights published by the research paper as result
- Instantiate their VSE encoder and extracts the branch interesting for the modality.

A Dockerfile is provided for each encoder which takes care of all the dependencies and downloads all required files.

**Table of Contents**

- [Prerequisites](#prerequisites)
- [Prepare the data](#prepare-the-data)
- [Build the docker images](#build-the-docker-images)
- [Run the Flows](#run-the-flows)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)


## Prerequisites

This demo requires Python 3.7 and `jina` installation.

## Prepare the data

The model used has been trained using `Flickr30k` and therefore we recommend using this dataset to try this system. But it is a good exercise to see if it works as well for other datasets or your custom ones.

To make this work, we need to get the image files from the `kaggle` dataset (https://www.kaggle.com/hsankesara/flickr-image-dataset). To get it, once you have your Kaggle Token in your system as described in (https://www.kaggle.com/docs/api), run:

```bash
pip install kaggle
kaggle datasets download hsankesara/flickr-image-dataset
unzip flickr-image-dataset.zip
rm flickr-image-dataset.zip
``` 

Then we also need `captions` data, to get this:

```bash
wget http://www.cs.toronto.edu/~faghri/vsepp/data.tar
tar -xvf data.tar
rm -rf data.tar
rm -rf data/coco*
rm -rf data/f8k*
rm -rf data/*precomp*
rm -rf data/f30k/images
mv flickr-image-dataset data/f30k/images
```

Once all the steps are completed, we need to make sure that under `cross-modal-search/data/f30k` folder, we have a folder `images` and a json file `dataset_flickr30k.json`. Inside the `images` folder there should be all the images of `Flickr30K` and the `dataset_flickr30k.json` contains the captions and its linkage to the images.

### Use Flickr8k

Although the model is trained on `Flickr30k`, you can test on `Flickr8k` dataset, which is a much smaller version of flickr30k.

To do so, instead of downloading the `flickr30k` from kaggle, just take its 8k counterpart

```bash
kaggle datasets download adityajn105/flickr8k
unzip flickr8k.zip 
rm flickr8k.zip
mv Images data/f8k/images
mv captions.txt data/f8k/captions.txt
```

make sure that your data folder has:

```bash
data/f8k/images/*jpg
data/fyk/f8k/captions.txt
```

## Build the docker images

To abstract all dependencies needed to make the model from _Improving Visual-Semantic Embeddings with Hard Negatives_ work, `docker` images have been prepared to contain text and image encoders. These images are very big (about `5GB` each (working to make them smaller)).

In order to build them (it may take some time since a lot of data is downloaded),

under `img_emb` run:
```bash
docker build -f Dockerfile -t jinaai/hub.executors.encoders.image.vse .
```

under `txt_emb` run:
```bash
docker build -f Dockerfile -t jinaai/hub.executors.encoders.nlp.vse .
```

## Run the Flows

### Index 

Index is run with the following command, where `batch_size` can be chosen by the user. Index will process both images and captions

```bash
python app.py -t index -n $num_docs -b $batch_size -d 'f8k'
```

Not that `num_docs` should be 8k or 30k depending on the `flickr` dataset you use. If you decide to index the complete datasets,
it is recommendable to increase the number of shards and parallelization. The dataset is provided with the `-d` parameter
with the valid options of `30k` and `8k`. If you want to index your own dataset, check `dataset.py` to see 
how `data` is provided and adapt to your own data source.

Jina normalizes the images needed before entering them in the encoder.
QueryLanguageDriver is used to redirect (filtering) documents based on modality.

### Query

```bash
python app.py -t query-restful
```

You can then query the system from [jinabox](https://jina.ai/jinabox.js/) using either images or text. 
The default port number will be `45678`

Examples of captions in the dataset:

`A man in an orange hat starring at something, A Boston terrier is running in the grass, A television with a picture of a girl on it`

Note the cross for which cross modal stands.

Internally, `TextEncoder` targets `ImageVectorIndexer` and `ImageEncoder` targets `TextVectorIndexer`.
`ImageVectorIndexer` and `TextVectorIndexer` map to a common Embedding Space. (To Jina it means having common dimensionality).

## Results
![](https://github.com/jina-ai/examples/blob/master/cross-modal-search/results/cross-modal-result.jpg "Cross Modal Search Results")
![](https://github.com/jina-ai/examples/blob/master/cross-modal-search/results/saxophone_image2text.png "Cross Modal Search Results")
![](https://github.com/jina-ai/examples/blob/master/cross-modal-search/results/saxophone_text2image.png "Cross Modal Search Results")

## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)


## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
