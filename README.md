# Examples for Jina

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Adding Tests for Examples](#adding-tests-for-examples)
- [Performance metrics](#performance)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

These examples showcase Jina in action and provide sample code for you to work from. We suggest you read [Jina 101](http://101.jina.ai) and <a href="https://jina.ai/2020/07/06/What-is-Neural-Search-and-Why-Should-I-Care.html">What is Neural Search?</a> to get a conceptual overview.

❗If you'd like to run our examples on Windows, please follow [this instruction](https://docs.jina.ai/chapters/install/os/on-wsl.html).

To learn more about how to use Jina, please refer to [our docs](http://www.jina.ai).

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
      <h4><a href="./wikipedia-sentences-incremental">Add Incremental Indexing to Wikipedia Search</a></h4>
      Index more effectively by adding incremental indexing to your Wikipedia search
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
      <h1>🖼️</h1>
    </td>
    <td>
      <h4><a href="./pokedex-with-bit">Google's Big Transfer Model in (Poké-)Production</a></h4>
      Use SOTA visual representation for searching Pokémon!
    </td>
  </tr>
  <tr>
    <td>
      <h1>🖼️</h1>
    </td>
    <td>
      <h4><a href="./object-search">Object detection with fasterrcnn and MobileNetV2</a></h4>
      Detect, index and query similar objects
    </td>
  </tr>
  <tr>
    <td>
      <h1>🎧</h1>
    </td>
    <td>
      <h4><a href="./audio-search">Search YouTube audio data with Vggish</a></h4>
      A demo of neural search for audio data based Vggish model.
    </td>
  </tr>
  <tr>
    <td>
      <h1>🎞️ </h1>
    </td>
    <td>
      <h4><a href="./tumblr-gif-search">Search Tumblr GIFs with KerasEncoder</a></h4>
      Use prefetching and sharding to improve the performance of your index and query flow when searching animated GIFs.
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
      <h4><a href="./advanced-vector-search">Index and query with FAISS</a></h4>
      Build a vector search engine that finds the closest vector in the database to a query.
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
  <tr>
    <td>
      <h1>🖼️📄</h1>
    </td>
    <td>
      <h4><a href="./multimodal-search-tirg">Multi-Modal: Search images with 2 modalities in the query</a></h4>
      Use more than one modality (image+text) to search images
    </td>
  </tr>
  <tr>
    <td>
      <h1>🗂️</h1>
    </td>
    <td>
      <h4><a href="./fashion-example-query">Build complex logic, structures and filters with Query Language</a></h4>
      Create separate indexes and queries for different clothing in Fashion-MNIST
    </td>
  </tr>
</table>

## Community Examples

Want to add your own example? Please check our [guidelines](example-guidelines.md)!

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

## Performance metrics

You can run the `perf-script.sh` in order to run all of the examples on your machine. Make sure this is done in a separate python virtualenv.

This measures QPS for indexing and querying.

This will store the results in [`performance.txt`](./performance.txt).

Note that a lot of the examples are not optimized (or configured for scaling). They are provided as is, for the basic functionality. 

## Adding Tests for Examples

You are highly encouraged to add a test for your example so that we will be alerted if it breaks in the future:

1. Put your test data in the `tests` folder. The test data can be a few text sentences, images or audio samples
2. Create `test_[your_example].py` in the `tests` folder. Add your test cases to the `tests` file with meaningful asserts depending on example input and output
3. Run the test locally to confirm before pushing with [pytest](https://docs.pytest.org/en/stable/contents.html)
4. Add your example folder name to the `path` variable in `matrix` of `.github/worflows/ci.yml`. This will trigger your example test on creating a pull request.


### Testing Tips

- For reference, check out the `tests` folder from [South Park example](./southpark-search/tests) if your data is about text and [object search example](./object-search/tests) for images.
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
