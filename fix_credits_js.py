"""credits.jsを安全に再生成"""
import json
import re

with open("credits.json", "r", encoding="utf-8") as f:
    credits = json.load(f)

lines = ["const BIRD_CREDITS = {"]
for bird_id, info in sorted(credits.items()):
    artist = info.get("artist", "Unknown")
    # Remove HTML tags
    artist = re.sub(r"<[^>]+>", "", artist)
    # Remove characters that break JS strings
    for ch in ['"', "'", "\\", "\n", "\r"]:
        artist = artist.replace(ch, "")
    artist = artist.strip()
    if len(artist) > 50:
        artist = artist[:47] + "..."

    lic = info.get("license", "Unknown")
    for ch in ['"', "'", "\\", "\n", "\r"]:
        lic = lic.replace(ch, "")

    lines.append(f'  "{bird_id}": {{ artist: "{artist}", license: "{lic}" }},')

lines.append("};")

with open("credits.js", "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Generated credits.js with {len(credits)} entries")
