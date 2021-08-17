# Semantic Wikipedia Search with Transformers and DistilBERT

![](https://docs.jina.ai/_images/jinabox-wikipedia.gif)

## Table of contents: 

- [Overview](#overview)
- [🐍 Build the app with Python](#-build-the-app-with-python)
- [🔮 Overview of the files in this example](#-overview-of-the-files-in-this-example)
- [🌀 Flow diagram](#-flow-diagram)
- [🔨 Next steps, building your own app](#-next-steps-building-your-own-app)
- [🙍 Community](#-community)
- [🦄 License](#-license)

## Overview
|  |  |
| ------------- | ------------- |
| Summary | This showcases a semantic text search app |
| Data for indexing | Wikipedia corpus |
| Data for querying | A text sentence  |
| Dataset used |  [Kaggle Wikipedia corpus](kaggle.com/mikeortman/wikipedia-sentences)     |
| ML model used |  [`distilbert-base-nli-stsb-mean-tokens `](https://huggingface.co/sentence-transformers/distilbert-base-nli-stsb-mean-tokens) |

This example shows you how to build a simple semantic search app powered by [Jina](http://www.jina.ai)'s neural search framework. You can index and search text sentences from Wikipedia using a state-of-the-art machine learning  [`distilbert-base-nli-stsb-mean-tokens `](https://huggingface.co/sentence-transformers/distilbert-base-nli-stsb-mean-tokens) language model from the [Transformers](https://huggingface.co) library.

| item   | content                                          |
|--------|--------------------------------------------------|
| Input  | 1 text file with 1 sentence per line             |
| Output | *top_k* number of sentences that match input query |

## 🐍 Build the app with Python

These instructions explain how to build the example yourself and deploy it with Python. If you want to skip the building steps and just run the app, check out the  [Docker section](#---deploy-the-prebuild-application-using-docker) below.


### 🗝️ Requirements
1. You have a working Python 3.7 or 3.8 environment. 
2. We recommend creating a [new Python virtual environment](https://docs.python.org/3/tutorial/venv.html) to have a clean installation of Jina and prevent dependency conflicts.   
3. You have at least 2 GB of free space on your hard drive. 

### 👾 Step 1. Clone the repo and install Jina


Begin by cloning the repo, so you can get the required files and datasets. In case you already have the examples repository on your machine make sure to fetch the most recent version.

```sh
git clone https://github.com/jina-ai/examples
cd examples/wikipedia-sentences
```

In your terminal,  you should now be located in you the wikipedia-sentences folder. Let's install Jina and the other required Python libraries. For further information on installing Jina check out our [documentation](https://docs.jina.ai/chapters/core/setup/). 


```sh
pip install -r requirements.txt
```
If this command runs without any error messages, you can then move onto step two. 

### 📥 Step 2. Download your data to search 

By default, a small test dataset is used for indexing. This can lead to bad search results.

To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (around 900 MB):

1. Set up [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
2. Run the script: `sh get_data.sh`
3. Index your new dataset: `python app.py -t index -d full -n $num_docs`

The whole dataset contains about 8 Million wikipedia sentences, indexing all of this will take a very long time.
Therefore, we recommend selecting only a subset of the data, the number of elements can be selected by the `-n` flag.
We recommend values smaller than 100000. For larger indexes, the SimpleIndexer used in this example will be very slow also in query time.
It is then recommended to use more advanced indexers like the FaissIndexer.  

### 🏃 Step 3. Index your data

Index your data by running:

```sh
python app.py -t index
```
Here, we can also specify the number of documents to index with ```--num_docs``` / ```-n``` (defult is 10000).

### 🔎 Step 4. Query your indexed data

Once indexing is completed, a search prompt will appear in your terminal. See the text below for an example search query and response.
You can also specify the top k search results with ```--top_k``` /  ```-k``` (default is 5)

```
please type a sentence: What is ROMEO
         
Ta-Dah🔮, here are what we found for: What is ROMEO
>  0(0.36). The ROMEO website, iOS app and Android app are commonly used by the male gay community to find friends, dates, love or get informed about LGBT+ topics.

```

## 🔮 Overview of the files in this example
Here is a small overview if you're interested in understanding what each file in this example is doing. 

| File | Explanation |
|---|---|
|📂 `test/*` |  Various maintenance tests to keep the example running. |
|📃 `app.py`  |  The gateway code to that runs the index & query Flow. |
|📃 `get_data.sh`  |  Downloads the Kaggle dataset. |
|📃 `requirements.txt` |   Contains all required python libraries. |


## 🌀 Flow diagram

This diagram provides a visual representation of the flow in this example, showing which Executors are used in which order:

![wiki_flow](.github/flow.png)  

It can be seen that the flow for this example is quite simple. We receive input Documents from the gateway,
which are then fed into a transformer. This transformer computes an embedding based on the text of the document.
Then, the documents are sent to the indexer which does the following:
 - Index time: Store all the documents on disk (in the workspace folder).
 - Query time: Compare the query document embedding with all stored embeddings and return closest matches

## ⏭️ Next steps, building your own app

Did you like this example and are you interested in building your own? For a detailed tuturial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation.

- [Enable querying while indexing](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences-query-while-indexing)

## 👩‍👩‍👧‍👦 Community

- [Slack channel](https://slack.jina.ai) - a communication platform for developers to discuss Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## 🦄 License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/examples/blob/master/LICENSE) for the full license text.
