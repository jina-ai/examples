import numpy as np
import clip
import torch
import torch.utils.data as data
import PIL
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load('ViT-B/32', device)
im = PIL.Image.open('../imgs/man_piercing.jpg')

### Single image

im_tensor_clip_input = preprocess(im).unsqueeze(0)
embedding_tensor = model.encode_image(im_tensor_clip_input)
embedding_np = embedding_tensor.detach().numpy()

file = open('./expected.npy','bw')
np.save(file, embedding_np)
file.close()

### batch 3 images

batch = torch.cat([im_tensor_clip_input,
                   im_tensor_clip_input,
                   im_tensor_clip_input])

embedding_tensor = model.encode_image(batch)
embedding_np = embedding_tensor.detach().numpy()
file = open('./expected_batch.npy','bw')
np.save(file, embedding_np)
file.close()