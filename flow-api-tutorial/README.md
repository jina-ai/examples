# Build an Image Search System in 3 minutes
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

In this demo, we'll use some code snippets to build search system. Make sure you've gone through [Jina 101](https://github.com/jina-ai/jina/tree/master/docs/chapters/101) and understood the Pod, Flow, Yaml before moving on. 

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Overview](#overview)
- [Wrap up](#wrap-up)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
## Overview
Jina supports you to index and search your data in a simple way. And it exposes 3 APIs to each of them, which help you to index and search `ndarray`, `files`, and `lines` data.

### 3 APIs for indexing your data
<p>

1. `index_ndarray()` is the API for indexing `ndarray`. In this example, we created a 3*8 random matrix by numpy. Jina Flow helps to index the matrix. First, we need to import Flow. Then, we add an empty pod named `_logforward` to the Flow. After that, we start the Flow simply by using `index_ndarray()`. After several seconds, you will receive the results in the logs. 
    
    <p>
    
    In this case, we used several parameters. `_logforward` is an internal yaml file, which locates in `/jina/resources/executors._forward.yml`. In the code `add(uses='_logforward')`, Flow will create an empty pod which just forward structured data to the clients. The structure is defined by `jina.proto`, which is a protobuf file. Pods forward the structured data file to each other or to the clients by gRPC.
    
    <p>
    
    In the logs, we will receive structured results, which is defined by `jina.proto` as well. `Envelope` and `Request` are the top of the structure. `Enveloope` describes some meta data and control data. `Request` is the message we send to the Flow. In this case, we send a 3*8 matrix, which matches 3 `docs` branches and the `shape` of the `blob` is 8. In the `docs` branch, the `buffer` in the `blob` is the value of the matrix. And `dtype` indicates the type of the value.

   ```python
   import numpy as np
   from jina.flow import Flow
   input_data = np.random.random((3,8))
   f = Flow().add(uses='_logforward')
   with f:
       f.index_ndarray(input_data)
   ```

2. `index_files()` is the API for indexing `files`. In this case, the general steps are similar. But it uses files as input data. As a result, the log structure is a little bit different. It is in the `request.index.docs`. we just record the uri of the file. In this case, we got 5 `docs` branches, because there are 5 yaml files in the directory.

    ```python
    from jina.flow import Flow
    f = Flow().add(uses='_logforward')
    with f:
        f.index_files(f'../pokedex-with-bit/pods/*.yml')
    ```
3. `index_lines()` is the API for indexing `lines`. In this case, the general steps are quiet similar as well. And in the `request.index.docs`, you can notice the `mime_type` that shows the type of the data, and the `text` that stores the data.
    ```python
    from jina.flow import Flow
    input_str = ['aaa','bbb']
    f = Flow().add(uses='_logforward')
    with f:
        f.index_lines(lines=input_str)
    ```

### 3 APIs for querying your data
<p>

1. `search_ndarray()` is the API for searching `ndarray`. The steps and the results are quiet the same as `index_ndarray()`, the main difference is the `index` branch is replaced by `search`

    ```python
    import numpy as np
    from jina.flow import Flow
    input_data = np.random.random((3,8))
    f = Flow().add(uses='_logforward')
    with f:
       f.search_ndarray(input_data)
    ```

2. `search_files()` is the API for searching `files`. The steps and the results are quiet the same as `index_files()`, the main difference is the `index` branch is replaced by `search` 
    ```python
    from jina.flow import Flow
    f = Flow().add(uses='_logforward')
    with f:
        f.search_files(f'../pokedex-with-bit/pods/chunk.yml')
    ```
3. `search_lines()` is the API for searching `lines`. The steps and the results are quiet the same as `index_files()`, the main difference is the `index` branch is replaced by `search`
    ```python
    from jina.flow import Flow
    text = input('please type a sentence: ')
    f = Flow().add(uses='_logforward')
    with f:   
        f.search_lines(lines=[text, ])
    ```

## Wrap up
In this example, we showed you 6 exampls on how to use `index` and `search`, and described the data structure during forwarding to the next pod or to the client, and we pointed out the key nodes in the structure.

## Next Steps

- Write your own Flows.
- try more examples in `index` and `search`
<br>
`ndarray` - [Faiss Search](https://github.com/jina-ai/examples/tree/master/faiss-search)
</br>
<br>
`files` - [Flower Search](https://github.com/jina-ai/examples/tree/master/flower-search)
</br>
<br>
`lines` - [Southpark Search](https://github.com/jina-ai/examples/tree/master/southpark-search)
<!---
- Check out the Docker images at Jina hub.
--->

## Documentation 

<a href="https://docs.jina.ai/">
<img align="right" width="350px" src="https://github.com/jina-ai/jina/blob/master/.github/jina-docs.png" />
</a>

The best way to learn Jina in-depth is to read our documentation. Documentation is built on every push, merge, and release event of the master branch. For more details, check out:

- [Jina command line interface arguments explained](https://docs.jina.ai/chapters/cli/index.html)
- [Jina Python API interface](https://docs.jina.ai/api/jina.html)
- [Jina YAML syntax for executor, driver and flow](https://docs.jina.ai/chapters/yaml/yaml.html)
- [Jina Protobuf schema](https://docs.jina.ai/chapters/proto/index.html)
- [Environment variables used in Jina](https://docs.jina.ai/chapters/envs.html)
- ... [and more](https://docs.jina.ai/index.html)

## Community

- [Slack channel](https://join.slack.com/t/jina-ai/shared_invite/zt-dkl7x8p0-rVCv~3Fdc3~Dpwx7T7XG8w) - a communication platform for developers to discuss Jina
- [Community newsletter](mailto:newsletter+subscribe@jina.ai) - subscribe to the latest update, release and event news of Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!



## License

Copyright (c) 2020 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
