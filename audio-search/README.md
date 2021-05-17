<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Build Audio Search with Vggish](#build-audio-search-with-vggish)
  - [Install Prerequisites](#install-prerequisites)
  - [Download Model](#download-model)
  - [Run](#run)
  - [Run as a Docker Container](#run-as-a-docker-container)
  - [Documentation](#documentation)
  - [Community](#community)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Build Audio Search with Vggish

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

A demo of neural search for audio data based Vggish model.


<p align="center">
  <img src=".github/demo.gif?raw=true" alt="Jina banner" width="90%">
</p>


## Install Prerequisites

- In order to run this example, you should have [youtube-dl](https://ytdl-org.github.io/youtube-dl/index.html),
[ffmpeg](https://ffmpeg.org/download.html) available in your system. Please refer to the specific installation instructions.
- For MacOS users, a [libmagic](https://filemagic.readthedocs.io/en/latest/guide.html)
installation will furtherly be needed and can be obtained by running
```bash
brew install libmagic
```

- You can add to your system the python libraries required for this example by running the following:
```bash
pip install -r requirements.txt
```

## Download Model

- In this example, we use the Vggish model to encode the sound files. You can find more details about the model at [https://github.com/tensorflow/models/tree/master/research/audioset/vggish](https://github.com/tensorflow/models/tree/master/research/audioset/vggish). Use the following cmd to download the models. For downloading the audioset data, we adapt the codes from the `runme.sh` script at [https://github.com/qiuqiangkong/audioset_tagging_cnn ](https://github.com/qiuqiangkong/audioset_tagging_cnn). 

```bash
bash download_model.sh
```

## Download Data
`get_data.sh` script downloads a few Beethoven symphonies from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:WAV_files). This is a small dataset so indexes quickly. Just run

```sh
sh ./get_data.sh
```
You can also use you own `.wav` files. Make sure the files are under `data/`. 

After preparing the data, here is how the folder looks like,
```
.
├── Dockerfile
├── README.md
├── app.py
├── data
│   ├── Yjo9lFbGXf_0.wav
│   └── Yjzij1UX73kU.wav
├── download_model.sh
├── flows
│   ├── index.yml
│   └── query.yml
├── get_data.sh
├── models
│   ├── vggish_model.ckpt
│   └── vggish_pca_params.npz
├── pods
│   ├── chunk_merger.yml
│   ├── customized_executors.py
│   ├── doc.yml
│   ├── encode.yml
│   ├── rank.yml
│   ├── segment.yml
│   ├── vec.yml
│   └── vggish
│       ├── mel_features.py
│       ├── vggish_input.py
│       ├── vggish_params.py
│       ├── vggish_postprocess.py
│       └── vggish_slim.py
├── requirements.txt
└── tests
    ├── data
    │   ├── YjmN-c5mDxfw.wav
    │   ├── Yjo9lFbGXf_0.wav
    │   └── Yjzij1UX73kU.wav
    └── test_audio_search.py
```


## Run

| Command                  | Description                  |
| :---                     | :---                         |
| ``python app.py -t index``  | To index files/data          |
| ``python app.py -t query`` | To run query on the index    |

Then open https://jina.ai/jinabox.js/ for querying.
## Run as a Docker Container


To mount local directory and run:

```bash
docker run -v "$(pwd)/data:/workspace/data" -v "$(pwd)/workspace:/workspace/workspace" jinaai/hub.app.audio-search:0.0.1 index
``` 

Run the following cmd and open [https://jina.ai/jinabox.js/](https://jina.ai/jinabox.js/) for querying

```bash
docker run -p 65481:65481 -e "JINA_PORT=65481" -v "$(pwd)/workspace:/workspace/workspace" jinaai/hub.app.audio-search:0.0.1 search
```

## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in-depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. For more details, check out:

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

Copyright (c) 2021 Jina AI. All rights reserved.


