import os
import requests

token = os.environ.get("HUGGING_FACE_TOKEN", "")
headers = {"Authorization": f"Bearer {token}"} if token else {}

models_to_test = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "stabilityai/stable-diffusion-2-1"
]

payload = {"inputs": "A dark misty Japanese mountain street at night, 35mm photo"}

for m in models_to_test:
    url = f"https://router.huggingface.co/hf-inference/models/{m}"
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        ct = res.headers.get("content-type", "")
        print(f"Model: {m} -> Status: {res.status_code}, Content-Type: {ct}, Length: {len(res.content)}")
        if res.status_code != 200:
            print("  Response text:", res.text[:200])
        elif "image" in ct:
            with open(f"test_{m.replace('/', '_')}.jpg", "wb") as f:
                f.write(res.content)
            print(f"  Saved test_{m.replace('/', '_')}.jpg successfully!")
    except Exception as e:
        print(f"Model: {m} -> Error: {e}")
