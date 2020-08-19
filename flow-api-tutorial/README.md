# Overview
Jina supports you to index and search your data in a simple way. And it exposes 3 APIs to each of them, which help you to index and search `ndarray`, `files`, and `lines` data.

# 3 APIs for indexing your data
<p>

1. `index_ndarray()` is the API for indexing `ndarray`.

   ```python
    import numpy as np
    from jina.flow import Flow
    input_data = np.random.random((10,100))
    f = Flow().add(uses='_logforward')
    with f:
        f.index_ndarray(input_data)
    ```

2. `index_files()` is the API for indexing `files`

    ```python
    from jina.flow import Flow
    f = Flow().add(uses='_logforward')
    with f:
        # Note that those yml files are in the examples project
        # which you can download from the github
        f.index_files(f'../pokedex-with-bit/pods/*.yml')
    ```
3. `index_lines()` is the API for indexing `lines`
    ```python
    from jina.flow import Flow
    input_str = ['aaa','bbb']
    f = Flow().add(uses='_logforward')
    with f:
        f.index_lines(lines=input_str)
    ```

# 3 APIs for querying your data
<p>

1. `search_ndarray()` is the API for searching `ndarray`

    ```python
    import numpy as np
    from jina.flow import Flow
    input_data = np.random.random((10,100))
    f = Flow().add(uses='_logforward')
    with f:
       f.search_ndarray(input_data)
    ```

2. `search_files()` is the API for searching `files`
    ```python
    from jina.flow import Flow
    f = Flow().add(uses='_logforward')
    with f:
        f.search_files(f'../pokedex-with-bit/pods/chunk.yml')
    ```
3. `search_lines()` is the API for searching `lines`
    ```python
    from jina.flow import Flow
    text = input('please type a sentence: ')
    f = Flow().add(uses='_logforward')
    with f:   
        f.search_lines(lines=[text, ])
    ```

Those are just simple ways to build your indexing and searching code. Beyond those, we have examples like [Faiss Search](https://github.com/jina-ai/examples/tree/master/faiss-search), [Southpark Search](https://github.com/jina-ai/examples/tree/master/southpark-search) and [Flower Search](https://github.com/jina-ai/examples/tree/master/flower-search), which show more details in configurations.