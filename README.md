# Examples for Jina

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Adding Tests for Examples](#adding-tests-for-examples)
- [Community](#community)
- [License](#license)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

These examples showcase Jina in action and provide sample code for you to work from. We suggest you read [Jina 101](http://101.jina.ai) and <a href="https://jina.ai/2020/07/06/What-is-Neural-Search-and-Why-Should-I-Care.html">What is Neural Search?</a> to get a conceptual overview.

To learn more about how to use Jina, please refer to [our docs](http://www.jina.ai).

## 🐣 Simple Examples

<table>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/my-first-jina-app">My First Jina App</a></h4>
      Brand new to neural search? Not for long! Use cookiecutter to search through Star Trek scripts using Jina
    </td>
  </tr>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/southpark-search">Build a NLP Semantic Search System with Transformers</a></h4>
      Upgrade from plain search to sentence search and practice your Flows and Pods by searching South Park scripts
    </td>
  </tr>
  <tr>
    <td>
      <h1>📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/multires-lyrics-search">Search Lyrics with Transformers and PyTorch</a></h4>
      Get a better understanding of chunks by searching a lyrics database. Now with shiny front-end!
    </td>
  </tr>
  <tr>
    <td>
      <h1>🖼️</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/pokedex-with-bit">Google's Big Transfer Model in (Poké-)Production</a></h4>
      Use SOTA visual representation for searching Pokémon!
    </td>
  </tr>
  <tr>
    <td>
      <h1>🖼️</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/object-search">Object detection with fasterrcnn and MobileNetV2</a></h4>
      Detect, index and query similar objects
    </td>
  </tr>
  <tr>
    <td>
      <h1>🎧</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/audio-search">Search YouTube audio data with Vggish</a></h4>
      A demo of neural search for audio data based Vggish model.
    </td>
  </tr>
  <tr>
    <td>
      <h1>🎞️ </h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/tumblr-gif-search">Search Tumblr GIFs with KerasEncoder</a></h4>
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
      <h4><a href="https://github.com/jina-ai/examples/tree/master/faiss-search">Index and query with FAISS</a></h4>
      Build a vector search engine that finds the closest vector in the database to a query.
    </td>
  </tr>
  <tr>
    <td>
      <h1>🖼️📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/cross-modal-search">Cross Modal: Search images from captions and vice-versa</a></h4>
      Use one modality (text) to search another (images)
    </td>
  </tr>
  <tr>
    <td>
      <h1>🖼️📄</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/multimodal-search-tirg">Multi-Modal: Search images with 2 modalities in the query</a></h4>
      Use more than one modality (image+text) to search images
    </td>
  </tr>
  <tr>
    <td>
      <h1>🗂️</h1>
    </td>
    <td>
      <h4><a href="https://github.com/jina-ai/examples/tree/master/fashion-example-query">Build complex logic, structures and filters with Query Language</a></h4>
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
      <h4><a href="https://github.com/alexcg1/jina-wikipedia-sentences">Simple Wikipedia Sentence Search</a></h4>
      Simple Jina app to search sentences from Wikipedia using Transformers
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

- For reference, check out the `tests` folder from [South Park example](https://github.com/jina-ai/examples/tree/master/southpark-search/tests) if your data is about text and [object search example](https://github.com/jina-ai/examples/tree/master/object-search/tests) for images.
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
