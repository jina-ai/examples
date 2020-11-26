
# Object search

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

In this example, we use `fasterrcnn_resnet50_fpn` for object detection and then index these cropped object images with `MobileNetV2`. You can use this demo system to index an image dataset and query the most similar object in those images. The query should be a cropped object image.

Features that come out of the box:

- Interactive query
- Parallel replicas
- Index with shards
- Containerization
- REST and gRPC gateway
- Dashboard monitor

To save you from dependency hell, we'll use the containerized version in these instructions. That means you only need to have [Docker installed](https://docs.docker.com/get-docker/). No Python virtualenv, no Python package (un)install. 

The code can of course run natively on your local machine, please [read the Jina installation guide for details](https://docs.jina.ai/chapters/install/via-pip.html).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Download and Extract Data](#download-and-extract-data)
- [Index Image Data](#index-image-data)
- [Start the Server](#start-the-server)
- [Query via REST API](#query-via-rest-api)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Download and Extract Data
### Use Flickr8k
You can try this example with [Flickr8k](https://www.kaggle.com/adityajn105/flickr8k) object detection dataset. You can also use other datasets like COCO & [Open Images 2019](https://www.kaggle.com/c/open-images-2019-object-detection/overview)

Download the Flickr8k from Kaggle

```bash
kaggle datasets download adityajn105/flickr8k
unzip flickr8k.zip 
rm flickr8k.zip
mv Images data/f8k/images
```

Note: Flickr8k is not an ideal dataset but we are using due to its small size.

## Index Image Data
<p align="center">
  <img src=".github/.README_images/index.png?raw=true" alt="Jina banner" width="90%">
</p>
Index 1000 images. This can take some time and you can try a smaller number as well.
```bash
python app.py -task index -n 1000 -overwrite True
```

If it's running successfully, you should be able to see logs scrolling in the console and in the dashboard:

<p align="center">
  <img src=".github/.README_images/0a8863abb3fcee182e1fe8fe46c47b7a.gif?raw=true" alt="Jina banner" width="45%">
  <img src=".github/.README_images/ed2907cd11ac26a2a3a2555f16071d13.gif?raw=true" alt="Jina banner" width="45%">
</p>

## Start the Server
<p align="center">
  <img src=".github/.README_images/query.png?raw=true" alt="Jina banner" width="90%">
</p>
Start server which returns `original` images. The matching of query happens with all indexed object images and returns the original parent image in which the indexed object was found.
```bash
python app.py -task query -r original
```

<p align="center">
  <img src=".github/.README_images/dog.png?raw=true" alt="Jina banner" width="45%">
  <img src=".github/.README_images/dog-results.png?raw=true" alt="Jina banner" width="45%">
</p>

Start server which returns `object` images. The matching of query happens with all indexed object images and returns them.
```bash
python app.py -task query -r object
```

<p align="center">
  <img src=".github/.README_images/cycle.png?raw=true" alt="Jina banner" width="45%">
  <img src=".github/.README_images/cycle-results.png?raw=true" alt="Jina banner" width="45%">
</p>

## Query via REST API

When the REST gateway is enabled, Jina uses the [data URI scheme](https://en.wikipedia.org/wiki/Data_URI_scheme) to represent multimedia data. Simply organize your picture(s) into this scheme and send a POST request to `http://0.0.0.0:45678/api/search`, e.g.:

```bash
curl --verbose --request POST -d '{"top_k": 10, "mode": "search",  "data": ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AxWcWRUeCEeBO68T3u1qLWarHqMaxDnxhAEaLh0Ssu6ZGfnKcjP4CeDLoJok3o4aOPYAJocsjktZfo4Z7Q/WR1UTgppAAdguAhR+AUm9AnqRH2jgdBZ0R+kKxAFoAME32BL7fwQbcLzhw+dXMmY9BS9K8EarXyWLH8VYK1MACkxlLTY4Eh69XfjpROqjE7P0AeBx6DGmA8/lRRlTCmPkL196pC0aWBkVs2wyjqb/LABVYL8Xgeomjl3VtEMxAeaUrGvnIawVh/oBAAD///GwU6v3yCoVAAAAAElFTkSuQmCC", "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAA2ElEQVR4nADIADf/AvdGjTZeOlQq07xSYPgJjlWRwfWEBx2+CgAVrPrP+O5ghhOa+a0cocoWnaMJFAsBuCQCgiJOKDBcIQTiLieOrPD/cp/6iZ/Iu4HqAh5dGzggIQVJI3WqTxwVTDjs5XJOy38AlgHoaKgY+xJEXeFTyR7FOfF7JNWjs3b8evQE6B2dTDvQZx3n3Rz6rgOtVlaZRLvR9geCAxuY3G+0mepEAhrTISES3bwPWYYi48OUrQOc//IaJeij9xZGGmDIG9kc73fNI7eA8VMBAAD//0SxXMMT90UdAAAAAElFTkSuQmCC"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```

[JSON payload syntax and spec can be found in the docs](https://docs.jina.ai/chapters/restapi/#).

This example shows you how to feed data into Jina via REST gateway. By default, Jina uses a gRPC gateway, which has much higher performance and rich features. If you are interested in that, go ahead and check out our [other examples](https://learn.jina.ai) and [read our documentation on Jina IO](https://docs.jina.ai/chapters/io/#).


## Troubleshooting

### Memory Issues

If you are using Docker Desktop, make sure to assign enough memory for your Docker container, especially when you have multiple replicas. Below are my MacOS settings with two replicas:


<p align="center">
  <img src=".github/.README_images/d4165abd.png?raw=true" alt="Jina banner" width="80%">
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

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
