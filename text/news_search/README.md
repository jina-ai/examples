# Build Bert-based NLP Semantic Search System

<p align="center">

[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-badge.svg "We fully commit to open-source")](https://jina.ai)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-hello-world-badge.svg "Run Jina 'Hello, World!' without installing anything")](https://github.com/jina-ai/jina#jina-hello-world-)
[![Jina](https://github.com/jina-ai/jina/blob/master/.github/badges/license-badge.svg "Jina is licensed under Apache-2.0")](#license)
[![Jina Docs](https://github.com/jina-ai/jina/blob/master/.github/badges/docs-badge.svg "Checkout our docs and learn Jina")](https://docs.jina.ai)
[![We are hiring](https://github.com/jina-ai/jina/blob/master/.github/badges/jina-corp-badge-hiring.svg "We are hiring full-time position at Jina")](https://jobs.jina.ai)
<a href="https://twitter.com/intent/tweet?text=%F0%9F%91%8DCheck+out+Jina%3A+the+New+Open-Source+Solution+for+Neural+Information+Retrieval+%F0%9F%94%8D%40JinaAI_&url=https%3A%2F%2Fgithub.com%2Fjina-ai%2Fjina&hashtags=JinaSearch&original_referer=http%3A%2F%2Fgithub.com%2F&tw_p=tweetbutton" target="_blank">
  <img src="https://github.com/jina-ai/jina/blob/master/.github/badges/twitter-badge.svg"
       alt="tweet button" title="👍Share Jina with your friends on Twitter"></img>
</a>
[![Python 3.7 3.8](https://github.com/jina-ai/jina/blob/master/.github/badges/python-badge.svg "Jina supports Python 3.7 and above")](#)
[![Docker](https://github.com/jina-ai/jina/blob/master/.github/badges/docker-badge.svg "Jina is multi-arch ready, can run on differnt architectures")](https://hub.docker.com/r/jinaai/jina/tags)

</p>

In this demo, we use Jina to build a semantic search system on the [BBCNewsData](https://www.kaggle.com/shineucc/bbc-news-dataset). The goal is to search for news articles from BBC News. It is hosted in kaggle by [Shine K George](https://www.kaggle.com/shineucc/)Thank you for the valuable resource. This demo will show you how to quickly build a search system from scratch with Jina. Before moving forward, We highly suggest to going through our lovely [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and [Jina "Hello, World!"👋🌍](https://github.com/jina-ai/jina#jina-hello-world-).



<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [Prerequirements](#prerequirements)
- [Prepare the data](#prepare-the-data)
- [Run the Flows](#run-the-flows)
- [Wrap up](#wrap-up)
- [Documentation](#documentation)
- [Stay tuned](#stay-tuned)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->



## Overview

First, We'll look into the working of Jina and how it uses Neural Search to the documents of our requirements. We want build a search system to find articles from BBC News which are similar to a user's input text. To make this happen, we divide the articles into sentences and consider each sentence as one **Document**. For the demo purposes, let us consider each Document to have only one **Chunk**, which contains the same sentence as the Document. Each sentence, as a Chunk, is encoded into a vector with the help of the **Encoder** (by using the `DistilBert` from the  `Transformers` lib).

Just like most of the search engines, we first build an indexing on all the documents(i.e characters and lines) extracted from the given dataset. During indexing, Jina, represents sentences as vectors (encoded by using an **Encoder**) and saves the vectors in the index. While querying, the input of the user is converted into vectors using the same **Encoder** which helps us in retrieving the indexed lines with similar meanings(i.e by measuring the similarity between vectors).


## Prerequirements

This demo requires Python 3.7.

```bash
pip install --upgrade -r requirements.txt
```


## Prepare the data

The raw data contains description,tags information in the `.csv` format as follows:

```
,description,tags
0,chelsea sack mutu  chelsea have sacked adrian mutu after he failed a drugs test  the yearold tested positive for a banned substance  which he later denied was cocaine  in october chelsea have decided to write off a possible transfer fee for mutu a m signing from parma last season who may face a twoyear suspension a statement from chelsea explaining the decision readwe want to make clear that chelsea has a zero tolerance policy towards drugs mutu scored six goals in his first five games after arriving at stamford bridge but his form went into decline and he was frozen out by coach jose mourinho chelseas statement added this applies to both performanceenhancing drugs or socalled recreational drugs they have no place at our club or in sport in coming to a decision on this case chelsea believed the clubs social responsibility to its fans players employees and other stakeholders in football regarding drugs was more important than the major financial considerations to the company any player who takes drugs breaches his contract with the club as well as football association rules the club totally supports the fa in strong action on all drugs cases fifas disciplinary code stipulates that a first doping offence should be followed by a sixmonth ban and the sports world governing body has reiterated their stance over mutus failed drugs test maintaining it is a matter for the domestic sporting authorities fifa is not in a position to make any comment on the matter until the english fa have informed us of their disciplinary decision and the relevant information associated with it said a fifa spokesman chelseas move won backing from drugtesting expert michelle verroken verroken a former director of drugfree sport for uk sport insists the blues were right to sack mutu and have enhanced their reputation by doing so chelsea are saying quite clearly to the rest of their players and their fans that this is a situation they are not prepared to tolerate it was a very difficult decision for them and an expensive decision for them but the terms of his contract were breached and it was the only decision they could make it is a very clear stance by chelsea and it has given a strong boost to the reputation of the club it emerged that mutu had failed a drugs test on october  and although it was initially reported that the banned substance in question was cocaine the romanian international later suggested it was a substance designed to enhance sexual performance the football association has yet to act on mutus failed drugs test and refuses to discuss his case ,"sports, stamford bridge, football association, fifa, michelle verroken, adrian mutu, jose mourinho, player, coach, director of drug-free sport for uk sport, spokesman, association football, adrian mutu, chelsea f.c., josé mourinho, doping in sport, transfer, english footballers, doping in association football, football, the football association"


```

Execute the below commands to get the data and perform certain data wrangling tasks. Overall, there are 106,820 lines in `/tmp/jina/news/bbc_news.csv`

```bash
cd news_search
bash ./get_data.sh /tmp/jina/news
```

## Run the Flows

### Index


```bash
python app.py -t index -n 2500
```

<details>
<summary>Click here to see the console output</summary>

<p align="center">
  <img src=".images/index.png?raw=true" alt="index flow console output">
</p>

</details>


### Query

```bash
python app.py -t query
```

<details>
<summary>Click here to see the console output</summary>

<p align="center">
  <img src="images/query.png?raw=true" alt="query flow console output">
</p>

</details>


## Wrap up
Congratulations! Now you've got your very own neural search engine to search for BBC news!

[For tutorials on how to build a search engine please visit](https://github.com/jina-ai/examples/tree/master/southpark-search)

## Documentation

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. You can find more details about the following topics in our documentation.

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Stay tuned

- [Slack chanel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company
- ![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social) - follow us and interact with us using hashtag `#JinaSearch`
- [Join Us](mailto:hr@jina.ai) - want to work full-time with us at Jina? We are hiring!
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!


## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
