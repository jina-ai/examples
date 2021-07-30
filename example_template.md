# Run the EXAMPLE NAME
*You can also include a gif with a full demo of the example*


 *ADD A TABLE OF CONTENTS HERE *
 
 - [Overview](#overview)
- [🐍 Build the app with Python](#-build-the-app-with-python)
- [🔮 Overview of the files in this example](#-overview-of-the-files-in-this-example)
- [🌀 Flow diagram](#-flow-diagram)
- [🔨 Next steps, building your own app](#-next-steps-building-your-own-app)
- [🐳 Deploy the prebuild application using Docker](#-deploy-the-prebuild-application-using-docker)
- [🙍 Community](#-community)
- [🦄 License](#-license)


## Overview
| About this example: |  |
| ------------- | ------------- |
| Learnings | *Describe what the user will learn after running this example* |
| Used for indexing | *What is the datatype of the indexing input* |
| Used for querying | *What is the data type of the query input* |
| Dataset used | *Link to the datasets* |
| Model used | *Link to the model* |


## 🐍 Build the app with Python

These instructions explain how to build the example yourself and deploy it with Python. If you want to skip the building steps and just run the example with Docker, check [the Docker deployment instructions at the end of this README](#deploy-with-docker)  


### 🗝️ Requirements

*Here outline in bullet points anything the user is expected to have before diving in.* 

For example:

1. You have a working Python 3.8 environment. 
2. We recommend creating a [new Python virtual environment](https://docs.python.org/3/tutorial/venv.html) to have a clean installation of Jina and prevent dependency conflicts.   
3. You have at least 2GB of free space on your hard drive. 

### 👾 Step 1. Clone the repo and install Jina

Begin by cloning the repo, so you can get the required files and datasets. (If you already have the examples repository on your machine make sure to fetch the most recent version)

```sh
git clone https://github.com/jina-ai/examples
````

And enter the correct folder:

```sh
cd examples/example_to_use (replace as necessary)
```

In your terminal, you should now be located in you the *enter example name* folder. Let's install Jina and the other required Python libraries. For further information on installing Jina check out [our documentation](https://docs.jina.ai/chapters/core/setup/).

```sh
pip install -r requirements.txt
```

### 📥 Step 2. Download your data to search (Optional)

There are two different options here. You can either use the toy data we provide in this repo, which is quick to index but will give very poor results. Alternatively, you can download a larger dataset, which takes longer to index, but will have better results.

1. **Toy dataset:** Skip to step 3. No action is needed here.

2. **Full dataset:**
  In order to get the full dataset, follow the instructions below:
  - Register for a free [Kaggle account](https://www.kaggle.com/account/login?phase=startRegisterTab&returnUrl=%2F)
  - Set up your API token (see [authentication section of their API docs](https://www.kaggle.com/docs/api))
  - Run `pip install kaggle`
  - Run `sh get_data.sh`

### 🏃 Step 3. Index your data
In this step, we will index our data.

*Here describe the Index Flow. Be as specific as possible in describing how this Index Flow works and what is its input. You are encouraged to use code snippets, images, or whatever helps to clarify.*

```
python app.py -t index (replace as necessary)
```

If you see the following output, it means your data has been correctly indexed.

```
Flow@5162[S]:flow is closed and all resources are released, current build level is 0
```

### 🔎 Step 4: Query your data
Next, we will deploy our query Flow.

*Here describe the Query Flow. Be as specific as possible in describing how this Query Flow works and what is its input. You are encouraged to use code snippets, images, or whatever helps to clarify.*

Run the query Flow in your terminal like this:

```
python app.py -t query (replace as necessary)
``` 
______

## 📉 Understanding your results
*Here include a short description of the results and how to interpret them if needed.*

## 🌀 Flow diagram
This diagram provides a visual representation of the Flows in this example; Showing which executors are used in which order.

*Here Show the Flow for this example.*

## 📖 Optional: Extra information useful for the user

*Use this section to add extra information you think the user could benefit from.
QueryLanguage, Faiss, Annoy for example.*

## 🔮 Overview of the files

*Add a list with all folders/files in the example:*

|                      |                                                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 📂 `flows/`          | Folder to store Flow configuration                                                                               |
| --- 📃 `index.yml`     | YAML file to configure indexing Flow                                                                             |
| --- 📃 `query.yml`     | YAML file to configure querying Flow                                                                             |
| 📂 `pods/`           | Folder to store Pod configuration                                                                                |
| --- 📃 `encoder.yml`   | YAML file to configure encoder Pod                                                                               |
| 📂 `workspace/`      | Folder to store indexed files (embeddings and documents). Automatically created after the first indexing   |

_____

## 🐋 Deploy with Docker
To make it easier for you, we have built and published the Docker image for this example.

### ☑️ Requirements:

1. You have Docker installed and working.
2. You have at least 8GB of free space on your hard drive.

### 🏃🏿‍♂️ Pull and run the image
Running the following command will pull the Docker image and run it.

*Replace below with the command to run the Docker image of this example*

```bash
docker .
```

_______

## ⏭️ Next steps

Did you like this example and are you interested in building your own? For a detailed tutorial on how to build your Jina app check out [How to Build Your First Jina App](https://docs.jina.ai/chapters/my_first_jina_app/#how-to-build-your-first-jina-app) guide in our documentation. 

If you have any issues following this guide, you can always get support from our [Slack community](https://slack.jina.ai) .

## 👩‍👩‍👧‍👦 Community

- [Slack channel](https://slack.jina.ai/) - a communication platform for developers to discuss Jina.
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities.
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`.  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## 🦄 License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/examples/blob/master/LICENSE) for the full license text.
