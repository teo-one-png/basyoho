"""credits.jsとsw.jsを再生成"""
import json, re, os

# --- credits.js ---
with open("credits.json", "r", encoding="utf-8") as f:
    credits = json.load(f)

lines = ["const BIRD_CREDITS = {"]
for bird_id, info in sorted(credits.items()):
    artist = info.get("artist", "Unknown")
    artist = re.sub(r"[\"']", "", artist).strip()
    if len(artist) > 60:
        artist = artist[:57] + "..."
    lic = info.get("license", "Unknown")
    lines.append(f'  "{bird_id}": {{ artist: "{artist}", license: "{lic}" }},')
lines.append("};")

with open("credits.js", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"credits.js: {len(credits)} entries")

# --- sw.js ---
# Bird images
bird_images = sorted([f for f in os.listdir("images") if f.endswith(".jpg")])
# Tree images
tree_images = []
trees_dir = os.path.join("images", "trees")
if os.path.exists(trees_dir):
    tree_images = sorted([f for f in os.listdir(trees_dir) if f.endswith(".jpg")])

assets = [
    "./index.html", "./style.css", "./app.js", "./data.js", "./tree_data.js",
    "./credits.js", "./db.js", "./quiz.js", "./settings.js", "./manifest.json",
    "./icon-192.png", "./icon-512.png",
]

sw = []
sw.append('const CACHE_NAME = "torioboe-v6";')
sw.append("const ASSETS = [")
for a in assets:
    sw.append(f'  "{a}",')
sw.append("];")
sw.append("")
sw.append("const BIRD_IMAGES = [")
for img in bird_images:
    sw.append(f'  "./images/{img}",')
for img in tree_images:
    sw.append(f'  "./images/trees/{img}",')
sw.append("];")
total_images = len(bird_images) + len(tree_images)
sw.append("")
sw.append("const ALL_ASSETS = [...ASSETS, ...BIRD_IMAGES];")
sw.append("")
sw.append('self.addEventListener("install", (e) => {')
sw.append("  e.waitUntil(")
sw.append("    caches.open(CACHE_NAME).then((cache) => cache.addAll(ALL_ASSETS))")
sw.append("  );")
sw.append("});")
sw.append("")
sw.append('self.addEventListener("activate", (e) => {')
sw.append("  e.waitUntil(")
sw.append("    caches.keys().then((keys) =>")
sw.append("      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))")
sw.append("    )")
sw.append("  );")
sw.append("});")
sw.append("")
sw.append('self.addEventListener("fetch", (e) => {')
sw.append("  e.respondWith(")
sw.append('    caches.match(e.request).then((cached) => cached || fetch(e.request))')
sw.append("  );")
sw.append("});")

with open("sw.js", "w", encoding="utf-8") as f:
    f.write("\n".join(sw) + "\n")
print(f"sw.js: v6 with {total_images} images ({len(bird_images)} birds + {len(tree_images)} trees)")
