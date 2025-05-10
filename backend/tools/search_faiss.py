# tools/search_faiss.py

import json
import torch
import clip
import numpy as np
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def load_data():
    metadata = json.load(open("data/art_metadata.json"))
    embeddings = np.load("data/art_embeddings.npy")
    return metadata, embeddings

def get_user_embedding(image_path):
    image = preprocess(Image.open(image_path).convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(image).cpu().numpy()
    return emb

def search_top_k(user_img_path, k=5):
    import faiss  # ⬅️ moved inside here
    metadata, embeddings = load_data()
    user_emb = get_user_embedding(user_img_path)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    D, I = index.search(user_emb, k)
    return [metadata[i] for i in I[0]]

