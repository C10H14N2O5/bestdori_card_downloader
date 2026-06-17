# Bestdori Card Downloader

一个基于 Bestdori API 的 Bang Dream! 卡面随机抽取与下载脚本。它会从四星、五星卡池中随机抽取卡面，并自动下载图片到本地。

脚本支持两种使用方式：

- CLI 快速模式：直接在命令行传入角色、星级等参数。
- 交互模式：启动脚本后按提示输入数字选择模式、角色和星级。

## 功能

- 按角色和星级筛选后随机抽取卡面。
- 从全部四星、五星卡池中纯随机抽取。
- 支持角色名称模糊匹配，也支持直接使用角色 ID。
- 默认启用 14 天去重，避免短期内重复抽到同一卡面。
- 自动缓存角色数据，减少重复请求。
- 优先下载特训后卡面，失败时回退到普通卡面。

## 环境要求

- Python 3.10 或更新版本
- `bestdori-api` Python 包，导入模块名为 `bestdori`
- 可访问 Bestdori API 的网络环境

安装依赖：

```bash
pip install bestdori-api
```

## 使用方法

进入脚本所在目录：

```bash
cd bestdori-card-downloader
```

### 交互模式

不传参数启动脚本：

```bash
python bestdori_card_downloader.py
```

启动后可以输入对应数字操作：

- `1`：筛选后随机，先选角色，再选星级。
- `2`：纯随机，从全部四星、五星卡池中抽取。
- `3`：刷新角色缓存。
- `0`：退出。

筛选后随机模式会继续提示：

- 角色序号：从脚本列出的角色列表中选择。
- 星级：输入 `4`、`5` 或 `45`，其中 `45` 表示四星和五星都可以。

### CLI 快速模式

按角色和星级抽取：

```bash
python bestdori_card_downloader.py -c 沙绫 -r 45
```

只抽五星：

```bash
python bestdori_card_downloader.py -c 纱夜 -r 5
```

使用角色 ID：

```bash
python bestdori_card_downloader.py -c 4 -r 45
```

不限角色纯随机：

```bash
python bestdori_card_downloader.py --random
```

忽略 14 天去重记录：

```bash
python bestdori_card_downloader.py -c 沙绫 -r 45 --no-dedup
```

## 参数说明

| 参数 | 简写 | 说明 |
| --- | --- | --- |
| `--character` | `-c` | 角色名称或角色 ID。名称支持模糊匹配。 |
| `--rarity` | `-r` | 星级筛选，可选 `4`、`5`、`45`，默认 `45`。 |
| `--random` |  | 纯随机模式，从全部四星、五星卡池中抽取。 |
| `--no-dedup` |  | 忽略近期去重记录。 |

## 输出位置

下载的卡面会保存到：

```text
~/Downloads/Bangdream_Temp/
```

脚本还会在该目录保存运行缓存：

- `char_cache.json`：角色缓存。
- `dedup.json`：14 天去重记录。

## 角色范围

交互模式下，脚本主要展示 `characterId` 为 `1-40` 的 40 名乐队成员，对应：

- Poppin'Party
- Afterglow
- Hello, Happy World!
- Pastel*Palettes
- Roselia
- Morfonica
- RAISE A SUILEN
- MyGO!!!!!

## 常见问题

如果首次运行比较慢，通常是因为脚本正在拉取角色列表和卡牌数据。

如果下载失败，可以稍后重试。Bestdori API 或图片资源偶尔可能响应较慢。

如果角色列表异常，可以在交互模式中输入 `3` 刷新角色缓存。

如果某个角色近期可抽卡面都已抽过，脚本会临时忽略去重并回退到原卡池。
