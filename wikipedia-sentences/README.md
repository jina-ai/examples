# Semantic Wikipedia Search with Transformers and DistilBERT

![](https://docs.jina.ai/_images/jinabox-wikipedia.gif)


## Table of contents: 
- [Overview](#overview)
- [🐍 Build it yourself and deploy with Python](#---build-it-yourself-and-deploy-with-python)
  * [Pre requirements:](#pre-requirements-)
  * [Step 1. Clone the repo and install Jina](#step-1-clone-the-repo-and-install-jina)
  * [Step 2. Indexing your data](#step-2-indexing-your-data)
  * [Step 3. 🔍 Search your data](#step-3----search-your-data)
- [Overview of the files in this example](#overview-of-the-files-in-this-example)
- [Flow diagram](#flow-diagram)
- [Next steps, building your own app](#next-steps--building-your-own-app)
- [🐳 Deploy the prebuild application using Docker](#---deploy-the-prebuild-application-using-docker)
  * [Pre-requirements:](#pre-requirements-)
  * [Step 1. Pull the prebuild image from Docker hub and run](#step-1-pull-the-prebuild-image-from-docker-hub-and-run)
  * [Step 2. Query the data](#step-2-query-the-data)
- [Community](#community)
- [License](#license)

# Overview
|  |  |
| ------------- | ------------- |
| Summary | This showcases a semantic text search app |
| Data for indexing | Wikipedia corpus |
| Data for querying | A text sentence  |
| Dataset used |  Kaggle Wikipedia corpus     |
| ML model used | Distilbert |

This example shows you how to build a simple semantic search app powered by [Jina](http://www.jina.ai)'s neural search framework. You can index and search text sentences from Wikipedia using a state of art machine learning  [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) language model from the [Transformers](https://huggingface.co) library.

# 🐍 Build the app with Python

These instructions explain how to build the example yourself and deploy it with Python. If you want to skip the building skips and just run the app, check out the Docker section below.  

## Pre requirements:
1. You have a working Python 3.8 environment. 
2. We recommend creating a [new python virtual envoriment](https://docs.python.org/3/tutorial/venv.html) to have a clean install of Jina and prevent dependency clashing.   
3. You have at least 8GB of free space on your hard drive. 


## Step 1. Clone the repo and install Jina

Begin by cloning the repo so you can get the required files and datasets, and entering the correct folder. 
```sh
git clone https://github.com/jina-ai/examples
cd examples/wikipedia-sentences
```

On your terminal,  you should now be located in you the wikipedia-sentences folder. Let's install Jina and the other required python libraries. For futher information on installing Jina check out [documentation](https://docs.jina.ai/chapters/core/setup/). 

```sh
pip install -r requirements.txt
```
If this command runs without any error messages, you can then move onto step two. 

## Step 2. Indexing your data
To make life a little easier for you, you can begin by indexing a very [small dataset of 50 sentences](data/toy-input.txt)  to make sure everything is working correctly. 

```sh
python app.py -t index
```
If you see the following command, it means your data has been correctly indexed. 
```sh
Flow@5162[S]:flow is closed and all resources are released, current build level is 0
```

We recommend you come back to this step later and index the full wikipedia sentence for better results. 

To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (almost 900 MB) follow these steps:

1. Set up a [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication) account
2. Run the script: `sh ./get_data.sh`
3. Set the input file: `export JINA_DATA_FILE='data/input.txt'`
4. Set the number of docs to index `export JINA_MAX_DOCS=30000` (or whatever number you prefer. The default is `50`)
5. Delete the old index: `rm -rf workspace`
6. Index your new dataset: `python app.py -t index`

## Step 3. 🔍 Search your data
Jina offers several different ways to search (query) your data. In this example, we show three of the most common ones. All three are optional, in a production environment, you would only choose whichever suits your use case best. 

### Using a REST API
Begin by running the following command to open the REST API interface.

```sh
python app.py -t query_restful
```

You should open another terminal window and paste the following command. For a quick explanation of what some of these parameter mean,  `top_k`  tells the system how many documents to return. The  `data`  parameter contains the text input you want to query.

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
```

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar documents to the text input you provided in the data field. Feel free to alter the text in the data field and play around with other queries!


### Using JinaBox; our frontend search interface

**JinaBox** is a light-weight, highly customizable JavaScript based front-end search interface. To use it for this example, begin by opening the REST API interface. 

```sh
python app.py -t query_restful
```

In your browser, open up the hosted JinaBox  on [jina.ai/jinabox.js](https://jina.ai/jinabox.js/).  In the configuration bar on the left hand side, choose a custom endpoint and enter the following information  `http://127.0.0.1:45678/search` . You can type in search queries into the text box on the right hand side!


### Directly from terminal
You can also easily search (query) your data directly from the terminal. Using the following command will open an interface directly in your terminal window. 

```sh
python app.py -t query
```

# Overview of the files in this example
Here is a small overview if you're interested in understanding what each file in this example is doing. 

`data/toy-input.txt` - contains a small number of sentences to test the example without downloading anything. `flows/index.yml` - contains the configuration details for indexing data. 
`flow/query.yml` - contains the configuration details for querying data. 
`pods/encode.yml` - specifies which executor should be used to encode the data. 
`pods/index.yml` - specifies which executor should be used to index and store the data. 
`test/*` - various maintenance tests to keep the example running. 
`app.py`  - the gateway code to combine the index and query flow 
`get_data.sh` - downloads the Kaggle dataset.
`manifest.yml` - needed to deploy to Jina Hub
`requirements.txt` - contains all required python libraries



# Flow diagram

Similar to the one in the pdf example. TO DO

# Next steps, building your own app

Did you like this example and are you interested in building your own? For a detailed tuturial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can always get support from our [Slack community](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) .

# 🐳 Deploy the prebuild application using Docker
If you want to run this example quickly without installing Jina, you can do so via Docker. If you'd rather build the example yourself, skip to the Python instructions below.  

## Pre-requirements:
1. You have Docker installed and working. 
2. You have at least 8GB of free space on your hard drive. 

## Step 1. Pull the prebuild image from Docker hub and run
We begin by running the following Docker command in the terminal. This will pull the prebuilt Docker image from Docker Hub and begin downloading the required file and data. To increase speed, this example only has 30,000 sentences indexed. 

```sh
docker run -p 45678:45678 jinahub/app.example.wikipedia-sentences-30k:0.2.10-1.0.10
```

If the command has worked correctly, you should see the following output....TODO

## Step 2. Query the data
There are several ways for you to query data in Jina; for this example, we will use a CURL command interface. You should open another terminal window and paste the following command. F

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```
For a quick explanation of what some of these parameters mean, `top_k` tells the system how many documents to return. The `data` parameter contains the text input you want to query. 

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar documents to the text input you provided in the data field. Feel free to alter the text in the data field and play around with other queries!

# Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

# License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.
