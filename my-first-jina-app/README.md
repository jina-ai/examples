<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Build Your First Neural Search App](#build-your-first-neural-search-app)
  - [👋 Introduction](#-introduction)
  - [🗝️ Key Concepts](#-key-concepts)
  - [🧪 Try it Out!](#-try-it-out)
  - [🐍 Install](#-install)
  - [🗃️ Work with Data](#-work-with-data)
  - [🏃 Run the Flows](#-run-the-flows)
  - [🤔 How Does it Actually Work?](#-how-does-it-actually-work)
  - [Troubleshooting](#troubleshooting)
  - [🎁 Wrap Up](#-wrap-up)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Build Your First Neural Search App

## 👋 Introduction

This tutorial guides you through building your own neural search app using the [Jina framework](https://github.com/jina-ai/jina/). Don't worry if you're new to machine learning or search. We'll spell it all out right here.

![](./images/jinabox-startrek.gif)

Our example program will be a simple neural search engine for text. It will take a user's typed input, and return a list of lines from Star Trek that match most closely.

⚠️ Need help? Check out the **[troubleshooting](#troubleshooting)** section further along.

## 🗝️ Key Concepts

First of all, read up on [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) so you have a clear understanding of how Jina works. We're going to refer to those concepts a lot. We assume you already have some knowledge of Python and machine learning.

## 🧪 Try it Out!

Before going through the trouble of downloading, configuring and testing your app, let's get an idea of the finished product. In this case, it's exactly the same as what we're building, but with lines from South Park instead:

### Deploy with Docker

Jina has a pre-built Docker image with indexed data. You can run it with:

```bash
docker run -p 45678:45678 jinaai/hub.app.distilbert-southpark
```
Note: You'll need to run the Docker image before trying the steps below

#### Query with Jinabox

[Jinabox](https://github.com/jina-ai/jinabox.js/) is a simple web-based front-end for neural search. You can see it in the graphic at the top of this tutorial.

1. Go to [jinabox](https://jina.ai/jinabox.js) in your browser
2. Ensure you have the server endpoint set to `http://localhost:45678/api/search`
3. Type a phrase into the search bar and see which South Park lines come up

**Note:** If it times out the first time, that's because the query system is still warming up. Try again in a few seconds!

#### Query with `curl`

Alternatively, you can open your shell and check the results via the RESTful API. The matched results are stored in `topkResults`.

```bash
curl --request POST -d '{"top_k": 10, "mode": "search", "data": ["text:hey, dude"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:45678/api/search'
```

You'll see the results output in JSON format. Each result looks like:

```json
{
            "matchDoc": {
              "docId": 48,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "Cartman[SEP]Hey, hey, did you see my iPad, Token?\n"
            },
            "score": {
              "value": 0.29252166,
              "opName": "MinRanker"
            }
          },
```

Now go back to your terminal and hit `Ctrl-C` a few times to ensure you've stopped Docker.

</details>

## 🐍 Install

Now that you know what we're building, let's get started!

### Prerequisites

You'll need:

* A basic knowledge of Python
* Python 3.7 or higher installed, and `pip`
* A Mac or Linux computer (we don't currently support Windows)
* 8 gigabytes or more of RAM
* Plenty of time - Indexing can take a while!

You should have also read the key concepts at the top of this page to get a good overview of how Jina and this example work.

### Clone the repo

Let's get the basic files we need to get moving:

```
git clone https://github.com/jina-ai/examples.git
cd examples/my-first-jina-app
```

### Cookiecutter

```
pip install -U cookiecutter && cookiecutter gh:jina-ai/cookiecutter-jina
```

We use [cookiecutter](https://github.com/cookiecutter/cookiecutter) to spin up a basic Jina app and save you having to do a lot of typing and setup.

For our Star Trek example, we recommend the following settings:

* `project_name`: `Star Trek` (non-default)
* `jina_version`: 0.5.5
* `project_slug`: `star_trek`
* `task_type`: `nlp` (non-default)
* `index_type`: `strings` (non-default)
* `public_port`: `65481`

Just use the defaults for all other fields.

### Files and Folders

After running `cookiecutter`, run:

```
cd star_trek
ls
```

You should see a bunch of files in the `star_trek` folder that cookiecutter created:

| File               | What it Does                                                             |
| ---                | ---                                                                      |
| `app.py`           | The main Python script where you initialize and pass data into your Flow |
| `Dockerfile`       | Lets you spin up a Docker instance running your app                      |
| `flows/`           | Folder to hold your Flows                                                |
| `pods/`            | Folder to hold your Pods                                                 |
| `README.md`        | An auto-generated README file                                            |
| `requirements.txt` | A list of required Python packages                                       |

In the `flows/` folder we can see `index.yml` and `query.yml` - these define the indexing and querying Flows for your app.

In `pods/` we see `chunk.yml`, `craft.yml`, `doc.yml`, and `encode.yml` - these Pods are called from the Flows to process data for indexing or querying.

More on Flows and Pods later!

### Install Requirements

In your terminal:

```
pip install -r requirements.txt
```

⚠️  Now we're going to get our hands dirty, and if we're going to run into trouble, this is where we'll find it. If you hit any snags, check our **[troubleshooting](#troubleshooting)** section!

## 🗃️ Work with Data

❗ **Note:** Cleaning and restructuring data is a key part of machine learning, but is outside the scope of this example. We simply download a pre-processed version of the dataset.

### Download Data

Our goal is to find out who said what in Star Trek episodes when a user queries a phrase. The [Star Trek dataset](https://www.kaggle.com/gjbroughton/start-trek-scripts) from Kaggle contains all the scripts and individual character lines from Star Trek: The Original Series all the way through Star Trek: Enterprise. We're using a subset in this example, which just contains the characters and lines from Star Trek: The Next Generation. This subset has also been converted from JSON to CSV format, which is more suitable for Jina to process.

Now let's ensure we're back in our base folder and download and the dataset by running:

```bash
source ../get_data.sh
```

<details>
  <summary>See console output</summary>

```bash
--2020-07-29 13:57:38--  https://github.com/alexcg1/startrek-startrek_tng/raw/master/startrek_tng.csv
Loaded CA certificate '/etc/ssl/certs/ca-certificates.crt'
Resolving github.com (github.com)... 13.237.44.5
Connecting to github.com (github.com)|13.237.44.5|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://raw.githubusercontent.com/alexcg1/startrek-startrek_tng/master/startrek_tng.csv [following]
--2020-07-29 13:57:39--  https://raw.githubusercontent.com/alexcg1/startrek-startrek_tng/master/startrek_tng.csv
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 151.101.164.133
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|151.101.164.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 4618017 (4.4M) [text/plain]
Saving to: ‘./star_trek/data/startrek_tng.csv’

startrek_tng.csv                               100%[=================================================================================================>]   4.40M  4.47MB/s    in 1.0s
```

</details>

⁉️  Why do we use `source`, not `sh`? This is because we're setting some environment variables. By running with `bash` or `sh` those would only be set in the sub-shell, not the shell we're working in. You can check the data path using `echo $JINA_DATA_PATH`

### Check Data

Now that `get_data.sh` has downloaded the data, let's make sure the file has everything we want:

```shell
head data/startrek_tng.csv
```

You should see output consisting of the lines spoken by the character (`What about my age?`):

```csv
The prisoners will all stand.
All present, stand and make respectful attention to honouredJudge.
Before this gracious court now appear these prisoners toanswer for the multiple and grievous savageries of their species. Howplead you, criminal?
Criminals keep silence!
You will answer the charges, criminals.
Criminal, you will read the charges to the court.
All present, respectfully stand. Q
This honourable court is adjourned. Stand respectfully. Q
Hold it right there, boy.
What about my age?
```

Note: Your character lines may be a little different. That's okay!

### Set Data Path

Now we need to tell Jina where to find the data. By default, `app.py` uses the environment variable `JINA_DATA_PATH` for this. We can simply run:

```sh
export JINA_DATA_PATH='data/startrek_tng.csv'
```

You can double check it was set successfully by running:

```sh
echo $JINA_DATA_PATH
```

⚠️  If `JINA_DATA_PATH` is empty, `app.py` is set to index only 3 sample strings, so be sure to check this!

## 🏃 Run the Flows

Now that we've got the code to load our data, we're going to dive into writing our app and running our Flows!

### Index Flow

[First](First) up we need to build up an index of our file. We'll search through this index when we use the query Flow later.

```bash
python app.py index
```

<details>
<summary>See console output</summary>

```console
index [====                ] 📃    256 ⏱️ 52.1s 🐎 4.9/s      4      batch        encoder@273512[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-2▸⚐
        encoder@273512[I]:received "index" from gateway▸crafter▸⚐
        encoder@273516[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-2▸⚐
        encoder@273525[I]:received "index" from gateway▸crafter▸encoder-head▸⚐
      chunk_idx@273529[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-2▸encoder-tail▸⚐
      chunk_idx@273537[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-2▸encoder-tail▸chunk_idx-head▸⚐
      chunk_idx@273529[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-2▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸⚐
      chunk_idx@273533[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-2▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸⚐
       join_all@273549[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-2▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸chunk_idx-tail▸⚐
       join_all@273549[I]:collected 2/2 parts of IndexRequest
index [=====               ] 📃    320 ⏱️ 71.2s 🐎 4.5/s      5      batch        encoder@273512[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-1▸⚐
        encoder@273512[I]:received "index" from gateway▸crafter▸⚐
        encoder@273516[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸⚐
        encoder@273520[I]:received "index" from gateway▸crafter▸encoder-head▸⚐
      chunk_idx@273529[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸⚐
      chunk_idx@273541[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸⚐
      chunk_idx@273529[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-2▸⚐
      chunk_idx@273533[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-2▸⚐
       join_all@273549[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-2▸chunk_idx-tail▸⚐
       join_all@273549[I]:collected 2/2 parts of IndexRequest
index [======              ] 📃    384 ⏱️ 71.4s 🐎 5.4/s      6      batch        encoder@273512[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-1▸⚐
        encoder@273516[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸⚐
      chunk_idx@273529[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸⚐
      chunk_idx@273537[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸⚐
      chunk_idx@273529[I]:received "control" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸⚐
      chunk_idx@273533[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸⚐
       join_all@273549[I]:received "index" from gateway▸crafter▸encoder-head▸encoder-1▸encoder-tail▸chunk_idx-head▸chunk_idx-1▸chunk_idx-tail▸⚐
       join_all@273549[I]:collected 2/2 parts of IndexRequest
```

</details>

Once you see this line:

```console
Flow@133216[S]:flow is closed and all resources should be released already, current build level is 0
```

You'll know indexing is complete. This may take a little while the first time, since Jina needs to download the language model and tokenizer to deal with the data. You can think of these as the brains behind the neural network that powers the search.

#### Index More Documents

To speed things along, by default Jina is set to index a maximum of 500 [Documents](https://github.com/jina-ai/jina/tree/master/docs/chapters/101#document--chunk). This is great for testing our search engine works, but not so good for searching through every little piece of data.

Once we've verified everything works, we can set it to `50000` (or any number less than `62605`) to index many more lines of the dataset:

```sh
export MAX_DOCS=50000
```

### Search Flow

Run:

```bash
python app.py search
```

After a while you should see the console stop scrolling and display output like:

```console
Flow@85144[S]:flow is started at 0.0.0.0:65481, you can now use client to send request!
```

⚠️  Be sure to note down the port number. We'll need it for `curl` and jinabox! In our case we'll assume it's `65481`, and we use that in the below examples. If your port number is different, be sure to use that instead.

ℹ️  `python app.py search` doesn't pop up a search interface - for that you'll need to connect via `curl`, Jinabox, or another client.

### Searching Data

Now that the app is running in search mode, we can search from the web browser with Jinabox or from the terminal with `curl`:

#### Jinabox

![](./images/jinabox-startrek.gif)

1. Go to [jinabox](https://jina.ai/jinabox.js) in your browser
2. Ensure you have the server endpoint set to `http://localhost:65481/api/search`
3. Type a phrase into the search bar and see which Star Trek lines come up

#### Curl

`curl` will spit out a *lot* of information in JSON format - not just the lines you're searching for, but all sorts of metadata about the search and the lines it returns. Look for the lines starting with `"matchDoc"` to find the matches.

```bash
curl --request POST -d '{"top_k":10,"mode":"search","data":["picard to riker"]}' -H 'Content-Type: application/json' 'http://0.0.0.0:65481/api/search'
```

You should see a lot of console output, but each result will will look similar to:

```json
{
            "matchDoc": {
              "docId": 421,
              "weight": 1.0,
              "mimeType": "text/plain",
              "text": "WORF!Vessel unknown, configuration unknown, sir.\n"
            },
            "score": {
              "value": 0.748656,
              "opName": "BiMatchRanker"
            }
          },
```

Congratulations! You've just built your very own search engine!

## 🤔 How Does it Actually Work?

This is where we dive deeper to learn what happens inside each Flow and how they're built up from Pods.

### Flows

<img src="https://raw.githubusercontent.com/jina-ai/jina/master/docs/chapters/101/img/ILLUS10.png" width="30%" align="left">

As you can see in [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101), just as a plant manages nutrient flow and growth rate for its branches, a Flow manages the states and context of a group of Pods, orchestrating them to accomplish one task. Whether a Pod is remote or running in Docker, one Flow rules them all!

We define Flows in `app.py` to index and query the content in our Star Trek dataset.

In this case our Flows are written in YAML format and loaded into `app.py` with:

```python
from jina.flow import Flow

<other code here>

def index():
    f = Flow.load_config('flows/index.yml')
```

It really is that simple! Alternatively you can build Flows in `app.py` itself [without specifying them in YAML](https://docs.jina.ai/chapters/flow/index.html).

#### Indexing

Every Flow has well, a flow to it. Different Pods pass data along the Flow, with one Pod's output becoming another Pod's input. Look at our indexing Flow as an example:

<p align="center">
<img src="images/flow-index.png">
</p>

If you look at `startrek_tng.csv` you'll see it's just one big text file. Our Flow will process it into something more suitable for Jina, which is handled by the Pods in the Flow. Each Pod performs a different task.

Jina 101, discusses [Documents and Chunks](https://github.com/jina-ai/jina/tree/master/docs/chapters/101#document--chunk). In our indexing Flow, we:

* Break our giant text file into sentences. We'll regard each sentence as a Document (For simplicity in this example, one sentence = one Document = one Chunk)
* Encode each sentence, as a Chunk, into a vector (in this case, using a Pod which specifies `distilbert` from the [🤗Transformers library](https://huggingface.co/transformers))
* Build indexes for each Chunk and Document for fast lookup
* Store the vectors in our indexes

Our Pods perform all the tasks needed to make this happen:

| Pod             | Task                                                 |
| ---             | ---                                                  |
| `crafter`       | Split the Document into Chunks                       |
| `encoder`       | Encode each Chunk into a vector                      |
| `chunk_idx`     | Build an index of Chunks                             |
| `doc_idx`       | Store the Document content                           |
| `join_all`      | Join the `chunk_idx` and `doc_idx` pathways          |


##### Diving into `index.yml`

For indexing, we define which Pods to use in `flows/index.yml`. Earlier, cookiecutter created some YAML files in `flows/` for us to start with. Let's break them down, starting with indexing:

<table>
<tr>
<th scope="col">
Code
</td>
<th scope="col">
What it does
</td>
</tr>
<tr>
<td>

```yaml
!Flow
  with:
  logserver: true
```

</td>
<td>

Starts the Flow and enables the logserver. We could monitor the Flow with [Jina Dashboard](https://github.com/jina-ai/dashboard) if we wanted.

</td>
</tr>
<tr>
<td>

```yaml
pods:
  crafter:
    yaml_path: pods/craft.yml
    read_only: true
```

</td>
<td>

Starts our Pods section, and specifies our first Pod, named `crafter` which is defined in `pod/craft.yml`. `pods/craft.yml` is another YAML file which specifies the Pod's [Executor](https://github.com/jina-ai/jina/tree/master/docs/chapters/101#executors) and other attributes.

</td>
</tr>
<tr>
<td>

```yaml
  encoder:
    yaml_path: pods/encode.yml
    parallel: $JINA_PARALLEL
    timeout_ready: 600000
    read_only: true
```

</td>
<td>

This code specifies:

* The encoder Pod and its path
* Replicas for parallel processing
* Timeout limits
* Read-only attribute, so the Pod can't adjust the input data

</td>
</tr>
<tr>
<td>

```yaml
  chunk_idx:
    yaml_path: pods/chunk.yml
    parallel: $JINA_SHARDS
    separated_workspace: true
```

</td>
<td>

Similar to the above, but includes the `separated_workspaces` attribute which forces each shard to store it's data in its own dedicated directory.

</td>
</tr>
<td>

```yaml
  doc_idx:
    yaml_path: pods/doc.yml
    needs: gateway
```

</td>
<td>

This Pod specifies prerequisites, namely the `gateway` Pod. We can see this in the Flow diagram above.

</td>
</tr>
<tr>
<td>

```yaml
  join_all:
    yaml_path: _merge
    needs: [doc_idx, chunk_idx]
```

</td>
<td>

`join_all` looks like just another Pod - but what's with the `_merge` path? This is a built-in YAML that merges all the messages that come in from the Pods `needs`.

</td>
</tr>
</table>

So, is that all of the Pods? Not quite! We always have another Pod working in silence - the `gateway` pod. Most of the time we can safely ignore it because it basically does all the dirty orchestration work for the Flow.

With all these Pods defined in our Flow, we're all set up to index all the character lines in our dataset.

#### Querying

Just like indexing, the querying Flow is also defined in a YAML file. Much of it is similar to indexing:

<table>
<tr>
<td>

![](images/flow-query.png)

</td>
<td>

```yaml
!Flow
with:
  read_only: true  # better add this in the query time
  rest_api: true
  port_grpc: $JINA_PORT
pods:
  chunk_seg:
    yaml_path: pods/craft.yml
    parallel: $JINA_PARALLEL
  tf_encode:
    yaml_path: pods/encode.yml
    parallel: $JINA_PARALLEL
    timeout_ready: 600000
  chunk_idx:
    yaml_path: pods/chunk.yml
    shards: $JINA_SHARDS
    separated_workspace: true
    polling: all
    reducing_yaml_path: _merge_topk_chunks
    timeout_ready: 100000 # larger timeout as in query time will read all the data
  ranker:
    yaml_path: BiMatchRanker
  doc_idx:
    yaml_path: pods/doc.yml
```

</td>
</tr>
</table>

In indexing we have to break down the Document into Chunks and index it. For querying we do the same, regarding the query as a Document, and we can use many of the same Pods. There are a few differences though:

So, in the query Flow we've got the following Pods:

| Pod             | Task                                                 |
| ---             | ---                                                  |
| `chunk_seg`     | Segments the user query into meaningful Chunks       |
| `tf_encode`     | Encode each word of the query into a vector          |
| `chunk_idx`     | Build an index for the Chunks for fast lookup        |
| `ranker`        | Sort results list                                    |
| `doc_idx`       | Store the Document content                           |

Since many of the Pods are the same as in indexing, they share the same YAML but perform differently based on the task at hand.

#### Index vs Query

Now that both our Flows are ready for action, let's take a quick look at the differences between them:

##### Code

Compared to `index.yml`, we have some extra features in `query.yml`:

| Code                                     | Meaning                                                                  |
| ---                                      | ---                                                                      |
| `rest_api:true`                          | Use Jina's REST API, allowing clients like jinabox and `curl` to connect |
| `port_expose: $JINA_PORT`                | The port for connecting to Jina's API                                    |
| `polling: all`                           | Setting `polling` to `all` ensures all workers poll the message          |
| `reducing_yaml_path: _merge_topk_chunks` | Use `_merge_topk_chunks` to reduce result from all replicas              |
| `ranker:`                                | A Pod to rank results by relevance                                       |

##### Structures

While the two Flows share (most of) the same Pods, there are some differences in structure:

* Index has a two-pathway design which deals with both Document and Chunk indexing in parallel, which speeds up message passing
* Query has a single pipeline

##### Request Messages

In our RESTful API we set the `mode` field in the JSON body and send the request to the corresponding API:

| API endpoint | JSON
| ---          | ---                  |
| `api/index`  | `{"mode": "index"}`  |
| `api/search` | `{"mode": "search"}` |

This is how Pods in both Flows can play different roles while sharing the same YAML files.

### Pods

<img src="https://raw.githubusercontent.com/jina-ai/jina/master/docs/chapters/101/img/ILLUS8.png" width="20%" align="left">

You can think of the Flow as telling Jina *what* tasks to perform on the dataset. The Pods comprise the Flow and tell Jina *how* to perform each task, and they define the actual neural networks we use in neural search, namely the machine-learning models like `distilbert-base-cased`. (Which we can see in `pods/encode.yml`)

Jina uses YAML files to describe objects like Flows and Pods, so we can easily configure the behavior of the Pods without touching their application code.

Let's start by looking at the Pods in our indexing Flow, `flows/index.yml`. Instead of the first Pod `crafter`, let's look at `encoder` which is a bit simpler:

```yaml
pods:

  <other pods here>

  encoder:
    yaml_path: pods/encode.yml
    parallel: $JINA_PARALLEL
    timeout_ready: 600000
    read_only: true
```

The `encoder` Pod's YAML file is stored in `pods/encode.yml`:

```yaml
!TransformerTorchEncoder
with:
  pooling_strategy: cls
  model_name: distilbert-base-cased
  max_length: 96
```

We first use the built-in `TransformerTorchEncoder` as the Pod's **[Executor](https://github.com/jina-ai/jina/tree/master/docs/chapters/101#executors)**. The `with` field is used to specify the parameters we pass to `TransformerTorchEncoder`.

| Parameter          | Effect                                                 |
| ---                | ---                                                    |
| `pooling_strategy` | Strategy to merge word embeddings into chunk embedding |
| `model_name`       | Name of the model we're using                          |
| `max_length`       | Maximum length to truncate tokenized sequences to      |

All the other Pods follow similar practices. While a Flow differs based on task (indexing or searching), Pods differ based on *what* is being searched. If you're doing an image search, you'll follow similar steps to a text search (encode, chunk, index, etc) but the way you do each step is different to working with a text dataset. Therefore you'd use different Pods (although they'd have the same kinds of filename, so the Flow doesn't need to be changed to see them.)


## Troubleshooting

### Module not found error

Be sure to run `pip install -r requirements.txt` before beginning, and ensure you have lots of RAM/swap and space in your `tmp` partition (see below issues). This may take a while since there are a lot of prerequisites to install.

If this error keeps popping up, look into the error logs to try to find which module it's talking about, and then run:

```sh
pip install <module_name>
```

### My Computer Hangs

Machine learning requires a lot of resources, and if your machine hangs this is often due to running out of memory. To fix this, try [creating a swap file](https://linuxize.com/post/how-to-add-swap-space-on-ubuntu-20-04/) if you use Linux. This isn't such an issue on macOS, since it allocates swap automatically.

### `ERROR: Could not install packages due to an EnvironmentError: [Errno 28] No space left on device`

This is often due to your `/tmp` partition running out of space so you'll need to [increase its size](https://askubuntu.com/questions/199565/not-enough-space-on-tmp).

### `command not found`

For any of these errors you'll need to install the relevant software package onto your system. In Ubuntu this can be done with:

```sh
sudo apt-get install <package_name>
```

## 🎁 Wrap Up

In this tutorial you've learned:

* How to install the Jina neural search framework
* How to load and index text data from files
* How to query data with `curl` and Jinabox
* The nitty-gritty behind Jina Flows and Pods

Now that you have a broad understanding of how things work, you can try out some of more [example tutorials](https://github.com/jina-ai/examples) to build image or video search, or stay tuned for our next set of tutorials that build upon your Star Trek app.
