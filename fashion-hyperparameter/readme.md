# Fashion-MNIST Evaluate & Optimize 

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

This examples showcases evaluation capabilities of Jina. You can use evaluation to try out different components and select the best. To make it easier we also show how to use Optuna to optimise faster. We are using the fashion-MNIST dataset for this purpose. It has greyscale cloth images and 10 type of category labels. 

We use the label of images for evaluating our encoder. We optimize `target_dimension` in encoder for metric precision@1.

## Installation  
```pip install requirements.txt```

## Evaluation  
First we index all the images along with its category as label. We define a custom evaluator in `pods/evaluate.py` which checks if the label of first result matches with the label of query image. Then we query with a pair of query and groundtruth. Query consists of image while groundtruth consists of true label.  

Running `python evaluate.py` will download data, index it and run the evaluation.   

### Index flow
<p align="center">
  <img src="readme_images/index.svg?raw=true" alt="image" width="80%">
</p>

### Evaluate flow
<p align="center">
  <img src="readme_images/evaluate.svg?raw=true" alt="image" width="80%">
</p>

## Optimize  
Define the parameter to be optimised in `sample_run_parameters` in `optimize.py`. On running `python optimize.py` it uses `Optuna` to run evaluations for our metric which is mean precision@1. It finally prints out the best parameters. Increase `n_trials` in `optimize.py` to run more experiments.   

## Serving for query  
Now manually fix up best value of hyperparameter `target_dimension` we found by optimizing, in `encoder.yml` to serve for query.  
Run `jina run flow flow/query.yml` to start the server for querying.  

### Query flow
<p align="center">
  <img src="readme_images/query.svg?raw=true" alt="image" width="80%">
</p>

## Modules
```
├── fashion
│   ├── config.py -> define jina config + hyperparameters
│   ├── data.py -> downloads the data
│   └── evaluation.py -> modules required for evaluation
│
├── flows
│   ├── evaluate.yml -> evaluate flow
│   ├── index.yml -> index flow
│   └── query.yml -> query flow
│
├── evaluate.py -> run this to get the evaluation
├── optimize.py -> define optuna parameters & run this to find the best parameters
│
├── pods
│   ├── components.py -> custom encoder
│   ├── encoder.yml
│   ├── evaluate.py -> custom evaluator
│   ├── evaluate.yml
│   ├── indexer.yml
│   └── reduce.yml
│
├── readme.md
└── requirements.txt
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

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
