# Build A Cross-Modal Search System To Look For Images From Captions and vice versa

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


**Table of Contents**
  - [Overview](#-overview)
  - [🐍 Build the app with Python](#-build-the-app-with-python)
  - [🌀 Flow diagram](#-flow-diagram)
  - [🚑 Troubleshooting](#-troubleshooting)
  - [📖 Optional: Extra information useful for the user](#-optional-extra-information-useful-for-the-user)
  - [🔮 Overview of the files](#-overview-of-the-files)
  - [🐋 Deploy the prebuild application using Docker](#-deploy-the-prebuild-application-using-docker) 
  - [⏭️ Next steps](#-next-steps)
  - [‍👩‍👧‍👦 Community](#-community)
  - [🦄License](#-license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

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

![](https://github.com/jina-ai/examples/blob/master/cross-modal-search/visualizations/cross-modal-result.jpg)

## Overview
|  |  |
| ------------- | ------------- |
| Learnings | How to use image captions (short descriptions of the image content) to search for images. |
| Used for indexing | Images + captions. |
| Used for querying | Image caption e.g. "A boy playing basketball". |
| Dataset used | [Flickr 8k](https://www.kaggle.com/adityajn105/flickr8k) containing 8k image caption pairs. |
| Model used | Both [CLIP: Contrastive Language-Image Pre-Training](https://arxiv.org/abs/2007.13135) and [VSE++: Improving Visual-Semantic Embeddings with Hard Negatives](https://arxiv.org/pdf/1707.05612.pdf) are demonstrated. |

In this example, Jina is used to implement a cross-modal search system.
This example allows the user to search for images given a caption description.
First, we encode all images in our dataset into vectors and create an index of these vectors.
When we search with text inputs, we compute the vector representation of this text and compare it to the previously calculated image vector index to find the most similar image. 
It is also possible to do it the other way around and use the image encoding to search for similar text-embeddings (captions).

_____

## 🐍 Build the app with Python

These instructions explain how to build the example yourself and deploy it with Python. 
If you want to skip the building steps and just run the example with Docker, check out the  [Docker section](#-deploy-the-prebuild-application-using-docker) below. 


### 🗝️ Requirements

1. You have a working Python 3.7 or 3.8 environment and a installation of [Docker](https://docs.docker.com/get-docker/). 
2. We recommend creating a [new Python virtual environment](https://docs.python.org/3/tutorial/venv.html) to have a clean installation of Jina and prevent dependency conflicts.   
3. You have at least 2 GB of free space on your hard drive. 

### 👾 Step 1. Clone the repo and install Jina

Begin by cloning the repo, so you can get the required files and datasets. (If you already have the examples repository on your machine make sure to fetch the most recent version)

```sh
git clone https://github.com/jina-ai/examples
cd examples/cross-modal-search
````
In your terminal, you should now be located in you the *cross-modal-search* folder. Let's install Jina and the other required Python libraries. For further information on installing Jina check out [our documentation](https://docs.jina.ai/chapters/core/setup/).

```sh
pip install -r requirements.txt
```

### 🏃 Step 2. Index your data
To quickly get started, you can index a [small dataset](data/toy-data) to make sure everything is working correctly. 
You can pre-fetch the Pods containing the machine learning models required to calculate the embeddings of the data using Docker.
```bash
docker pull jinahub/pod.encoder.clipimageencoder:0.0.2-1.2.0
docker pull jinahub/pod.encoder.cliptextencoder:0.0.3-1.2.2
```
Or for the VSE model:

```bash
docker pull jinahub/pod.encoder.vseimageencoder:0.0.5-1.2.0
docker pull jinahub/pod.encoder.vsetextencoder:0.0.6-1.2.0
```
Once the images are downloaded, run
```bash
python app.py -t index
```
If you see the following output, it means your data has been correctly indexed.

```
Flow@5162[S]:flow is closed and all resources are released, current build level is 0
```

We recommend you come back to this step later and index the full flickr 8k dataset for better results. To index the [full dataset](https://www.kaggle.com/adityajn105/flickr8k) (8000 images) follow these steps:
1. Register for a free [Kaggle account](https://www.kaggle.com/account/login?phase=startRegisterTab&returnUrl=%2F)
2. Set up your API token (see [authentication section of their API docs](https://www.kaggle.com/docs/api))
3. Run `sh get_data.sh` 

To index the full dataset, run
```shell
python app.py -t index --data_set=f8k
```

### 🔎 Step 3: Query your data
Jina offers several ways to search (query) your data. In this example, we show two of the most common ones. In a production environment, you would only choose one which suits your use case best. 

#### Using a REST API
Begin by running the following command to open the REST API interface.

```sh
python app.py -t query_restful
```

You should open another terminal window and paste the following command. 

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://localhost:45678/search'
```

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar images sentences to the text input you provided in the `data` parameter.
Note, that the toy-data only contains two images.
Feel free to alter the text in the 'data' parameter and play around with other queries (this is only fun with the large dataset)! For a better understanding of the parameters see the table below. 
|  |  |
|--|--|
| `top_k` | Integer determining the number of sentences to return |
| `mode` | Mode to trigger in the call. See [here](https://docs.jina.ai/chapters/rest/) for more details |
| `data` | Text input to query |
 
#### Using Jina Box; our frontend search interface
**Jina Box** is a light-weight, highly customizable JavaScript based front-end search interface. To use it for this example, begin by opening the REST API interface. 

```sh
python app.py -t query_restful
```

In your browser, open up the hosted Jina Box on [jina.ai/jinabox.js](https://jina.ai/jinabox.js/). In the configuration bar on the left-hand side, choose a custom endpoint and enter the following: `http://127.0.0.1:45678/search`.
You can type search queries into the text box on the right-hand side!

______

## 🌀 Flow diagram
This diagram provides a visual representation of the Flows in this example; Showing which executors are used in which order.
Remember, our goal is to compare vectors representing the semantics of images with vectors encoding the semantics of short text descriptions.

### Indexing
![](visualizations/cross-modal-index-flow.png)  
As you can see, the Flow that Indexes the data contains three parallel branches: 
- Upper: a key-value indexer for the images that we use as a lookup (like a Dictionary in Python).
- Middle: transformations to get from the JPG to vectors
- Lower: transformations to get from text descriptions to vectors
To have️ low latency at query time, we store the computed vectors on disk.

### Querying
![](visualizations/cross-modal-query-flow.png)  
This Flow shows what happens when a user queries our data. First, the provided text description is passed through the text Encoder which turns
it into a vector. Now, we use our image vector index to find the most similar image encodings to the previously computed text vector from the user.
Because the user does not want to see the vector as a result, but the image this vector belongs to we use the key-value lookup to get from image vector to human-interpretable JPG image.
Note, that this Flow only shows how to search for images using text. The example actually support searching for text using images as well. 
As an exercise, you can think of the required steps for that and check against our [Flow configuration](flows/flow-query.yml).


## 🚑 Troubleshooting

In case a Flow hangs during indexing it often helps to restart the process.


## 📖 Optional: Extra information useful for the user

**Motive behind Cross-Modal Retrieval**

Cross-modal retrieval tries to effectively search for documents of one modality (text) in an index storing data of another modality (images). An example of this is google image search.
```bash
python app.py -t index -n $num_docs -s $request_size -d 'f8k' -m clip
```

If your index hangs, please remove the workspace,
reduce the `request_size` and re-run the above command to index.
The default `request_size` is 12. 
Check out the fix suggested in [this issue](https://github.com/jina-ai/examples/issues/613).

Not that `num_docs` should be 8k or 30k depending on the `flickr` dataset you use.
If you decide to index the complete datasets,
it is recommendable to increase the number of shards and parallelization.
The dataset is provided with the `-d` parameter with the valid options of `30k` and `8k`.
If you want to index your own dataset,
check `dataset.py` to see how `data` is provided and adapt to your own data source.
If you want to switch to `VSE++` model, replace `-m clip` with `-m vse`
Request size can be configured with `-s` flag.

Jina normalizes the images needed before entering them in the encoder.
`QueryLanguageDriver` is used to redirect (filtering) documents based on modality.

Modality is an attribute assigned to a document in Jina in the protobuf Document structure.
It is possible that documents may be of the same mime type,
but come from different distributions,
for them to have different modalities.
**Example**: In an article or web page, 
the body text and the title are from the same mime type (text),
but will differ in statistical properties (like expected length or frequency of certain key-words) and should therefore be modeled separately.
If that is the case, we consider them as different modalities.


Different Encoders map different modalities to a common embedding space.
They need to extract semantic information from the documents. 

In this embedding space,
documents that are semantically relevant to each other from different modalities are expected to be close to another - [Metric Learning](https://en.wikipedia.org/wiki/Similarity_learning#:~:text=Metric%20learning%20is%20the%20task,(or%20the%20triangle%20inequality).)

In the example, we expect images embeddings to be nearby their captions’ embeddings.

**Research for Cross-Modal Retrieval**

The models used for the example are cited from the paper, you can try our example with one of them:

1. [CLIP: Contrastive Language-Image Pre-Training](https://arxiv.org/abs/2007.13135) (recommend)
2. [VSE++: Improving Visual-Semantic Embeddings with Hard Negatives](https://arxiv.org/pdf/1707.05612.pdf).

Both of the models have been trained to encode pairs of `text` and `images` into a common embedding space.

**CLIP Encoders in Jina for Cross-Modal Search**

Two encoders have been created for this example, namely `CLIPImageEncoder` and `CLIPTextEncoder`,
for encoding image and text respectively.

**VSE Encoders in Jina for Cross-Modal Search**

Two Encoders have been created for this example, namely `VSEImageEncoder` and `VSETextEncoder`,
for encoding image and text respectively.


## 🔮 Overview of the files

|                      |                                                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 📂 `flows/`          | Folder to store Flow configuration                                                                               |
| --- 📃 `flow-index.yml`     | YAML file to configure indexing Flow                                                                             |
| --- 📃 `flow-query.yml`     | YAML file to configure querying Flow                                                                             |
| 📂 `pods/`           | Folder to store Pod configuration                                                                                |
| --- 📂 `clip`   | YAML files to configure the Encoder using the clip model                                                                               |
| --- 📂 `vse`   | YAML files to configure the Encoder using the vse model                                                                                |
| --- 📃 `image-load.yml`   | YAML file to configure loading JPG files                                                                             |
| --- 📃 `image-normalzer.yml`   | YAML file to configure how images are normalized                                                                           |
| --- 📃 `index-image-kv.yml`   | YAML file to configure the key-value image index                                                                           |
| --- 📃 `index-image-vector.yml`   | YAML file to configure the vector image index                                                                           |
| --- 📃 `index-text.yml`   | YAML file to configure the index for the text vectors                                                                            |
| --- 📃 `merge_matche_sort_topk.yml`   | YAML file to configure the merging ranking of matches in the final result.                                                                     |
| 📂 `workspace/`      | Folder to store indexed files (embeddings and documents). Automatically created after the first indexing   |
| 📂 `visualizations/`      | Folder to store images used for documentation  |
| 📂 `data/`      | Folder to store the toy-data for the example  |

_____

## 🐋 Deploy the prebuild application using Docker
To make it easier for the user, we have built and published the [Docker image](https://hub.docker.com/r/jinahub/app.example.crossmodalsearch) with the indexed documents.
Just be aware that the image weights 11 GB. Make sure that your docker lets you allocate a sufficient amount of memory. 

You can retrieve the docker image using:

```bash
docker pull jinahub/app.example.crossmodalsearch:0.0.3-1.0.8
```
So you can pull from its latest tags. 

To run the application with the pre-indexed documents and ready to be used from Jina Box, run

```bash
docker run -p 45678:45678 jinahub/app.example.crossmodalsearch:0.0.3-1.0.8
```

## ⏭️ Next steps

Did you like this example and are you interested in building your own? For a detailed tutorial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can always get support from our [Slack community](https://slack.jina.ai) .

## 👩‍👩‍👧‍👦 Community

- [Slack channel](https://slack.jina.ai) - a communication platform for developers to discuss Jina.
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities.
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`.  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## 🦄 License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
