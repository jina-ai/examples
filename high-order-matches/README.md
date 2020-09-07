# Retrieving High-order Matches

New feature since `0.5.0`.

![](Figure_1.png)

## Prerequisite 
```bash
pip install -r requirements.txt
```

## Run & Plot

```bash
python app.py
```


## Understand the YAML

After it searches for the first shot, it recursively searches on matches. Each time retrieves top-50.

```yaml
SearchRequest:
  - !VectorSearchDriver
    with:
      top_k: 50
      fill_embedding: true
  - !VectorSearchDriver
    with:
      top_k: 50
      fill_embedding: true
      recur_on: matches
      recur_range: [ 0, 2 ]
```