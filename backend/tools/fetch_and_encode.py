import os
import json
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm
import torch
import clip
import numpy as np

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

SAVE_DIR = "data"
os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_artworks(page=1, limit=100):
    url = "https://api.artic.edu/api/v1/artworks"
    params = {
        "page": page,
        "limit": limit,
        "fields": "id,title,image_id,artist_display,date_display,style_title",
        "query[term][is_public_domain]": "true"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    return []

def get_clip_embedding(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        tensor = preprocess(image).unsqueeze(0).to(device)
        with torch.no_grad():
            embedding = model.encode_image(tensor).cpu().numpy()
        return embedding[0]
    except Exception as e:
        print(f"❌ Image failed: {e}")
        return None

def main():
    all_data = []
    embeddings = []

    for page in range(1, 6):
        artworks = fetch_artworks(page)
        for art in tqdm(artworks, desc=f"Page {page}"):
            image_id = art.get("image_id")
            if not image_id:
                continue

            image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg"
            emb = get_clip_embedding(image_url)
            if emb is None:
                continue

            embeddings.append(emb)
            all_data.append({
                "title": art.get("title"),
                "artist": art.get("artist_display"),
                "date": art.get("date_display"),
                "style": art.get("style_title"),
                "image_url": image_url
            })

    with open(f"{SAVE_DIR}/art_metadata.json", "w") as f:
        json.dump(all_data, f)
    np.save(f"{SAVE_DIR}/art_embeddings.npy", np.array(embeddings))
    print(f"✅ Saved {len(embeddings)} artworks.")

if __name__ == "__main__":
    main()

