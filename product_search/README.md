# Product Search Example

This directory contains examples for both text and image search, using the same dataset for each.

## Set up

- Ensure Kaggle installed
- Run `get_data.sh`

## Play with each example

- Go to directory
- Install requirements, get data, download model (for image search)
- `python app.py -t index` to index
- `python app.py -t query` to query

## Notes

- Image search uses same command line args as text search (i.e. with `-t`, `query` instead of `search`)
- Dockerfiles, manifests, tests not updated yet. Still reflect Wiki/Pokedex search
- Text results are rubbish. Perhaps due to very short Documents
