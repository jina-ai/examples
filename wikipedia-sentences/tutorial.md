<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Build Your First Jina App](#build-your-first-jina-app)
  - [👋 Introduction](#-introduction)
  - [🗝️ Key Concepts](#-key-concepts)
  - [🧪 Try it Out!](#-try-it-out)
  - [🐍 Install](#-install)
  - [🏃 Run the Flows](#-run-the-flows)
  - [🤔 How Does it Actually Work?](#-how-does-it-actually-work)
  - [⏭️  Next Steps](#-next-steps)
  - [🤕 Troubleshooting](#troubleshooting)
  - [🎁 Wrap Up](#-wrap-up)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Build your first Jina app

## 👋 Introduction

This tutorial guides you through building your own neural search app using the [Jina framework](https://github.com/jina-ai/jina/). Don't worry if you're new to machine learning or search. We'll spell it all out right here.

TODO
![](./images/jinabox-startrek.gif)

Our example program will be a simple neural search engine for text. It will take a user's typed input, and return a list of sentences from Wikipedia that match most closely.

When you're finished, you'll have recreated our [wikipedia sentence search example](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences) from scratch and have a better understanding of how things work in Jina.

⚠️ Need help? Check out the **[troubleshooting](#troubleshooting)** section further along.

## 🗝️ Key concepts

TODO urls

- **[What is Neural Search?]()** See how Jina's search is different from the traditional way
- **[Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101)**: Get an idea of Jina's core components
- **[Jina 102](https://github.com/jina-ai/jina/tree/master/docs/chapters/102)**: See how Jina's components are wired together

## 🧪 Try it out!

Before going through the trouble of downloading, configuring and testing your app, let's get an idea of the finished product: 

### Run with Docker

```sh
docker run --name wikipedia-search -p 45678:45678 jinahub/app.example.wikipedia-sentences-30k:0.2.8-0.9.23
```
Note: You'll need to run the Docker image before trying the steps below

### Search the data

#### With Jina Box

[Jinabox](https://github.com/jina-ai/jinabox.js/) is a simple web-based front-end for neural search. You can see it in the graphic at the top of this tutorial.

1. Go to [Jina Box](https://jina.ai/jinabox.js) in your browser
2. Ensure you have the server endpoint set to `http://127.0.0.1:45678/api/search`
3. Type a phrase into the search bar and see which Wikipedia sentences come up

**Note:** If it times out the first time, that's because the query system is still warming up. Try again in a few seconds!

#### With `curl`

```sh
curl --request POST -d '{"top_k":10,"mode":"search","data":["middle east"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```

`curl` will output a *lot* of information in JSON format - not just the lines you're searching for, but also metadata about the search and the Documents it returns. Look for the lines starting with `"matchDoc"` to find the matches.

After looking through the JSON you should see lines that contain the text of the Document matches:

```json
"text": "OACIS for the Middle East is a union list of serials from or about the Middle East.\n",
```

ℹ️  You likely won't see the above match, since we use a random subset of the dataset (you can see the shuffling and cutting in [`get-data.sh`](./get-data.sh))
ℹ️  There's a LOT of other data too, but its all metadata and not strictly relevant to the output a user would want to see.

### Shut down Docker

Start a new terminal window and run:

```sh
docker stop wikipedia-search
```

To cleanly exit the Docker container

## 🐍 Build your app

### Prerequisites

* Linux or macos (or see [instructions to install Jina on Windows](https://docs.jina.ai/chapters/install/os/via-pip.html#on-windows))
* Basic knowledge of Python
* Python 3.7 or higher, and `pip`
* 8 gigabytes or more of RAM

### Create a virtualenv and install Jina

A virtualenv will ensure your system libraries and project libraries don't conflict or interfere with each other.

```sh
mkdir my_jina_app
cd my_jina_app
virtualenv env
source /env/bin/activate
```

Now you can install Jina in this clean environment:

```sh
pip install jina[hub]==1.0
```

TODO
Above we are only specifying to install [Jina Hub]() - this is because Hub contains the wizard to create a new Jina app.

After this tutorial, when you need to escape your virtualenv, just run:

```sh
deactivate
```

### Create a new app

```sh
jina hub new --type=app
```

We recommend the following settings:

| Parameter                   | What to type                                          |
| ---                         | ---                                                   |
| `project_name`              | `Wikipedia sentence search`                           |
| `jina_version`              | Use default setting                                   |
| `project_slug`              | Use default setting                                   |
| `author_name`               | Your name                                             |
| `project_short_description` | `Search Wikipedia sentences using Jina neural search` |
| `task_type`                 | `2` (NLP)                                             |
| `index_type`                | `2` (strings)                                         |
| `public_port`               | Use default setting                                   |
| `parallel`                  | Use default setting                                   |
| `shards`                    | Use default setting                                   |
| `version`                   | Use default setting                                   |

TODO
After answering all the questions, the wizard will create [a folder and files](https://docs.google.com/document/d/1A2t-K2DEZvJ7sOmWLuCmUQINyESaxucM7wOJCSCPmdI/edit#) for your new Jina app.

### Install app requirements

In your terminal:

```sh
cd wikipedia_sentence_search
pip install -r requirements.txt
```

### Download data (optional)

Our goal is to search a set of sentences from Wikipedia and return the closest sentences to our search term. We're using [this dataset](https://www.kaggle.com/mikeortman/wikipedia-sentences) from Kaggle.

By default we include a [subset of this data](/data/toy-input.txt), so you don't need to download anything. However, if you'd like to work with more sentences:

To get the data, you'll need to 

1. Set up [Kaggle](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
2. `wget https://raw.githubusercontent.com/jina-ai/examples/master/wikipedia-sentences/get_data.sh`
3. `sh ./get_data.sh`

The `get_data.sh` script:

- Creates a data directory
- Downloads the dataset from Kaggle
- Extracts and shuffles the dataset to ensure some variety in what we ask Jina to search

Since `app.py` indexes `data/toy-input.txt` by default, we'll override it with an environment variable

```sh
export JINA_DATA_FILE='data/input.txt'
```

You can double check it was set successfully by running:

```sh
echo $JINA_DATA_FILE
```

## 🏃 Run your app

In section you will index and search through your data

### Index Flow

First up we need to build up an index of our dataset, which we'll later search with our search Flow.

```sh
python app.py -t index
```

You'll see a lot of output scrolling by. Indexing is complete when you see:

```sh
Flow@58199[S]:flow is closed and all resources should be released already, current build level is EMPTY
```

This may take longer the first time, because Jina needs to download the language model and tokenizer to process the dataset. You can think of these as the brains that power the search.

### Search Flow

Run:

```bash
python app.py -t query_restful
```

After a while you should see the console stop scrolling and display output like:

```console
        🖥️ Local access         http://0.0.0.045678
        🔒 Private network:     http://192.168.1.68:45678
        🌐 Public address:      http://81.37.167.157:45678
```

Your search engine is now ready to run!

⚠️  Be sure to note down the port number. You'll need it for `curl` and the Jina Box frontend! In our case we can see it's `45678`.

ℹ️  `python app.py query_restful` doesn't pop up a search interface - for that you'll need to connect via `curl`, Jinabox, or another client. Alternatively run `python app.py query` to search from your terminal

### Searching Wikipedia sentences

See our section on [searching the data](#search-the-data).

When you're finished, you can stop the search Flow with Ctrl-C (or Command-C on a Mac).

## 🤔 How does it work?

Let's dive deeper to learn what happens inside our Flows and how they're built up from Pods.

### Flows

<img src="https://raw.githubusercontent.com/jina-ai/jina/master/docs/chapters/101/img/ILLUS10.png" width="30%" align="left">

As you can see in [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101), just as a plant manages nutrient flow and growth rate for its branches, Jina's Flow manages the states and context of a group of Pods, orchestrating them to accomplish one specific task. 

We define Flows in `app.py` to index and query our dataset:

```python
from jina.flow import Flow

<other code here>

def index():
    f = Flow.load_config('flows/index.yml')

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None)) # Set data path
        f.index_lines(filepath=data_path, batch_size=16, read_mode='r', size=num_docs) # Set mode (index_lines) and indexing settings
```

Then to start the Flow, we just run `python app.py -t <flow_name>`, in this case:

```sh
python app.py -t index
```

ℹ️  The `-t` is short for for `--task`
ℹ️  Alternatively you can build Flows in `app.py` itself [without specifying them in YAML](https://docs.jina.ai/chapters/flow/index.html) or with [Jina Dashboard](http://dashboard.jina.ai)

#### Indexing

Every Flow is defined in its own YAML fie.

`input.txt` is just one big text file. Our Flow will process it into something more suitable for Jina, which is handled by the Pods in the Flow. Each Pod performs a different task, with one Pod's output becoming another Pod's input. 

Let's look at `flows/index.yml`:

```yaml
!Flow
version: '1'
pods:
  - name: encoder
    uses: pods/encode.yml
    timeout_ready: 1200000
    read_only: true
  - name: indexer
    uses: pods/index.yml
```

Each Pod performs a different operation on the dataset:

| Pod       | Task                                                       |
| ---       | ---                                                        |
| `encoder` | Encode each input Document into a vector                   |
| `indexer` | Build an index of the vectors and metadata key-value pairs |

Different use cases would use different Pods in their Flows. An example would be a `crafter` Pod to break a Document down into sentences. (This example doesn't need such a Pod because each input is already just one sentence.)

#### Searching

Just like indexing, the search Flow is also defined in a YAML file, in this case at `flows/query.yml`:

```yaml
!Flow
version: '1'
with:
  read_only: true
  port_expose: $JINA_PORT
pods:
  - name: encoder
    uses: pods/encode.yml
    timeout_ready: 60000
    read_only: true
  - name: indexer
    uses: pods/index.yml
```

As in `flows/index.yml`, we use two Pods, but this time they behave differently:

| Pod       | Task                                                              |
| ---       | ---                                                               |
| `encoder` | Encode user's query into a vector                                 |
| `indexer` | Query vector index and key-value pairs; Return matching Documents |

### Pods

<img src="https://raw.githubusercontent.com/jina-ai/jina/master/docs/chapters/101/img/ILLUS8.png" width="20%" align="left">

You can think of the Flow as telling Jina *what* tasks to perform on the dataset. The [Pods]() comprise the Flow and tell Jina *how* to perform each task, and they define the actual neural networks we use in neural search, namely the machine-learning models like `distilbert-base-cased`. (Which we can see in `pods/encode.yml`)

Jina uses YAML files to describe objects like Flows and Pods, so we can easily configure the behavior without touching our application code.

Let's look at `pods/encode.yml` as an example:

```yaml
!TransformerTorchEncoder
with:
  pooling_strategy: auto
  pretrained_model_name_or_path: distilbert-base-cased
  max_length: 96
```

The built-in `TransformerTorchEncoder` is the Pod's **[Executor](https://github.com/jina-ai/jina/tree/master/docs/chapters/101#executors)** TODO url. The `with` field specifies the parameters we pass to `TransformerTorchEncoder`.

| Parameter                       | Effect                                                     |
| ---                             | ---                                                        |
| `pooling_strategy`              | Strategy to merge word embeddings into Document embeddings |
| `pretrained_model_name_or_path` | Name of the model we're using                              |
| `max_length`                    | Maximum length to truncate tokenized sequences to          |

All the other Pods follow similar a similar structure.

## ⏭️  Next steps

### Improve accuracy

You may have noticed your results are not so accurate when you query your dataset. This can be fixed in several ways:

#### Index more Documents

[Download the larger dataset](), and increase `JINA_MAX_DOCS` to index more sentences. This gives the language model more data to work with: 

```sh
export JINA_MAX_DOCS=30000
```

#### Increase `max_length`

In `pods/encode.yml` increase the length of your embeddings:

```yaml
with:
  ...
  max_length: 192 # This works better for our Wikipedia dataset
```

#### Change language model

Language model performance depends on your task. If you're indexing Chinese sentences, you wouldn't use an English-language model! Jina default model for text search is [`distilbert-base-cased`](https://huggingface.co/distilbert-base-cased). [Other models](https://huggingface.co/models) may work better depending on your dataset and use case.

In `pods/encode.yml`:

```yaml
with:
  ...
  pretrained_model_name_or_path: <your model name>
```

### Simplify the code

The `crafter` Pod splits each entry of our dataset into individual sentences. Our dataset is already in sentences, so this Pod is redundant. Let's remove it:

```sh
rm -f pods/craft.yml
```

Also remove those Pods from `flows/index.yml` and `flows/query.yml`

### Enable incremental indexing

In this example, if you wanted to index more data you would need to remove your `workspace` directory and then re-index **everything** from scratch. To avoid this [we can add incremental indexing](https://github.com/jina-ai/examples/tree/master/wikipedia-sentences-incremental)

## 🤕 Troubleshooting

### Module not found error

- Run `pip install -r requirements.txt`
- Ensure you have enough RAM/swap and space in your `tmp` partition (see below issues)

### My Computer Hangs

Machine learning requires a lot of resources. If your computer hangs this may be because it's run out of memory. To fix this, try [creating a swap file](https://linuxize.com/post/how-to-add-swap-space-on-ubuntu-20-04/) if you use Linux. This is less of an issue on macOS, since it allocates swap automatically.

## 🎁 Wrap up

In this tutorial you've learned:

* How to install Jina's neural search framework
* How to load and index text data from files
* How to query data with `curl` and Jina Box
* The details behind Jina Flows and Pods

Now you have a broad understanding of how things work. Nexy you can look at more [examples](https://github.com/jina-ai/examples) to build [image](https://github.com/jina-ai/examples/tree/master/pokedex-with-bit) or [video](https://github.com/jina-ai/examples/tree/master/tumblr-gif-search) search, or see a [more advanced text search example](https://github.com/jina-ai/examples/tree/master/multires-lyrics-search).
