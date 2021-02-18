import numpy as np
import clip
import torch
import torch.utils.data as data
import PIL
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load('ViT-B/32', device)

text = 'Han likes eating pizza'
embeddeding_tensor = model.encode_text(clip.tokenize(text))
embedding_np = embeddeding_tensor.detach().numpy()

file = open('./expected.npy','bw')
np.save(file, embedding_np)
file.close()
