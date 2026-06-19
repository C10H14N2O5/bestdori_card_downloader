# BangDream Card Downloader Usage

This skill bundles `scripts/bestdori_card_downloader.py`, a frozen Python CLI for drawing and downloading BanG Dream card images through the Bestdori API.

## Modes

| Mode | How to run | What it does |
| --- | --- | --- |
| Filtered random | `-c <character> -r <rarity>` | Choose a character and rarity, then draw a matching card. |
| Pure random | `--random` | Draw from all 3-star, 4-star, and 5-star cards without character filtering. |
| Interactive | no arguments | Show a numeric menu for filtered draw, pure random, cache refresh, or exit. |

## CLI Parameters

| Parameter | Meaning | Examples |
| --- | --- | --- |
| `--character`, `-c` | Character ID or fuzzy character name. | `-c 4`, `-c "沙绫"`, `-c "纱夜"` |
| `--rarity`, `-r` | Rarity filter: digit combinations like `345`, `34`, `45`, `35`, or single digits `3`, `4`, `5`; default is `345`. | `-r 5`, `-r 345` |
| `--random` | Pure random mode across all 3-star, 4-star, and 5-star cards. | `--random` |
| `--no-dedup` | Ignore the 14-day dedup record and do not record the draw. | `--random --no-dedup` |

## Recommended Agent Invocation

Prefer PowerShell on Windows:

```powershell
Set-Location <skill-directory>
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py --random --no-dedup
```

For a specific character:

```powershell
Set-Location <skill-directory>
$env:PYTHONIOENCODING='utf-8'
python scripts/bestdori_card_downloader.py -c 4 -r 345
```

## Interactive Menu

Run without arguments:

```powershell
python scripts/bestdori_card_downloader.py
```

Menu choices:

- `1`: filtered random draw by character and rarity.
- `2`: pure random draw from all 3-star, 4-star, and 5-star cards.
- `3`: refresh the Bestdori character cache.
- `0`: exit.

## Character Filtering

The script displays and filters the 40 main band members with `characterId` 1-40:

- 1-5: Poppin'Party
- 6-10: Afterglow
- 11-15: Hello, Happy World!
- 16-20: Pastel*Palettes
- 21-25: Roselia
- 26-30: Morfonica
- 31-35: RAISE A SUILEN
- 36-40: MyGO!!!!!

Numeric character queries match `characterId` directly. Text queries use fuzzy substring matching against cached character names.

## Output

Downloaded PNG images are saved to:

```text
~/Downloads/Bangdream_Temp/
```

Filename pattern:

```text
{character_name}_{rarity}_{card_prefix}_{after_training|normal}.png
```

The script prefers `after_training` images and falls back to `normal`.

## State Files

The output directory also stores:

- `char_cache.json`: cached Bestdori character names.
- `dedup.json`: card IDs drawn in the last 14 days.

When `--no-dedup` is used, deduplication is ignored and the draw is not recorded.

## Dependency

Install:

```powershell
python -m pip install bestdori-api
```

Import modules used by the script:

```python
import bestdori
import bestdori.cards
import bestdori.characters
```

## Known Issues

- Windows console output may fail on `✓` or Japanese/Chinese names unless `PYTHONIOENCODING=utf-8` is set.
- The first run needs network access to fetch character and card data.
- Bestdori server slowness may cause timeouts; retry the command.
- Writing output may require permission for the user's Downloads folder.
