# Build a Search system using Facebook AI Similarity Search (FAISS) or Annoy as vector database <!-- omit in toc -->

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

In this demo we will build a vector search engine with Jina. This means that given a dataset and some data to search in it, it will find the closest vector in it.

But not just that, let's imagine that after you indexed your data you want to use a different type of indexer now to query, 
what you do then? You index your data each time for every type? No, no, don't worry, we will see how to use different
 indexers as vector databases and how to use a `ref_indexer` as a base indexer. 
So you can have that as a base and then query with whatever type you wish.
 

Before moving forward, we highly suggest completing/reviewing our [Jina 101](http://101.jina.ai) and [Jina "Hello, World!"👋🌍](https://github.com/jina-ai/jina#jina-hello-world-) to make sure we are on the same page. 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Requirements](#requirements)
- [Prepare the data](#prepare-the-data)
- [Define the Flows](#define-the-flows)
- [Run the Flows](#run-the-flows)
- [Evaluation results](#evaluation-results)
- [Use Docker image from the jina hub](#use-docker-image-from-the-jina-hub)
- [Good to know](#good-to-know)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

For this example you can use one of these 2 datasets [ANN_SIFT10K or ANN_SIFT1M](http://corpus-texmex.irisa.fr/), which are datasets comprised of three vector sets:  

- 10K or 1M to index
- 100 or 10K to query
- 25K or 100k to train

We will work with ANN_SIFT10K (siftsmall), that are [SIFT](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform) descriptors for some image dataset. 
But if you wish you could use a larger datasets from the same [source](http://corpus-texmex.irisa.fr/). A [docker image](https://hub.docker.com/r/jinahub/app.example.advancedvectorsearch) is published where the ANN_SIFT1M (sift) has already been indexed
using 4 shards.

And since we said we want to use different indexers to query, we will use [Faiss](https://hub.docker.com/r/jinahub/pod.indexer.faissindexer) and [Annoy](https://hub.docker.com/r/jinahub/pod.indexer.annoyindexer).

Another cool thing to have would be to be able to compare the results between those indexers, so we will also show how to evaluate ranking results with Faiss and Annoy, and add the search with NumpyIndexer (that uses exhaustive search, so it's close to 100% recall) to compare. But we encourage you to try different indexers and different options for other indexers to see what gets the best results and performance.

## Requirements

Let's start! First thing is to be sure we have all the requirements, so we can run:

```bash
pip install -r requirements.txt
```

And to make things easy will use the docker images for Annoy and Faiss, so make sure to pull the from the [Jina Hub repository](https://hub.docker.com/u/jinahub)

## Prepare the data

Now let's get some data. We have prepared a small script that will download it

```bash
./get_data.sh siftsmall
```

Cool we have the data now, but FAISS needs to learn some patterns of the data in order to build an efficient indexing scheme. A.K.A we still need the training data, which is done with some subset of data that is not necessarily part of the index.So you need to run this script that will generate a workspace folder where the training data will be stored.

```bash
./generate_training_data.sh
```
This workspace folder will contain the built index once the vectors are indexed and will be mapped to the docker image.

## Define the Flows

### Index <!-- omit in toc -->

Finally we're done getting all the prerequisites, we can index our data now! 

To index the data we will define our **Flow** with a **YAML** file. In the Flow YAML file, we will add **Pods** in sequence. In this demo, we have two pods defined `encoder` and `indexer` as you can see it here:


<table style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-index.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
version: '1'
pods:
  - name: encoder
    uses: yaml/encode.yml
    shards: $JINA_PARALLEL
  - name: indexer
    uses: yaml/indexer.yml
    shards: $JINA_SHARDS
    timeout_ready: 10000
    polling: any
```
</sub>
</td>
</tr>
</table>

As a side note, we actually have another Pod working in silence, since the input to the very first Pod is always the Pod with the name of **gateway**, aka the "Forgotten" Pod. But most of the time, we can safely ignore the **gateway** because it essentially does the dirty work of orchestrating the work for the Flow.


### Query <!-- omit in toc -->

Ok, we have our data indexed, and for query we need to do a similar thing.Which means we also need a Flow to process the request message during querying. The query flow looks very similar
to the index flow but with an extra pod used to evaluate results.

<table  style="margin-left:auto;margin-right:auto;">
<tr>
<td> flow-query.yml</td>
</tr>
<tr>
<td>
  <sub>

```yaml
!Flow
version: '1'
env:
  OMP_NUM_THREADS: ${{OMP_NUM_THREADS}}
with:
  read_only: true
pods:
  - name: encoder
    show_exc_info: true
    uses: yaml/encode.yml
    shards: $JINA_PARALLEL
  - name: indexer
    polling: all
    show_exc_info: true
    uses: $JINA_USES
    uses_internal: $JINA_USES_INTERNAL
    shards: $JINA_SHARDS
    timeout_ready: -1
    uses_after: yaml/merge-matches-sort.yml
    volumes: './workspace:/docker-workspace'
    remove_uses_ba: true
    docker_kwargs:
      environment:
        JINA_FAISS_INDEX_KEY: $JINA_FAISS_INDEX_KEY
        JINA_FAISS_DISTANCE: $JINA_FAISS_DISTANCE
        JINA_FAISS_NORMALIZE: $JINA_FAISS_NORMALIZE
        JINA_FAISS_NPROBE: $JINA_FAISS_NPROBE
        JINA_ANNOY_METRIC: $JINA_ANNOY_METRIC
        JINA_ANNOY_NTREES: $JINA_ANNOY_NTREES
        JINA_ANNOY_SEARCH_K: $JINA_ANNOY_SEARCH_K
        OMP_NUM_THREADS: ${{OMP_NUM_THREADS}}
  - name: evaluate
    show_exc_info: true
    uses: yaml/evaluate.yml
```
</sub>
</td>
</tr>
</table>

All the `environment` variables are added so that it is easy for the user to try out different configurations of `annoy` or `faiss` indexers.

In this Flow, the `faiss_indexer` is the one that will do the nearest neighbours search from the given chunk (in this case, since every document has one chunk they are the same). Additionally, it will return the top_k most similiar documents in order of similiarity. Later, `doc_indexer` retrieves the actual document value from the Document Id.

## Run the Flows

### Index <!-- omit in toc -->

That was a lot of info, let's get to actually run our Flows now. To index you just run the following command

```bash
python app.py -t index
```
You could also change request_size if you want. 

### Query <!-- omit in toc -->

Now, to query you can choose between `annoy`, `faiss`, or `numpy`. And you run the script like this:

```bash
python app.py -t query -i {index_type}
```
It is important to make sure that the environment variables in `app.py` are set to the right docker image tags that one wants to test.


## Evaluation results

The results with the default parameters for Annoy, Faiss and NumpyIndexers are:

```bash
python app.py -t query -i numpy

Recall@100 => 99.47000050544739%
```

```bash
python app.py -t query -i faiss

Recall@100 => 47.16999990865588%
```

```bash
python app.py -t query -i annoy

Recall@100 => 77.69999986886978%
```

But feel free to look for different parameters to guarantee the best results

## Use Docker image from the jina hub

To make thing a little easier, we have built and published the [Docker image](https://hub.docker.com/r/jinahub/app.example.advancedvectorsearch) with the ANN_SIFT1M dataset indexed. You can retrieve the docker image using:

```bash
docker pull jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```
So you can pull from its latest tags and run it. By default it runs the search with `faiss` indexer. 

To simply run it, please do:
```bash
docker run jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```

If you want to run the image with `annoy` as a search library, you can override the entrypoint doing:

```bash
docker run -it --entrypoint=/bin/bash jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20 entrypoint.sh annoy
```

If you want to change the parameters of `Faiss` or `Annoy` Indexer you can pass different environment variables
to the `docker run` command by doing for instance:

```bash
docker run -e JINA_FAISS_INDEX_KEY='Flat' jinahub/app.example.advancedvectorsearch:0.0.2-0.9.20
```

## Good to know

An important parameter to set is `JINA_DISTANCE_REVERSE`, depending on the type of distance or metric that is used. For instance for `inner_product` distance, `JINA_DISTANCE_REVERSE` should be set to `True`. This is because returned measure for `Faiss` is similarity and not distance. Which means that the results should be sorted in descending order to get what we would expect.

Another parameter that cannot be found in the `init` arguments of `FaissIndexer` or `AnnoyIndexer` is `OMP_NUM_THREADS`. This controls how many threads are used by `Faiss` when querying. And since the image has been built with 4 shards (around 250K documents each), the `OMP_NUM_THREADS` is set to 1 to have the example use 4 CPUs. But also feel free to tweak this parameter to check the quality and speed of the results.


## Wrap up

In this example we have seen how to use different indexers as vector databases and how to use a `ref_indexer` as a base indexer. We also have seen how to use a pod inside a docker container inside our index and query flows, and how to use evaluators to assess the quality of our search system.

## Next Steps

Where to go from here? You can always try:  

- different kinds of inverted indices and options from FAISS or Annoy.
- other indexers.
- indexing larger datasets.

Finally, play around with different evaluation metrics.

**Enjoy Coding with Jina!**

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
