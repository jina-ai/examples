from jina import Flow
from jina.types.document.generators import from_csv

flow = (
    Flow()
    .add(uses="jinahub+docker://TransformerTorchEncoder", name="encoder")
    .add(
        uses="jinahub+docker://SimpleIndexer",
        volumes="./workspace:/workspace/workspace",
        name="indexer",
    )
)

with flow, open("data/superheroes.csv") as fp:
    flow.index(from_csv(fp, field_resolver={"powers_text": "text"}), size=10)
