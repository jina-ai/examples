# ScaNN


## Usage

To build Scann from source  [follow instructions from here](https://github.com/google-research/google-research/tree/master/scann). 

## Possible bugs

### Typo on config.py

If you are running under MacOs probably you will need to do the following changes.

In `config.py` modify `generate_shared_lib_name` as follows :

```
def generate_shared_lib_name(namespec):
"""Converts the linkflag namespec to the full shared library name."""
# Assume Linux for now
# return namespec[1][3:]
#They have a typo with this, this is a dirty fix,hardcoded the name of the lib
return "libtensorflow_framework.2.dylib"
```
They have a typo when running under MacOs,  [you can find more info here](https://github.com/google-research/google-research/issues/342). 

### Compatibiliy with hash_set

You need to change the following files:

`memory_logging.h`
`partitioner_base.h`
`dataset.cc`
`kmeans_tree_node.cc`

in ech file change the  `#include <hash_set>`
for 

```
#if defined __GNUC__ || defined __APPLE__
#include <ext/hash_set>
#else
#include <hash_set>
#endif
```


