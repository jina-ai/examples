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

### 📇 Step 2. Index & 🔍 Search

By default, we'll start off by indexing a [small dataset of 50 sentences](data/toy-input.txt) :

```sh
python app.py -t index
```
Here, we can also specify the number of documents to index with ```--num_docs``` / ```-n``` (defult is 50) and the top k search results with ```--top_k``` /  ```-k``` (defult is 5).

Once indexing is completed, a search prompt will appear in your terminal. See the image below for an example search query and response.

```
please type a sentence: What is ROMEO
         
Ta-Dah🔮, here are what we found for: What is ROMEO
>  0(0.36). The ROMEO website, iOS app and Android app are commonly used by the male gay community to find friends, dates, love or get informed about LGBT+ topics.

```


To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (almost 900 MB):

1. Set up [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
2. Run the script: `sh ./get_data.sh`
3. Set the input file: `export JINA_DATA_FILE='data/input.txt'`
4. Set the number of docs to index `export JINA_MAX_DOCS=30000` (or whatever number you prefer. The default is `50`)
5. Index your new dataset: `python app.py -t index`

If you are using a subset of the data (less then 30,000 documents) we recommend you shuffle the data. This is because the input file is ordered alphabetically, and Jina indexes from the top down. So without shuffling, your index may contain unrepresentative data, like this:

```
0.000123, which corresponds to a distance of 705 Mly, or 216 Mpc.
000webhost is a free web hosting service, operated by Hostinger.
0010x0010 is a Dutch-born audiovisual artist, currently living in Los Angeles.
0-0-1-3 is an alcohol abuse prevention program developed in 2004 at Francis E. Warren Air Force Base based on research by the National Institute on Alcohol Abuse and Alcoholism regarding binge drinking in college students.
0.01 is the debut studio album of H3llb3nt, released on February 20, 1996 by Fifth Colvmn Records.
001 of 3 February 1997, which was signed between the Government of the Republic of Rwanda, and FAPADER.
003230 is a South Korean food manufacturer.
```

On Linux, you can shuffle using the [`shuf` command](https://linuxhint.com/bash_shuf_command/):

```bash
shuf input.txt > input.txt
```

To shuffle a file on macos, please read [this post](https://apple.stackexchange.com/questions/142860/install-shuf-on-os-x/195387).


## 🔮 Overview of the files in this example
Here is a small overview if you're interested in understanding what each file in this example is doing. 

📂 `test/*`   Various maintenance tests to keep the example running.   

📃 `app.py`    The gateway code to that runs the index & query Flow.  

📃 `indexer.py`    Indexing executor code that uses numpy to aggregate embeddings.

📃 `transformer.py`    Encoding executor code using transformer model.  


📃 `get_data.sh`    Downloads the Kaggle dataset. 

📃 `manifest.yml`      Needed to deploy to Jina Hub.

📃 `requirements.txt`    Contains all required python libraries.


## 🌀 Flow diagram

This diagram provides a visual representation of the flow in this example, showing which Executors are used in which order.
![wiki_flow](https://user-images.githubusercontent.com/22567795/119640719-7930d480-be4b-11eb-8566-83ba068aa05b.jpeg)

## 🔨 Next steps, building your own app

Did you like this example and are you interested in building your own? For a detailed tuturial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation.

- [Enable querying while indexing](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences-query-while-indexing)

## 🐳 Deploy the prebuild application using Docker
Warning! This section is not maintained, so we can't guarantee it works! 
 
If you want to run this example quickly without installing Jina, you can do so via Docker. If you'd rather build the example yourself, return to the Python instructions above.  

### Requirements:
1. You have Docker installed and working. 
2. You have at least 8 GB of free space on your hard drive. 

### Step 1. Pull the prebuild image from Docker hub and run
We begin by running the following Docker command in the terminal. This will pull the prebuilt Docker image from Docker Hub and begin downloading the required files and data. To increase speed, this example only has 30,000 sentences indexed. 

```sh
docker run -p 45678:45678 jinahub/app.example.wikipedia-sentences-30k:0.2.10-1.0.10
```

### Step 2. Query the data
There are several ways for you to query data in Jina; for this example, we will use a CURL command interface. You should open another terminal window and paste the following command.

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```
For a quick explanation of what some of these parameters mean, `top_k` tells the system how many documents to return. The `data` parameter contains the text input you want to query. 

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar documents to the text input you provided in the data field. Feel free to alter the text in the data field and play around with other queries!

## 🙍 Community

- [Slack channel](https://slack.jina.ai/) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## 🦄 License

Copyright (c) 2021 Jina AI Limited. All rights reserved.
Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/examples#license) for the full license text.