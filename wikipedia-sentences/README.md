
# Semantic Wikipedia Search with Transformers and DistilBERT

![](https://docs.jina.ai/_images/jinabox-wikipedia.gif)


## Table of contents: 

- [Overview](#overview)
- [🐍 Build the app with Python](#-build-the-app-with-python)
- [🔮 Overview of the files in this example](#-overview-of-the-files-in-this-example)
- [🌀 Flow diagram](#-flow-diagram)
- [🔨 Next steps, building your own app](#-next-steps-building-your-own-app)
- [🐳 Deploy the prebuild application using Docker](#-deploy-the-prebuild-application-using-docker)
- [🙍 Community](#-community)
- [🦄 License](#-license)


## Overview
|  |  |
| ------------- | ------------- |
| Summary | This showcases a semantic text search app |
| Data for indexing | Wikipedia corpus |
| Data for querying | A text sentence  |
| Dataset used |  [Kaggle Wikipedia corpus](kaggle.com/mikeortman/wikipedia-sentences)     |
| ML model used |  [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) |

This example shows you how to build a simple semantic search app powered by [Jina](http://www.jina.ai)'s neural search framework. You can index and search text sentences from Wikipedia using a state-of-the-art machine learning  [`distilbert-based-uncased`](https://huggingface.co/distilbert-base-uncased) language model from the [Transformers](https://huggingface.co) library.

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

### 🏃 Step 2. Indexing your data
To quickly get started, you can index a [small dataset of 50 sentences](data/toy-input.txt)  to make sure everything is working correctly. 

```sh
python app.py -t index
```
The relevant Jina code to index data given your Flow's YAML definition breaks down to
```python
with Flow().load_config('flows/index.yml'):
    f.index_lines(filepath='data/toy-input.txt', read_mode='r', batch_size=16, num_docs=10)
```
The Flow will interpret each line in the txt file as one Document.
You can limit the number of indexed Documents with the `num_docs`
argument. If you see the following output, it means your data has been correctly indexed.
```sh
Flow@5162[S]:flow is closed and all resources are released, current build level is 0
```

We recommend you come back to the indexing step later and run the full wikipedia dataset for better results. To index the [full dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) (almost 900 MB) follow these steps:

<details>
  <summary>Click to expand!</summary>
  
1. Set up a [Kaggle.com](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication) account
2. Install the [Kaggle Python library](https://github.com/Kaggle/kaggle-api#installation) and set up your [API credentials](https://github.com/Kaggle/kaggle-api#api-credentials)
3. Run the script: `sh ./get_data.sh`
4. Set the input file: `export JINA_DATA_FILE='data/input.txt'`
5. Set the number of docs to index `export JINA_MAX_DOCS=30000` (or whatever number you prefer. The default is `50`)
6. Delete the old index: `rm -rf workspace`
7. Index your new dataset: `python app.py -t index`

If you are using a subset of the data (less than 30,000 documents) we recommend you shuffle the data. This is because the input file is ordered alphabetically, and Jina indexes from the top down. So without shuffling, your index may contain unrepresentative data, like this:

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

To shuffle a file on macOS, please read [this post](https://apple.stackexchange.com/questions/142860/install-shuf-on-os-x/195387).

</details>


### Step 3. 🔍 Search your data
Jina offers several ways to search (query) your data. In this example, we show three of the most common ones. All three are optional, in a production environment, you would only choose one which suits your use case best. 


#### Using a REST API
Begin by running the following command to open the REST API interface.

```sh
python app.py -t query_restful
```

You should open another terminal window and paste the following command. 

```sh
curl --request POST -d '{"top_k": 5, "mode": "search",  "data": ["hello world"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/search'
```

Once you run this command, you should see a JSON output returned to you. This contains the five most semantically similar Wikipedia sentences to the text input you provided in the `data` parameter. Feel free to alter the text in the 'data' parameter and play around with other queries! For a better understanding of the parameters see the table below. 
|  |  |
|--|--|
| `top_k` | Integer determining the number of sentences to return |
| `mode` | Mode to trigger in the call. See [here](https://docs.jina.ai/chapters/rest/) for more details |
| `data` | Text input to query |
 

#### Using Jina Box; our frontend search interface

**Jina Box** is a light-weight, highly customizable JavaScript based front-end search interface. To use it for this example, begin by opening the REST API interface. 

```sh
python app.py -t query_restful
```

In your browser, open up the hosted Jina Box on [jina.ai/jinabox.js](https://jina.ai/jinabox.js/). In the configuration bar on the left-hand side, choose a custom endpoint and enter the following: `http://127.0.0.1:45678/search` . You can type search queries into the text box on the right-hand side!


#### Directly from terminal
You can also easily search (query) your data directly from the terminal. Using the following command will open an interface directly in your terminal window. 

```sh
python app.py -t query
```

### Step 4. Incremental indexing (optional)
What if new data arrives that needs to be indexed? Many applications will require incremental indexing, which is a way to add new data to an index, without re-indexing the original data.
Of course, we don't want to re-calculate our index for all our data every time we add a couple of new Documents. 
For this case, Jina provides a simple and intuitive solution which we will demonstrate using a second [small dataset](data/toy-input-incremental.txt).
Just as before, index the [first dataset](data/toy-input.txt) and then *incrementally* the [second dataset](data/toy-input-incremental.txt)
```python
with Flow().load_config('flows/index.yml'):
    f.index_lines(filepath='data/toy-input.txt', read_mode='r', batch_size=16, num_docs=10)
    f.index_lines(filepath='data/toy-input-incremental.txt', read_mode='r', batch_size=16, num_docs=10)
```
One challenge we need to address when incrementally adding new data to the index is duplication of Documents.
Jina provides a [DocCache](pods/index_cache.yml) Pod that is pre-configured for you and takes care of detecting duplicates 
when adding to the index. Finally, we add the DocCache Pod to the [index Flow](flows/index_incremental.yml). 
```yaml
!Flow
version: '1'
pods:
  - name: encoder
    uses: pods/encode.yml
    timeout_ready: 1200000
    read_only: true
  - name: indexer
    uses_before: pods/index_cache.yml  # use before indexing to detect duplicates 
    uses: pods/index.yml
```
As you can see, compared to the previous [index Flow](flows/index.yml) we just needed to add one line to the YAML spec.
To see the incremental indexing in action, run 
```shell
python app.py -t index_incremental
```

## 🔮 Overview of the files in this example
Here is a small overview if you're interested in understanding what each file in this example is doing. 
|File   | Explanation  |
|--|--|
|📂 `flows/`  | Folder to store Flow configuration    |
|--- 📃 `flows/index.yml`  | Contains the details of which Executors should be used for indexing your data. |
|--- 📃 `flows/query.yml`  | Contains the details of which Executors should be used for querying your data. |
|--- 📃 `flows/index_incremental.yml`  | Contains the details of which Pods are required for the incremental indexing. |
|📂 `pods/` | Folder to store Pod configurations|
|--- 📃 `pods/encode.yml`  | Specifies the configurations values for the encoding Executor.   |
|--- 📃 `pods/index.yml`  | Specifies the configurations values for the encoding Executor.   |
|--- 📃 `pods/index_cache.yml`  | Specifies the DocCache necessary for the incremental indexing.   |
|📂 `test/*`  | Various maintenance tests to keep the example running.   |
|📃 `app.py`   | The gateway code to combine the index and query Flow.  |
|📃 `get_data.sh`  |  Downloads the Kaggle dataset.|
|📃 `manifest.yml`   |Needed to deploy to Jina Hub.|
|📃 `requirements.txt`  |  Contains all required python libraries.|


## 🌀 Flow diagram

This diagram provides a visual representation of the two Flows in this example, showing which Executors are used in which order.

![116664240-7bad2500-a998-11eb-90fa-1d1268806602](https://user-images.githubusercontent.com/59612379/116871566-bde29a80-ac14-11eb-84d8-26b5b48dee81.jpeg)


## 🔨 Next steps, building your own app

Did you like this example and are you interested in building your own? For a detailed tutorial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 
If you have any issues following this guide, you can always get support from our [Slack community](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) .

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

