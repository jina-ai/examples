It resolves the issue: [#134](https://github.com/jina-ai/examples/issues/134)

# Overview
There are 3 ways to use index and search method in Jina, we have examples like faiss, southpark and flower-search. This note will help you understand the pattern beyond those 3 examples.

#3 ways to initiate index flow
<p>
 
1.index_ndarray supports ndarray, and you can use this method to index your array data, like pics and sounds. Here is the example:[Faiss Search](https://github.com/jina-ai/examples/tree/master/faiss-search)

```python
import numpy as np
from jina.flow import Flow
flow = Flow().load_config('flow-index.yml')
input_data = np.random.random(10,100)
with flow.build() as fl:
    fl.index_ndarray(input_data)
```
2.index_files supports you to load files. In our example we use jpg files.Here is the example:[flower Search](https://github.com/jina-ai/examples/tree/master/flower-search)
```python
from jina.flow import Flow
f = Flow().load_config('flow-index.yml')
data_path="/your/data/path"
with f:
    f.index_files(f'{data_path}/*.jpg')
```
3.index_lines supports you to load lines, which you can only use it in text.Here is the example: [Southpark Search](https://github.com/jina-ai/examples/tree/master/southpark-search)
```python
from jina.flow import Flow
input_str = ['aaa','bbb']
f = Flow().load_config('flow-index.yml')
with f:
    f.index_lines(lines=input_str)
```

#3 ways to initiate query flow
<p>

1.search_ndarray supports you to search ndarray by ANN models. Here is the example[Faiss Search](https://github.com/jina-ai/examples/tree/master/faiss-search)

```python
import numpy as np
from jina.flow import Flow
input_data = np.random.random(10,100)
flow = Flow().load_config('flow-query.yml')
with flow.build() as fl:
   fl.search_ndarray(input_data)
```

2.search_files helps you to search from files.Here is the example:[flower Search](https://github.com/jina-ai/examples/tree/master/flower-search)
```python
from jina.flow import Flow
data_path="/your/data/path"
f = Flow().load_config('flow-query.yml')
with f:
    f.search_files(f'{data_path}/*.jpg')
```
3.search_lines helps you to search in lines.Here is the example: [Southpark Search](https://github.com/jina-ai/examples/tree/master/southpark-search)
```python
from jina.flow import Flow
f = Flow().load_config('flow-query.yml')
with f:
    text = input('please type a sentence: ')
    if not text:
        break
    f.search_lines(lines=[text, ])
```
