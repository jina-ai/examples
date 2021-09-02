# Examples for Jina

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Adding Tests for Examples](#adding-tests-for-examples)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

These examples showcase Jina in action and provide sample code for you to work from. 

We suggest you read the following to get an overview of what Jina is and how it works:

- [What is neural search?](https://github.com/jina-ai/jina/blob/master/.github/2.0/neural-search.md)
- [Get started](https://github.com/jina-ai/jina/#get-started) - especially the cookbooks for Document, Executor and Flow

## 🐣 Simple Examples

<table>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="./wikipedia-sentences">Semantic Wikipedia Search with Transformers and DistilBERT</a></h4>
      Brand new to neural search? See a simple text-search example to understand how Jina works
    </td>
  </tr>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="./multires-lyrics-search">Search Lyrics with Transformers and PyTorch</a></h4>
      Get a better understanding of chunks by searching a lyrics database. Now with shiny front-end!
    </td>
  </tr>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="./audio-to-audio-search">Find Similar Audio Clips</a></h4>
      A simple example to show how to find similar audio clips using Jina
    </td>
  </tr>
</table>

## 🚀  Advanced Examples

<table>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="./wikipedia-sentences-query-while-indexing">Querying While Indexing in the Wikipedia Search Example</a></h4>
      Support both querying and indexing simultaneously in our Wikipedia Search Example
    </td>
  </tr>
  
  <tr>
    <td>
      <h1>🖼️📄</h1>
    </td>
    <td>
      <h4><a href="./cross-modal-search">Cross Modal: Search images from captions and vice-versa</a></h4>
      Use one modality (text) to search another (images)
    </td>
  </tr>
</table>

## Community Examples

Want to add your own example? Please check our [guidelines](example-guidelines.md)!

<table>
    <tr>
    <td>
      <h1>🖼️📄</h1>
    </td>
    <td>
      <h4>Meme Search - <a href="https://github.com/alexcg1/jina-meme-search-example/">Text search</a> / <a href="https://github.com/alexcg1/jina-meme-search-image-backend">Image search</a> / <a href="https://github.com/alexcg1/jina-meme-search-frontend">Front end</a></h4>
      Search memes by caption or similar image.
    </td>
  </tr><tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/alexcg1/jina-app-store-example">App Store Search</a></h4>
      Use Transformers to search through a rich app store dataset with a responsive front-end
    </td>
  </tr>
</table>

#### Legacy examples

<table>
    <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/yuanbit/jina-financial-qa-search">Financial Question Answering Search</a></h4>
      Opinionated QA passage retrieval with BERT-based reranker
    </td>
  </tr>
</table>

## Adding Tests for Examples

You are highly encouraged to add a test for your example so that we will be alerted if it breaks in the future:

1. Put your test data in the `tests` folder. The test data can be a few text sentences, images or audio samples
2. Create `test_[your_example].py` in the `tests` folder. Add your test cases to the `tests` file with meaningful asserts depending on example input and output
3. Run the test locally to confirm before pushing with [pytest](https://docs.pytest.org/en/stable/contents.html)
4. Add your example folder name to the `path` variable in `matrix` of `.github/worflows/ci.yml`. This will trigger your example test on creating a pull request.


### Testing Tips

- For reference, check out the `tests` folder from any of the examples in this repo.
- Try using the original example function by importing them to the test. Avoid any modifications to original Flow or logic.
- Use the [pytest fixture](https://docs.pytest.org/en/stable/fixture.html) `tmpdir` for temporary directory

## Community

- [Slack channel](http://slack.jina.ai) - a communication platform for developers to discuss Jina
- [LinkedIn](https://www.linkedin.com/company/jinaai/) - get to know Jina AI as a company and find job opportunities
- [![Twitter Follow](https://img.shields.io/twitter/follow/JinaAI_?label=Follow%20%40JinaAI_&style=social)](https://twitter.com/JinaAI_) - follow us and interact with us using hashtag `#JinaSearch`  
- [Company](https://jina.ai) - know more about our company, we are fully committed to open-source!


## License

Copyright (c) 2021 Jina AI Limited. All rights reserved.

Jina is licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/jina-ai/jina/blob/master/LICENSE) for the full license text.
