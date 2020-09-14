from jina.flow import Flow
from corpus import input_fn

f = (Flow().add(name='dummyEncoder', uses='mwu.yml'))

# test it with dry run
with f:
    #f.dry_run()
    f.index(input_fn)
