from jina import Document
import itertools as it

def index_generator(filepath: str, num_docs: int):
    def sample(iterable):
        for i in iterable:
            yield i

    with open(filepath, "r") as f:
        for line in it.islice(sample(f), num_docs):
            uri, name, text = line.split(",")
            document = Document()
            document.text = text
            document.tags["name"] = name
            document.tags["uri"] = uri
            yield document

input_fn = index_generator('data/people_wiki.csv', 500)
print(f' {next(input_fn)}')
