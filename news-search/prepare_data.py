__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"


import os
import zipfile

root_path = '/tmp/jina/'
demo_name = 'news'
workspace = os.path.join(root_path, demo_name)
if not os.path.exists(root_path):
    os.mkdir(root_path)
if not os.path.exists(workspace):
    os.mkdir(workspace)

fz = zipfile.ZipFile(os.path.join('/tmp', 'new2016zh.zip'), 'r')

for file in fz.namelist():
    fz.extract(file, workspace)