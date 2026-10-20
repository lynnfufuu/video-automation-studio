import os
import time
import urllib.parse
import requests
import cv2

ITEMS = [
    {
        "out_name": "opt1_sc1_entry_angle2.jpg",
        "prompt": "1990s flash photography, heavy rusty iron bunker door set into white ceramic tiled poolrooms wall, latch dissolving into solid ceramic tile, analog horror found footage, harsh direct flash, authentic 4:3, no text, no timestamp",
        "seed": 111
    },
    {
        "out_name": "opt1_sc2_environment_angle2.jpg",
        "prompt": "1990s flash photography, endless Roman colonnade hall with white square ceramic tiles flooded with clear turquoise water, subtle water ripples, harsh camera flash, analog horror, 4:3, no text, no timestamp",
        "seed": 222
    },
    {
        "out_name": "opt1_sc5_protocol_angle2.jpg",
        "prompt": "1990s flash photography, industrial square air circulation intake vent in white ceramic tiled ceiling glowing faintly, humid poolrooms mist, analog horror found footage, 4:3, no text, no timestamp",
        "seed": 333
    },
    {
        "out_name": "opt2_sc1_entry_angle2.jpg",
        "prompt": "1990s flash photography, wide abandoned multi-level 1989 shopping mall atrium with dead escalators and shuttered metal store gates, dark and eerie, harsh direct flash, analog horror, 4:3, no text, no timestamp",
        "seed": 444
    },
    {
        "out_name": "opt2_sc2_environment_angle2.jpg",
        "prompt": "1990s flash photography, deserted 1980s shopping mall corridor with buzzing purple and amber neon store sign casting sickly shadows, analog horror found footage, 4:3, no text, no timestamp",
        "seed": 555
    },
    {
        "out_name": "opt2_sc3_rations_angle2.jpg",
        "prompt": "1990s flash photography, dusty metal wire shelves in an abandoned shopping mall food court stockroom stacked with vintage 1980s canned food and sealed emergency rations, analog horror, 4:3, no text, no timestamp",
        "seed": 666
    },
    {
        "out_name": "opt2_sc5_protocol_angle2.jpg",
        "prompt": "1990s flash photography, dark ominous service corridor exit door in abandoned shopping mall with faint glowing red exit sign above, harsh camera flash, analog horror found footage, 4:3, no text, no timestamp",
        "seed": 777
    },
    {
        "out_name": "opt3_sc1_entry_angle2.jpg",
        "prompt": "1990s flash photography, looking down an endless vertical industrial steel ladder shaft descending three hundred meters into red heat haze and rusted catwalks, analog horror found footage, 4:3, no text, no timestamp",
        "seed": 888
    },
    {
        "out_name": "opt3_sc4_entities_angle2.jpg",
        "prompt": "1990s flash photography, tall gaunt humanoid shadow figure with glowing pale white eyes standing at the end of a dense red steamy industrial maintenance tunnel, harsh camera flash, analog horror, 4:3, no text, no timestamp",
        "seed": 999
    },
    {
        "out_name": "opt3_sc5_protocol_angle2.jpg",
        "prompt": "1990s flash photography, heavy circular reinforced steel blast bunker hatch door with mechanical locking wheel on industrial bulkhead, red warning strobe, analog horror found footage, 4:3, no text, no timestamp",
        "seed": 1010
    },
    {
        "out_name": "opt3_sc6_verdict_angle2.jpg",
        "prompt": "1990s flash photography, massive sealed hydraulic blast door with yellow and black hazard warning stripes in subterranean bunker, heavy steel rivets, harsh camera flash, analog horror, 4:3, no text, no timestamp",
        "seed": 1212
    }
]

def main():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "ai_scenes"))
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"[STILLS GENERATOR] Starting download of {len(ITEMS)} key scene stills...")
    
    for idx, item in enumerate(ITEMS):
        dest_path = os.path.join(out_dir, item["out_name"])
        print(f"[{idx+1}/{len(ITEMS)}] Requesting: {item['out_name']} (seed={item['seed']})...", flush=True)
        
        # 36s rate limit sleep
        time.sleep(36)
        
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(item['prompt'])}?width=1440&height=1080&nologo=true&seed={item['seed']}"
        
        success = False
        for attempt in range(3):
            try:
                r = requests.get(url, timeout=45)
                if r.status_code == 200 and len(r.content) > 10000:
                    raw_temp = dest_path + ".temp.jpg"
                    with open(raw_temp, "wb") as f:
                        f.write(r.content)
                        
                    im = cv2.imread(raw_temp)
                    if im is not None:
                        # Clean bottom watermark (35px) and enforce 1440x1080
                        clean = im[:-35, :]
                        clean_4_3 = cv2.resize(clean, (1440, 1080), interpolation=cv2.INTER_LANCZOS4)
                        cv2.imwrite(dest_path, clean_4_3, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        print(f"[{idx+1}/{len(ITEMS)}] SUCCESS -> Saved {item['out_name']} (1440x1080)", flush=True)
                        success = True
                    if os.path.exists(raw_temp):
                        os.remove(raw_temp)
                    break
                else:
                    print(f"  Attempt {attempt+1} got status {r.status_code}, retrying in 30s...", flush=True)
                    time.sleep(30)
            except Exception as e:
                print(f"  Attempt {attempt+1} error: {e}, retrying in 30s...", flush=True)
                time.sleep(30)
                
        if not success:
            print(f"[{idx+1}/{len(ITEMS)}] FAILED to generate {item['out_name']}", flush=True)
            
    print("[STILLS GENERATOR] All downloads complete!")

if __name__ == "__main__":
    main()
