---
name: bangdream-card-draw
description: Draw and download BanG Dream card images through the bundled Bestdori API Python script. Use when the user asks to draw a random Bang Dream or BanG Dream card, fetch a Bestdori card image, download a card face, choose a card by character and rarity, use a Bandori card randomizer, or run the BangDream card draw CLI.
---

# BangDream Card Draw

## Quick Start

Use the bundled script at `scripts/bestdori_card_downloader.py`. Prefer CLI mode for agent use because it is deterministic and does not require interactive prompts.

On Windows, set UTF-8 output before running the script so the check mark and Japanese/Chinese card names print correctly:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py --random --no-dedup
```

The Python package dependency is `bestdori-api`; it provides the import module named `bestdori`.

```powershell
python -m pip install bestdori-api
```

## Common Commands

Draw one random 3-star, 4-star, or 5-star card from the full card pool:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py --random
```

Draw one random card without updating or using the 14-day dedup record:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py --random --no-dedup
```

Draw by character ID and rarity:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py -c 4 -r 345
```

Draw by fuzzy character name and rarity:

```powershell
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py -c "沙绫" -r 5
```

## Behavior

- `--character` / `-c` accepts a character ID or fuzzy character name.
- `--rarity` / `-r` accepts digit combinations like `345` (all), `34` (3+4), `45` (4+5), `35` (3+5), or single digits `3`, `4`, `5`; default is `345`.
- `--random` ignores character filtering and draws from all 3-star, 4-star, and 5-star cards.
- `--no-dedup` ignores the 14-day deduplication record and does not record the draw.
- With no CLI arguments, the script enters the original interactive menu: `1` filtered random, `2` pure random, `3` refresh character cache, `0` exit.

## Outputs And State

The script writes downloaded PNG card images and cache files to the current user's downloads folder:

```text
~/Downloads/Bangdream_Temp/
```

Files in that directory include:

- Downloaded PNG images named from character, rarity, card title, and image type.
- `char_cache.json` for Bestdori character names.
- `dedup.json` for the 14-day recent draw record.

The script first tries `after_training` card art, then falls back to `normal`.

## Troubleshooting

- If `ModuleNotFoundError: No module named 'bestdori'` appears, install `bestdori-api`.
- If Windows raises `UnicodeEncodeError` while printing output, set `PYTHONIOENCODING=utf-8`.
- If the output directory cannot be created, request permission to write to `~/Downloads/Bangdream_Temp/`.
- If Bestdori is slow or unavailable, retry; the script sets a 30-second request timeout.
- For fuller parameter and workflow details, read `references/usage.md`.
