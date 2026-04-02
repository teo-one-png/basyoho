#!/usr/bin/env python3
"""
Fix fish_credits.json by adding the 29 missing fish entries.
Uses Japanese Wikipedia API to find image filenames, then Wikimedia Commons API for credit info.
"""

import json
import time
import urllib.request
import urllib.parse
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

CREDITS_JSON = 'fish_credits.json'
CREDITS_JS = 'fish_credits.js'

# Missing IDs with their Japanese names (from fish_data.js) and scientific names for Wikipedia lookup
MISSING_FISH = {
    'biwamasu':        {'name_jp': 'ビワマス',       'wiki_jp': 'ビワマス',         'wiki_en': 'Biwa trout'},
    'nigorobuna':      {'name_jp': 'ニゴロブナ',     'wiki_jp': 'ニゴロブナ',       'wiki_en': 'Carassius buergeri grandoculis'},
    'honmoroko':       {'name_jp': 'ホンモロコ',     'wiki_jp': 'ホンモロコ',       'wiki_en': 'Gnathopogon caerulescens'},
    'biwahigai':       {'name_jp': 'ビワヒガイ',     'wiki_jp': 'ビワヒガイ',       'wiki_en': 'Sarcocheilichthys variegatus microoculus'},
    'aburahigai':      {'name_jp': 'アブラヒガイ',   'wiki_jp': 'アブラヒガイ',     'wiki_en': 'Sarcocheilichthys biwaensis'},
    'dememoroko':      {'name_jp': 'デメモロコ',     'wiki_jp': 'デメモロコ',       'wiki_en': 'Squalidus japonicus'},
    'utsusemikajika':  {'name_jp': 'ウツセミカジカ', 'wiki_jp': 'ウツセミカジカ',   'wiki_en': 'Cottus reinii'},
    'iwatoko_namazu':  {'name_jp': 'イワトコナマズ', 'wiki_jp': 'イワトコナマズ',   'wiki_en': 'Silurus lithophilus'},
    'koi':             {'name_jp': 'コイ',           'wiki_jp': 'コイ',             'wiki_en': 'Common carp'},
    'tamoroko':        {'name_jp': 'タモロコ',       'wiki_jp': 'タモロコ',         'wiki_en': 'Gnathopogon elongatus'},
    'motsugo':         {'name_jp': 'モツゴ',         'wiki_jp': 'モツゴ',           'wiki_en': 'Pseudorasbora parva'},
    'kamatsuka':       {'name_jp': 'カマツカ',       'wiki_jp': 'カマツカ (魚)',    'wiki_en': 'Pseudogobio esocinus'},
    'zezera':          {'name_jp': 'ゼゼラ',         'wiki_jp': 'ゼゼラ',           'wiki_en': 'Biwia zezera'},
    'higai':           {'name_jp': 'ヒガイ',         'wiki_jp': 'ヒガイ',           'wiki_en': 'Sarcocheilichthys variegatus'},
    'itomoroko':       {'name_jp': 'イトモロコ',     'wiki_jp': 'イトモロコ',       'wiki_en': 'Squalidus gracilis'},
    'tanago':          {'name_jp': 'タナゴ',         'wiki_jp': 'タナゴ',           'wiki_en': 'Acheilognathus melanogaster'},
    'yaritanago':      {'name_jp': 'ヤリタナゴ',     'wiki_jp': 'ヤリタナゴ',       'wiki_en': 'Tanakia lanceolata'},
    'namazu':          {'name_jp': 'ナマズ',         'wiki_jp': 'ナマズ',           'wiki_en': 'Japanese catfish'},
    'dojou':           {'name_jp': 'ドジョウ',       'wiki_jp': 'ドジョウ',         'wiki_en': 'Misgurnus anguillicaudatus'},
    'shimadojou':      {'name_jp': 'シマドジョウ',   'wiki_jp': 'シマドジョウ',     'wiki_en': 'Cobitis biwae'},
    'yoshinobori':     {'name_jp': 'ヨシノボリ',     'wiki_jp': 'ヨシノボリ',       'wiki_en': 'Rhinogobius'},
    'kawayoshinobori':  {'name_jp': 'カワヨシノボリ', 'wiki_jp': 'カワヨシノボリ',   'wiki_en': 'Rhinogobius flumineus'},
    'numachichibu':    {'name_jp': 'ヌマチチブ',     'wiki_jp': 'ヌマチチブ',       'wiki_en': 'Tridentiger brevispinis'},
    'unagi':           {'name_jp': 'ニホンウナギ',   'wiki_jp': 'ニホンウナギ',     'wiki_en': 'Japanese eel'},
    'medaka':          {'name_jp': 'メダカ',         'wiki_jp': 'メダカ',           'wiki_en': 'Japanese rice fish'},
    'sunayatsume':     {'name_jp': 'スナヤツメ',     'wiki_jp': 'スナヤツメ',       'wiki_en': 'Lethenteron reissneri'},
    'kawayatsume':     {'name_jp': 'カワヤツメ',     'wiki_jp': 'カワヤツメ',       'wiki_en': 'Lethenteron camtschaticum'},
    'itoyo':           {'name_jp': 'イトヨ',         'wiki_jp': 'イトヨ',           'wiki_en': 'Three-spined stickleback'},
    'wakasagi':        {'name_jp': 'ワカサギ',       'wiki_jp': 'ワカサギ',         'wiki_en': 'Hypomesus nipponensis'},
}


