<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Build an Audio Search](#build-an-audio-search)
  - [Install Prerequisites](#install-prerequisites)
  - [Download Data](#download-data)
  - [Run](#run)
  - [Documentation](#documentation)
  - [Community](#community)
  - [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Build an Audio Search 

A demo of neural search for audio data based on **Mel Frequency Cepstral Coefficients** 


Install Prerequisites
---------------------

    click
    pillow
    librosa
    jina[devel]==0.4.1
    
    
Download Data
-------------

To download the dataset run the below command 

    sh ./get_data.sh
    
## Run

| Command                  | Description                  |
| :---                     | :---                         |
| ``python app.py index``  | To index files/data          |
| ``python app.py search`` | To run query on the index    |

    

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

Copyright (c) 2020 Jina AI. All rights reserved.

    