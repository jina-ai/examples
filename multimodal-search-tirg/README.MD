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

# Multimodal Search With TIRG & fashion200k
In this example we build a multimodal search engine for image retrieval using [TIRG](https://github.com/google/tirg) (Composing Text and Image for Image Retrieval). We use the [Fashion200k](https://github.com/xthan/fashion-200k) dataset, where the input query is in the form of a clothing image plus some text that describes the desired modifications to the image.

At index time we encode the images with TIRG's image encoder. At query time we use the feature embeddings constructed by TIRG's multimodal encoder based on both the input image and text to search over the indexed images. The query text is the modification we want to apply over the query image.  

TIRG's multimodal encoder requires both image and text to create the final encoding. This is made possible by leveraging the capabilities of Jina's MultiModalEncoder to handle any type of modality.  

The Fashion200k model was only trained for certain types of image modifications, such as types of dresses, colors or lengths. Hence, it is limited in the types of modifications it can do, e.g. replace with 3/4 length, replace with beige.  

Note: The [TIRG paper](https://arxiv.org/pdf/1812.07119.pdf) reports a Recall@1 of 14.1 for the Fashion200k dataset and some queries might not have good results.  

<p align="center">
  <img src=".readme_images/fashion200k.png?raw=true" alt="Jina banner" width="70%">
</p>
<p align="center">
  <img src="https://github.com/google/tirg/blob/master/images/newpipeline.png?raw=true" alt="Jina banner" width="70%">
</p>

**Table of Contents**

- [Download and Extract Data](#download-and-extract-data)
- [Build Encoder Images](#build-encoder-images)
- [Index Image Data](#index-image-data)
- [Query](#query)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Download and Extract Data

Run the following script to download the data from [Kaggle](https://www.kaggle.com/mayukh18/fashion200k-dataset).

*Note: the size of the dataset is 6GB.*

```bash
bash ./get_data.sh data/
```

Alternatively, You can [Download](https://drive.google.com/drive/folders/0B4Eo9mft9jwoamlYWFZBSHFzV3c) and extract the data from google drive.


## Index Image Data
<p align="center">
  <img src=".readme_images/index.png?raw=true" alt="Jina banner" width="100%">
</p>
Index 1000 images. This can take some time and you can try a smaller number as well. We use a custom TirgImageEncoder for encoding the images. Jina normalizes the images before sending them to the encoder. If you decide to index large datasets, it is recommended to increase the number of shards and parallelization.  

```bash
python app.py --task index -n 1000 -overwrite True
```

If it's running successfully, you should be able to see and scroll through the logs in the console and in the dashboard:

<p align="center">
  <img src="https://github.com/jina-ai/examples/blob/master/.github/.README_images/0a8863abb3fcee182e1fe8fe46c47b7a.gif?raw=true" alt="Jina banner" width="45%">
  <img src="https://github.com/jina-ai/examples/blob/master/.github/.README_images/ed2907cd11ac26a2a3a2555f16071d13.gif?raw=true" alt="Jina banner" width="45%">
</p>

## Query
<p align="center">
  <img src=".readme_images/query.png?raw=true" alt="Jina banner" width="100%">
</p>
This will start the server, where you can then run your query and see the results as a pop-up. TIRG's multimodal encoder requires both input image and text to create the final encoding. This is made possible by leveraging our MultiModalEncoder capabilities. We use our QueryLanguageDriver to redirect text and image documents based on modality.  

```bash
python app.py --task query --image_path path_to_image --text_query 'change color to red'
```

## Troubleshooting

### Memory Issues

If you are using Docker Desktop, make sure to assign enough memory for your Docker container, especially when you have multiple replicas. Below are my MacOS settings with two replicas:


<p align="center">
  <img src="https://github.com/jina-ai/examples/blob/master/.github/.README_images/d4165abd.png?raw=true" alt="Jina banner" width="80%">
</p>

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

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.