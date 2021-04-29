**Table of Contents**
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
- [Run the EXAMPLE NAME](#run-the-example-name)
  - [🗝️ Pre requirements](#Pre-requirements)
  - [🔮 Overview of the files](#Overview-of-the-files)
  - [🏃 Run the Flows](#run-the-flows)
  - [🌀 Flow Diagram](#flow-diagram)
  - [🌟 Results](#results)
  - [🧞 OPTIONAL: EXTRA KNOWLEDGE FROM THIS EXAMPLE](#optional)
  - [💫 Deploy with Docker](#Deploy-with-docker)
  - [Next steps](#next-steps)
  - [Community](#community)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Run the EXAMPLE NAME

Write a short description of
1. What is this?
2. What is the expected outcome?
3. What the user will learn?

If you want to run the example with Docker, check the instruction at the end of this README.  

## 🗝️ Pre requirements

Outline in bullet points anything the user is expected to have before diving in. For example:

1. You have a working Python 3.8 environment. 
2. We recommend creating a [new python virtual envoriment](https://docs.python.org/3/tutorial/venv.html) to have a clean install of Jina and prevent dependency clashing.   
3. You have at least 8GB of free space on your hard drive. 

### Install requirements

In order to install all the Python libraries required you can run the following in your terminal:

```
pip install -r requirements.txt
```

## 🔮 Overview of the files

Add a list with all files in the example:

* `index.yml`: YAML file for indexing
* `query.yml`: YAML file for querying
* `encoder.yml`: YAML file for encoder pod
* `/workspace: Directory that stores indexed files (embeddings and documents). Automatically created after the first indexing.

## 🏃 Run the Flows

Most Jina applications will use two Flows. One for Indexing and one for Querying.

### Step 1: Index your data

Describe the Index Flow. Be as specific as possible. You are encouraged to user code snippets, images, or whatever helps to clarify.

### Step 2: Search your data

Describe the Query Flow. Be as specific as possible. You are encouraged to user code snippets, images, or whatever helps to clarify.

## 🌀 Flow diagram

Show the Flow for this example.

## 🌟 Results

Short description of the results and how to interpret them if needed.

## 🧞 Optional: Extra information useful for the user

You can use this section to add extra information you think the user could benefit from.
QueryLanguage, Faiss, Annoy for example. 

## 💫 Deploy with Docker

Pre requirements:

1. You have Docker installed and working.
2. You have at least 8GB of free space on your hard drive.

In order to build the docker image please run:

```bash
docker build -f Dockerfile -t {DOCKER_IMAGE_TAG} .
```

## Next steps

Check the tutorial for [My first Jina app](https://docs.jina.ai/chapters/my_first_jina_app).

## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina.
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina.
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities.
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`.  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!

## License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See LICENSE for the full license text.
