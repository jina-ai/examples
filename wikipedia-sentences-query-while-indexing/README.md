# Querying While Indexing in the Wikipedia Search Example

| About this example: |  |
| ------------- | ------------- |
| Learnings | How to configure Jina for querying while indexing |
| Used for indexing | Text data |
| Used for querying | Text data |
| Dataset used | [Wikipedia dataset from kaggle](https://www.kaggle.com/mikeortman/wikipedia-sentences) |
| Model used | [distilbert-base-cased](https://huggingface.co/distilbert-base-cased) |

This is an example of using [Jina](http://www.jina.ai) to support both querying and indexing simultaneously in our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences). 

## Table of contents: 

  * [Prerequisites](#prerequisites)
  * [What is querying while indexing?](#what-is-querying-while-indexing)
  * [Configuration changes](#configuration-changes)
  * [🐍 Build the app with Python](#-build-the-app-with-python)
  * [Flow diagrams](#flow-diagrams)
  * [🔮 Overview of the files](#-overview-of-the-files)
  * [Troubleshooting](#troubleshooting)
  * [⏭️ Next steps](#-next-steps)
  * [👩‍👩‍👧‍👦 Community](#-community)
  * [🦄 License](#-license)

## Prerequisites

- Run and understand our [Wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences)

## What is querying while indexing?

Querying while indexing means you are able to still query your data while new data is simultaneously being inserted (or updated, or deleted).
Jina achieves this with its the dump-reload feature.
For more in-depth technical information about how Jina achieves this, refer to [the docs](https://docs.jina.ai/chapters/dump-reload/)

## Configuration changes

This feature requires you to split the Flow, one for Indexing (and Updates, Deletes) and one for Querying, and have them running at the same time.
Also, you will need to replace the indexers in Flows.
The Index Flow (also referred to as the DBMS Flow) will require a `DBMSIndexer`, while the Query Flow will require `QueryIndexer`.
In our case we use `BinaryPbDBMSIndexer` and `CompoundQueryExecutor` (made up of `BinaryPbQueryIndexer` and `NumpyQueryIndexer`).
These are the standard Indexers provided by Jina, but we also provide:

- [PostgreSQLDBMSIndexer](https://github.com/jina-ai/jina-hub/tree/master/indexers/dbms/PostgreSQLIndexer), which leverages the resilience of PostgreSQL as a storage engine
- [AnnoyQueryIndexer](https://github.com/jina-ai/jina-hub/tree/master/indexers/query/AnnoyQueryIndexer), which uses the [`annoy`](https://github.com/spotify/annoy) algorithm to provide faster query results

You can check the `flows` and `pods` directories for the changes to the files.
_____

## 🐍 Build the app with Python

These instructions explain how to run the example yourself and deploy it with Python. 

### 🗝️ Requirements

1. Have a working Python 3.7 or 3.8 environment.
1. We recommend creating a [new Python virtual environment](https://docs.python.org/3/tutorial/venv.html) to have a clean installation of Jina and prevent dependency conflicts.   
1. Have at least 2 GB of free space on your hard drive.

### Running the example

### 👾 Step 1. Clone the repo and install Jina

Begin by cloning the repo so you can get the required files and datasets. (If you already have the examples repository on your machine make sure to fetch the most recent version)

```sh
git clone https://github.com/jina-ai/examples
````

And enter the correct folder:

```sh
cd examples/wikipedia-sentences-query-while-indexing
```

In your terminal, you should now be located in you the *wikipedia-sentences-query-while-indexing* folder. Let's install Jina and the other required Python libraries. For further information on installing Jina check out [our documentation](https://docs.jina.ai/chapters/core/setup/).

```sh
pip install -r requirements.txt
```

In order to run the example you will need to do the following:

### 📥 Step 2. Download your data to search (Optional)

The repo includes a small subset of the Wikipedia dataset, for quick testing. You can just use that. 

If you want to use the entire dataset, run `bash get_data.sh` and then modify the `DATA_FILE` constant (in `app.py`) to point to that file.

### 🏃 Step 3. Running the Flows

1. In one terminal session, run the command `jinad`.

    `JinaD` is our platform for running Jina services (Flows, Pods) remotely, wherever you want to run them. In this example, we use `JinaD` to serve the two Flows (Index and Query). You can read more about it [in the docs](https://docs.jina.ai/chapters/remote/jinad).

2. In another terminal, run `python app.py -t flows`

    This will create the two Flows, and then repeatedly do the following, every 20 seconds:

    1. Index 5 Documents
    2. Send a `DUMP` request to the DBMS (Index) Flow to dump its data to a specific location
    3. Send a `ROLLING_UPDATE` request to the Query Flow to take down its Indexers and start them again, with the new data located at the respective path
    
    **Notice** the logs of the operations.

    **Warning**: the data file is limited to 200 documents. Once that is exhausted, the process will terminate. If you want to use the entire dataset, run `bash get_data.sh` and then modify the `DATA_FILE` constant to point to that file.

### 🔎 Step 4: Query your data

Finally, in a third terminal, run `python app.py -t client`

This will prompt you for a query, send the query to the Query Flow, and then show you the results.

**Notice** how the number of total matches grows as step **2** from above gets repeated.

Alternatively, you can query the REST API with whatever client you are comfortable with, `cURL`, `Postman` etc.
The query format is as follows:

```sh
curl -X POST -d '{"data": [{"text":"hello world"}]}' http://0.0.0.0:9001/search
```

Optionally, if you have [`jq`](https://stedolan.github.io/jq/), you can just get the text of the matches of the query:

```sh
curl -X POST -d '{"data": [{"text":"hello world"}]}' http://0.0.0.0:9001/search | jq -r '.search.docs[] | .matches[] | .text'
```

## Flow diagrams

Below you can see a graphical representation of the Flow pipeline:

#### DBMS Flow

![](.github/images/DBMS.png)

#### Query Flow

![](.github/images/QUERY.png)

Notice the following:

- the encoder has the same configuration
- the Query Flow uses replicas. One replica continues to serve requests while the other is being reloaded.
- the Indexer in the Query Flow is actually made up of two Indexers: one for vectors, one for Document metadata. On the DBMS Flow, this data is stored into one DBMS Indexer.

## 🔮 Overview of the files

| File or folder |  Contents |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 📂 `data/`      | Folder where the data files are stored   |
| 📂 `flows/`          | Folder to store Flow configuration                                                                               |
| --- 📃 `dbms.yml`     | YAML file to configure DBMS (Index) Flow                                                                             |
| --- 📃 `query.yml`     | YAML file to configure Querying Flow                                                                             |
| 📂 `pods/`           | Folder to store Pod configuration                                                                                |
| --- 📃 `dbms_indexer.yml`   | YAML file to configure the DBMS Indexer                                                                               |
| --- 📃 `encoder.yml`   | YAML file to configure encoder Pod                                                                               |
| --- 📃 `query_indexer.yml`   | YAML file to configure the Query Indexer                                                                               |
| 🐍 `app.py`      | Code file for the example   |


## Troubleshooting

1. When running `jinad` from a virtual environment, make sure it points to the same installation as `jina`.
2. On some Mac machines, you may have to run `jinad` with `sudo` command.

_________

## ⏭️ Next steps

Did you like this example and are you interested in building your own? For a detailed tutorial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can always get support from our [Slack community](https://slack.jina.ai) .

## 👩‍👩‍👧‍👦 Community

- [Slack channel](https://slack.jina.ai) - a communication platform for developers to discuss Jina.
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities.
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`.  
- [Company](https://jina.ai) - know more about our company. We are fully committed to open-source!

## 🦄 License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.
