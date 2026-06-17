#!/usr/bin/env python3
"""
Bang Dream! 卡面下载工具
功能：按角色/星级筛选后随机抽取卡面图片，支持纯随机与去重。
"""

import bestdori
import bestdori.cards as cards
import bestdori.characters as chars
import json
import random
import re
import argparse
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ============ 配置 ============
OUTPUT_DIR = Path.home() / "Downloads" / "Bangdream_Temp"
DEDUP_FILE = OUTPUT_DIR / "dedup.json"
CHAR_CACHE_FILE = OUTPUT_DIR / "char_cache.json"
DEDUP_DAYS = 14
REQUEST_TIMEOUT = 30
bestdori.settings.timeout = REQUEST_TIMEOUT

# ============ 工具函数 ============

def sanitize_filename(name: str) -> str:
    """清理 Windows 文件名中的非法字符"""
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def load_json(path: Path):
    """安全加载 JSON 文件"""
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def save_json(path: Path, data):
    """安全保存 JSON 文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============ 角色缓存 ============

def fetch_characters():
    """从 Bestdori API 拉取角色列表，返回 {id: name} 映射"""
    print("  正在从 Bestdori 拉取角色列表...")
    try:
        data = chars.get_all(2)
    except Exception as e:
        print(f"  [错误] 拉取角色列表失败: {e}")
        return None

    char_map = {}
    for cid_str, info in data.items():
        cid = int(cid_str)
        names = info.get('characterName', [])
        # 优先级: zh-CN(3) > zh-TW(2) > ja(0) > en(1)
        name = None
        for idx in [3, 2, 0, 1]:
            if idx < len(names) and names[idx]:
                name = names[idx]
                break
        if not name:
            name = f"Character_{cid}"
        char_map[cid] = name

    return char_map


def load_character_cache():
    """加载角色缓存，没有则自动拉取"""
    cache = load_json(CHAR_CACHE_FILE)
    if cache:
        # 转换字符串 key 为 int
        return {int(k): v for k, v in cache.items()}
    print("未找到角色缓存，自动拉取...")
    char_map = fetch_characters()
    if char_map:
        save_json(CHAR_CACHE_FILE, char_map)
        print(f"  已缓存 {len(char_map)} 个角色")
    return char_map


def refresh_character_cache():
    """强制刷新角色缓存"""
    print("正在刷新角色缓存...")
    char_map = fetch_characters()
    if char_map:
        save_json(CHAR_CACHE_FILE, char_map)
        print(f"✓ 已刷新并缓存 {len(char_map)} 个角色")
        return char_map
    else:
        print("[错误] 刷新失败，将使用旧缓存")
        return load_character_cache()


# ============ 去重管理 ============

def load_dedup():
    """加载去重记录，返回 {card_id: drawn_at_str}"""
    return load_json(DEDUP_FILE)


def clean_dedup(dedup: dict) -> dict:
    """清理超过 DEDUP_DAYS 天的记录"""
    cutoff = datetime.now() - timedelta(days=DEDUP_DAYS)
    cleaned = {}
    for cid_str, timestamp_str in dedup.items():
        try:
            dt = datetime.fromisoformat(timestamp_str)
            if dt >= cutoff:
                cleaned[cid_str] = timestamp_str
        except (ValueError, TypeError):
            # 无效格式，丢弃
            pass
    return cleaned


def save_dedup(dedup: dict):
    """保存去重记录"""
    save_json(DEDUP_FILE, dedup)


def record_drawn(card_id: int, dedup: dict):
    """记录已抽取的卡牌"""
    dedup[str(card_id)] = datetime.now().isoformat()
    save_dedup(dedup)


# ============ 卡牌数据 ============

def fetch_all_cards():
    """获取全量卡牌数据 (四星+五星)"""
    print("  正在拉取卡牌数据...")
    try:
        data = cards.get_all(5)
    except Exception as e:
        print(f"  [错误] 拉取卡牌数据失败: {e}")
        return None

    result = []
    for cid_str, info in data.items():
        rarity = info.get('rarity', 0)
        if rarity in (4, 5):
            result.append({
                'id': int(cid_str),
                'characterId': info.get('characterId', 0),
                'rarity': rarity,
                'attribute': info.get('attribute', ''),
                'resourceSetName': info.get('resourceSetName', ''),
                'prefix': info.get('prefix', ['']),
            })
    return result


def get_card_name(card: dict, char_map: dict) -> str:
    """获取卡牌的显示名称"""
    char_name = char_map.get(card['characterId'], f"Unknown_{card['characterId']}")
    rarity_stars = {4: '四星', 5: '五星'}.get(card['rarity'], f"{card['rarity']}星")
    # prefix 可能有多个训练阶段的名字，取第一个非空的
    prefix = ''
    if card.get('prefix'):
        for p in card['prefix']:
            if p:
                prefix = p
                break
    parts = [char_name, rarity_stars]
    if prefix:
        parts.append(prefix)
    return '_'.join(parts)


def download_card_image(card: dict, char_map: dict) -> Path | None:
    """下载卡面图片，优先下载特训后(after_training)，返回文件路径"""
    card_id = card['id']
    card_name = get_card_name(card, char_map)
    safe_name = sanitize_filename(card_name)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 尝试下载特训后图，失败则下载普通图
    for img_type in ('after_training', 'normal'):
        try:
            card_obj = cards.Card(card_id)
            img_bytes = card_obj.get_card(img_type)  # type: ignore
            if img_bytes and len(img_bytes) > 100:  # 确保不是空图或太小
                ext = '.png'
                filename = f"{safe_name}_{img_type}{ext}"
                filepath = OUTPUT_DIR / filename
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                return filepath
        except Exception as e:
            print(f"    [{img_type}] 下载失败: {e}")
            continue

    return None


# ============ 抽取逻辑 ============

def build_available_pool(all_cards: list, dedup: dict, char_id: int | None, rarity: int | None):
    """构建可用卡池（过滤去重后的），返回候选列表"""
    # 筛选
    pool = all_cards
    if char_id is not None:
        pool = [c for c in pool if c['characterId'] == char_id]
    if rarity is not None:
        pool = [c for c in pool if c['rarity'] == rarity]

    if not pool:
        return []

    # 去重：过滤最近 DEDUP_DAYS 天内抽过的
    recent_ids = set(dedup.keys())
    available = [c for c in pool if str(c['id']) not in recent_ids]

    # 如果过滤后为空，回退到原池
    if not available:
        print("  (所有卡牌近期都已抽过，暂时忽略去重)")
        return pool

    return available


def draw_filtered(char_map: dict, all_cards: list, dedup: dict):
    """模式1：筛选后随机"""
    # 仅保留 8 个乐队的 40 名成员，排除 NPC 和配角
    # Poppin'Party、Afterglow、HHW、Pastel*Palettes、Roselia、Morfonica、RAS、MyGO!!!!!
    band_character_ids = set(range(1, 41))

    # 显示角色列表
    char_list = sorted(
        [(cid, name) for cid, name in char_map.items() if cid in band_character_ids],
        key=lambda x: x[0]
    )
    if not char_list:
        print("\n[错误] 角色列表为空，请刷新角色缓存")
        return

    print("\n角色列表：")
    for i, (cid, name) in enumerate(char_list, 1):
        print(f"  {i:2d}. {name} (ID:{cid})")
    print()

    # 选择角色
    while True:
        try:
            choice = input(f"请输入角色序号 (1-{len(char_list)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(char_list):
                selected_char_id = char_list[idx][0]
                selected_char_name = char_list[idx][1]
                break
            else:
                print(f"  请输入 1 到 {len(char_list)} 之间的数字")
        except ValueError:
            print("  请输入有效数字")
        except (EOFError, KeyboardInterrupt):
            print("\n已取消")
            return

    # 选择星级
    while True:
        choice = input("请选择星级 (4=四星, 5=五星, 45=两者皆可): ").strip()
        if choice == '4':
            rarity = 4
            rarity_label = '四星'
            break
        elif choice == '5':
            rarity = 5
            rarity_label = '五星'
            break
        elif choice == '45':
            rarity = None
            rarity_label = '四星+五星'
            break
        else:
            print("  请输入 4、5 或 45")

    # 构建卡池
    pool = build_available_pool(all_cards, dedup, selected_char_id, rarity)
    if not pool:
        print(f"\n[错误] 没有找到符合条件的卡牌（{selected_char_name} {rarity_label}）")
        return

    # 随机抽取
    card = random.choice(pool)
    card_name = get_card_name(card, char_map)
    print(f"\n抽到了: {card_name} (卡牌ID: {card['id']})")

    # 下载
    print("正在下载...")
    filepath = download_card_image(card, char_map)
    if filepath:
        print(f"✓ 下载完成: {filepath}")
        record_drawn(card['id'], dedup)
    else:
        print("[错误] 下载失败，请检查网络连接")


def draw_pure_random(char_map: dict, all_cards: list, dedup: dict):
    """模式2：纯随机 (四星+五星，不限角色)"""
    pool = build_available_pool(all_cards, dedup, None, None)
    if not pool:
        print("[错误] 卡池为空，请检查数据")
        return

    card = random.choice(pool)
    card_name = get_card_name(card, char_map)
    print(f"\n抽到了: {card_name} (卡牌ID: {card['id']})")

    print("正在下载...")
    filepath = download_card_image(card, char_map)
    if filepath:
        print(f"✓ 下载完成: {filepath}")
        record_drawn(card['id'], dedup)
    else:
        print("[错误] 下载失败，请检查网络连接")


# ============ 命令行快速模式 ============

def match_character(query: str, char_map: dict):
    """根据名称或ID匹配角色，返回 (char_id, char_name) 或 None"""
    # 纯数字 -> ID 匹配
    if query.isdigit():
        cid = int(query)
        if cid in char_map:
            return (cid, char_map[cid])
        return None

    # 模糊匹配 (忽略大小写，包含匹配)
    query_lower = query.lower()
    candidates = []
    for cid, name in char_map.items():
        if query_lower in name.lower():
            candidates.append((cid, name))

    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        print(f"[警告] 找到多个匹配角色：{', '.join(n for _, n in candidates)}")
        print(f"  将使用第一个匹配: {candidates[0][1]}")
        return candidates[0]

    return None


def fast_mode(args):
    """命令行快速模式：一行命令完成抽卡下载"""
    char_map = load_character_cache()
    if not char_map:
        print("[错误] 无法获取角色数据，程序退出")
        sys.exit(1)

    print("正在加载卡牌数据...")
    all_cards = fetch_all_cards()
    if not all_cards:
        print("[错误] 无法获取卡牌数据，程序退出")
        sys.exit(1)
    print(f"  已加载 {len(all_cards)} 张四星/五星卡牌")

    dedup = {} if args.no_dedup else clean_dedup(load_dedup())
    if not args.no_dedup:
        print(f"  去重记录: {len(dedup)} 条 (近{DEDUP_DAYS}天)")

    if args.random:
        # 纯随机模式
        pool = build_available_pool(all_cards, dedup, None, None)
        if not pool:
            print("[错误] 卡池为空")
            sys.exit(1)
        card = random.choice(pool)
        print("\n模式: 纯随机 (全四五星卡池)")
    else:
        # 筛选模式
        match = match_character(args.character, char_map)
        if not match:
            band_ids = set(range(1, 41))
            band_chars = {cid: name for cid, name in char_map.items() if cid in band_ids}
            print(f"[错误] 未找到角色: {args.character}")
            print(f"可用角色: {', '.join(f'{name}(ID:{cid})' for cid, name in sorted(band_chars.items()))}")
            sys.exit(1)

        char_id, char_name = match
        rarity = {'4': 4, '5': 5}.get(args.rarity, None)
        rarity_label = {'4': '四星', '5': '五星'}.get(args.rarity, '四星+五星')

        pool = build_available_pool(all_cards, dedup, char_id, rarity)
        if not pool:
            print(f"[错误] 没有找到符合条件的卡牌（{char_name} {rarity_label}）")
            sys.exit(1)

        card = random.choice(pool)
        print(f"\n筛选: {char_name} | {rarity_label} | 候选 {len(pool)} 张")

    card_name = get_card_name(card, char_map)
    print(f"抽到了: {card_name} (卡牌ID: {card['id']})")

    print("正在下载...")
    filepath = download_card_image(card, char_map)
    if filepath:
        print(f"✓ 下载完成: {filepath}")
        if not args.no_dedup:
            record_drawn(card['id'], dedup)
    else:
        print("[错误] 下载失败，请检查网络连接")
        sys.exit(1)


# ============ 主菜单 ============

def main():
    # ---- 命令行参数解析 (快速模式) ----
    parser = argparse.ArgumentParser(description='Bang Dream! 卡面随机抽取工具')
    parser.add_argument('-c', '--character', type=str, help='角色名称或ID，支持模糊匹配 (如: saya, 山吹沙绫, 4)')
    parser.add_argument('-r', '--rarity', type=str, default='45', choices=['4', '5', '45'],
                        help='星级: 4=四星, 5=五星, 45=两者皆可 (默认: 45)')
    parser.add_argument('--random', action='store_true', help='纯随机模式 (全四五星卡池)')
    parser.add_argument('--no-dedup', action='store_true', help='忽略去重记录')
    args_cli = parser.parse_args()
    if args_cli.random or args_cli.character:
        fast_mode(args_cli)
        return
    # ---- 原有交互模式 ----
    print("=" * 50)
    print("  Bang Dream! 卡面随机抽取工具")
    print("=" * 50)

    # 初始化
    char_map = load_character_cache()
    if not char_map:
        print("[错误] 无法获取角色数据，程序退出")
        return

    print("正在加载卡牌数据...")
    all_cards = fetch_all_cards()
    if not all_cards:
        print("[错误] 无法获取卡牌数据，程序退出")
        return
    print(f"  已加载 {len(all_cards)} 张四星/五星卡牌")

    dedup = clean_dedup(load_dedup())
    recent_count = len(dedup)
    print(f"  去重记录: {recent_count} 条 (近{DEDUP_DAYS}天)")

    # 主循环
    while True:
        print("\n" + "-" * 40)
        print("请选择模式：")
        print("  1. 筛选后随机 (按角色+星级)")
        print("  2. 纯随机 (全四五星卡池)")
        print("  3. 刷新角色缓存")
        print("  0. 退出")
        print("-" * 40)

        try:
            choice = input("请输入选项: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见~")
            break

        if choice == '1':
            draw_filtered(char_map, all_cards, dedup)
        elif choice == '2':
            draw_pure_random(char_map, all_cards, dedup)
        elif choice == '3':
            new_map = refresh_character_cache()
            if new_map:
                char_map = new_map
        elif choice == '0':
            print("再见~")
            break
        else:
            print("无效选项，请重新输入")

        # 每次操作后清理去重记录
        dedup = clean_dedup(dedup)


if __name__ == '__main__':
    main()