def api_get(url):
    """Make a GET request and return JSON."""
    req = urllib.request.Request(url, headers={'User-Agent': 'FishCreditsBot/1.0 (educational project)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def get_image_from_jp_wiki(title_jp):
    """Get the main image filename from Japanese Wikipedia article."""
    url = (
        'https://ja.wikipedia.org/w/api.php?action=query&titles='
        + urllib.parse.quote(title_jp)
        + '&prop=pageimages&format=json&pithumbsize=800'
    )
    data = api_get(url)
    pages = data.get('query', {}).get('pages', {})
    for pid, pdata in pages.items():
        if pid == '-1':
            return None
        # pageimage gives the filename
        img = pdata.get('pageimage')
        if img:
            return img
    return None


def get_image_from_en_wiki(title_en):
    """Get the main image filename from English Wikipedia article."""
    url = (
        'https://en.wikipedia.org/w/api.php?action=query&titles='
        + urllib.parse.quote(title_en)
        + '&prop=pageimages&format=json&pithumbsize=800'
    )
    data = api_get(url)
    pages = data.get('query', {}).get('pages', {})
    for pid, pdata in pages.items():
        if pid == '-1':
            return None
        img = pdata.get('pageimage')
        if img:
            return img
    return None


def get_commons_info(filename):
    """Get artist and license info from Wikimedia Commons for a given filename."""
    url = (
        'https://commons.wikimedia.org/w/api.php?action=query&titles=File:'
        + urllib.parse.quote(filename)
        + '&prop=imageinfo&iiprop=extmetadata|url&format=json'
    )
    data = api_get(url)
    pages = data.get('query', {}).get('pages', {})
    for pid, pdata in pages.items():
        if pid == '-1':
            return None
        imageinfo = pdata.get('imageinfo', [])
        if not imageinfo:
            return None
        info = imageinfo[0]
        ext = info.get('extmetadata', {})

        artist_html = ext.get('Artist', {}).get('value', 'Unknown')
        # Strip HTML tags from artist
        import re
        artist = re.sub(r'<[^>]+>', '', artist_html).strip()
        # Clean up multiple spaces
        artist = re.sub(r'\s+', ' ', artist)

        license_short = ext.get('LicenseShortName', {}).get('value', 'Unknown')
        license_url_val = ext.get('LicenseUrl', {}).get('value', '')

        desc_url = info.get('descriptionurl', '')
        original_url = info.get('url', '')

        return {
            'artist': artist,
            'license': license_short,
            'license_url': license_url_val,
            'source': desc_url,
            'original_url': original_url,
        }
    return None


def main():
    # Load existing credits
    with open(CREDITS_JSON, 'r', encoding='utf-8') as f:
        credits = json.load(f)

    print(f"Existing entries: {len(credits)}")

    added = 0
    failed = []

    for fish_id, info in MISSING_FISH.items():
        if fish_id in credits:
            print(f"  SKIP {fish_id} - already in credits")
            continue

        print(f"\n--- Processing {fish_id} ({info['name_jp']}) ---")

        # Try Japanese Wikipedia first
        filename = None
        print(f"  Trying ja.wikipedia: {info['wiki_jp']}")
        try:
            filename = get_image_from_jp_wiki(info['wiki_jp'])
        except Exception as e:
            print(f"  Error with ja.wiki: {e}")

        time.sleep(1)

        # If not found, try English Wikipedia
        if not filename:
            print(f"  Trying en.wikipedia: {info['wiki_en']}")
            try:
                filename = get_image_from_en_wiki(info['wiki_en'])
            except Exception as e:
                print(f"  Error with en.wiki: {e}")
            time.sleep(1)

        if not filename:
            print(f"  WARNING: No image found for {fish_id}")
            # Use a fallback credit
            credits[fish_id] = {
                'name_jp': info['name_jp'],
                'artist': 'Wikimedia Commons',
                'license': 'CC BY-SA',
                'license_url': '',
                'source': '',
                'original_url': '',
            }
            added += 1
            failed.append(fish_id)
            continue

        print(f"  Found image: {filename}")

        # Get Commons info
        print(f"  Fetching Commons info...")
        try:
            commons_info = get_commons_info(filename)
        except Exception as e:
            print(f"  Error getting Commons info: {e}")
            commons_info = None

        time.sleep(2)

        if commons_info:
            credits[fish_id] = {
                'name_jp': info['name_jp'],
                'artist': commons_info['artist'],
                'license': commons_info['license'],
                'license_url': commons_info['license_url'],
                'source': commons_info['source'],
                'original_url': commons_info['original_url'],
            }
            print(f"  OK: artist={commons_info['artist'][:50]}, license={commons_info['license']}")
        else:
            credits[fish_id] = {
                'name_jp': info['name_jp'],
                'artist': 'Wikimedia Commons',
                'license': 'CC BY-SA',
                'license_url': '',
                'source': '',
                'original_url': '',
            }
            failed.append(fish_id)
            print(f"  FALLBACK: no Commons info found")

        added += 1

    print(f"\n=== Added {added} entries. Total: {len(credits)} ===")
    if failed:
        print(f"Used fallback for: {failed}")

    # Save JSON
    with open(CREDITS_JSON, 'w', encoding='utf-8') as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)
    print(f"Saved {CREDITS_JSON}")

    # Generate JS
    lines = ['const FISH_CREDITS = {']
    for fid, fdata in credits.items():
        artist = fdata.get('artist', 'Unknown').replace('"', '\\"')
        license_val = fdata.get('license', 'Unknown').replace('"', '\\"')
        lines.append(f'  "{fid}": {{ artist: "{artist}", license: "{license_val}" }},')
    lines.append('};')

    with open(CREDITS_JS, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Saved {CREDITS_JS}")


if __name__ == '__main__':
    main()
