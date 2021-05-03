
# Semantic Wikipedia Search with Transformers and DistilBERT

![](https://docs.jina.ai/_images/jinabox-wikipedia.gif)


## Table of contents: 
- [Overview](#overview)
- [🐍 Build it yourself and deploy with Python](#---build-it-yourself-and-deploy-with-python)
- [Overview of the files in this example](#overview-of-the-files-in-this-example)
- [Flow diagram](#flow-diagram)
- [Next steps, building your own app](#next-steps--building-your-own-app)
- [🐳 Deploy the prebuild application using Docker](#---deploy-the-prebuild-application-using-docker)
- [Community](#community)
- [License](#license)

# Overview
|  |  |
| ------------- | ------------- |
| Summary | This showcases a semantic text search app |
| Data for indexing | Wikipedia corpus |
| Data for querying | A text sentence  |
| Dataset used |  [Kaggle Wikipedia corpus](kaggle.com/mikeortman/wikipedia-sentences)     |
| ML model used |  [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) |

This example shows you how to build a simple semantic search app powered by [Jina](http://www.jina.ai)'s neural search framework. You can index and search text sentences from Wikipedia using a state of art machine learning  [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) language model from the [Transformers](https://huggingface.co) library.

# 🐍 Build the app with Python

These instructions explain how to build the example yourself and deploy it with Python. If you want to skip the building steps and just run the app, check out the Docker section below.  

## Pre requirements:
1. You have a working Python 3.7 or 3.8 environment. 
2. We recommend creating a [new python virtual envoriment](https://docs.python.org/3/tutorial/venv.html) to have a clean install of Jina and prevent dependency conflicts.   
3. You have at least 2GB of free space on your hard drive. 


## Step 1. Clone the repo and install Jina

Begin by cloning the repo so you can get the required files and datasets.

```sh
git clone https://github.com/jina-ai/examples
cd examples/wikipedia-sentences
```

On your terminal,  you should now be located in you the wikipedia-sentences folder. Let's install Jina and the other required python libraries. For futher information on installing Jina check out our [documentation](https://docs.jina.ai/chapters/core/setup/). 

```sh
pip install -r requirements.txt
```
If this command runs without any error messages, you can then move onto step two. 

## Step 2. Indexing your data
To quickly get started, you can index a [small dataset of 50 sentences](data/toy-input.txt)  to make sure everything is working correctly. 

```sh
python app.py -t index
```
If you see the following output, it means your data has been correctly indexed. 
```sh
Flow@5162[S]:flow is closed and all resources are released, current build level is 0
```

We recommend you come back to this step later and index the full wikipedia dataset for better results. To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (almost 900 MB) follow these steps:

1. Set up a [Kaggle.com](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication) account
2. Install the [Kaggle Python library](https://github.com/Kaggle/kaggle-api#installation) and set up your [API credentials](https://github.com/Kaggle/kaggle-api#api-credentials)
3. Run the script: `sh ./get_data.sh`
4. Set the input file: `export JINA_DATA_FILE='data/input.txt'`
5. Set the number of docs to index `export JINA_MAX_DOCS=30000` (or whatever number you prefer. The default is `50`)
6. Delete the old index: `rm -rf workspace`
7. Index your new dataset: `python app.py -t index`

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

## Step 3. 🔍 Search your data
Jina offers several different ways to search (query) your data. In this example, we show three of the most common ones. All three are optional, in a production environment, you would only choose one which suits your use case best. 


### Using a REST API
Begin by running the following command to open the REST API interface.

```sh
python app.py -t query_restful
```

You should open another terminal window and paste the following command. 

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
```

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar Wikipedia sentences to the text input you provided in the 'data' parameter. Feel free to alter the text in the 'data' parameter and play around with other queries! For a better understanding of the parameters see the table below. 
|  |  |
|--|--|
| `top_k` | Integer determining the number of sentences to return |
| `mode` | Mode to trigger in the call. See [here](https://docs.jina.ai/chapters/rest/) for more details |
| `data` | Text input to query |
 




### Using JinaBox; our frontend search interface

**JinaBox** is a light-weight, highly customizable JavaScript based front-end search interface. To use it for this example, begin by opening the REST API interface. 

```sh
python app.py -t query_restful
```

In your browser, open up the hosted JinaBox on [jina.ai/jinabox.js](https://jina.ai/jinabox.js/). In the configuration bar on the left hand side, choose a custom endpoint and enter the following: `http://127.0.0.1:45678/search` . You can type in search queries into the text box on the right hand side!


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

This diagram provides a visual representation of the two Flows in this example. Showing which executors are used in which order. 

![116664240-7bad2500-a998-11eb-90fa-1d1268806602](https://user-images.githubusercontent.com/59612379/116871566-bde29a80-ac14-11eb-84d8-26b5b48dee81.jpeg)


# Next steps, building your own app

Did you like this example and are you interested in building your own? For a detailed tuturial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can always get support from our [Slack community](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) .

# 🐳 Deploy the prebuild application using Docker
If you want to run this example quickly without installing Jina, you can do so via Docker. If you'd rather build the example yourself, return to the Python instructions above.  

## Pre-requirements:
1. You have Docker installed and working. 
2. You have at least 8GB of free space on your hard drive. 

## Step 1. Pull the prebuild image from Docker hub and run
We begin by running the following Docker command in the terminal. This will pull the prebuilt Docker image from Docker Hub and begin downloading the required file and data. To increase speed, this example only has 30,000 sentences indexed. 

```sh
docker run -p 45678:45678 jinahub/app.example.wikipedia-sentences-30k:0.2.10-1.0.10
```

## Step 2. Query the data
There are several ways for you to query data in Jina; for this example, we will use a CURL command interface. You should open another terminal window and paste the following command.

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
