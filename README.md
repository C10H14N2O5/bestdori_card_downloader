# Bestdori Card Downloader

一个基于 Bestdori API 的 Bang Dream! 卡面随机抽取与下载脚本。它会从四星、五星卡池中随机抽取卡面，并自动下载图片到本地。

这是一个个人向、非官方的小工具，主要用于个人学习、收藏和娱乐用途。项目开发过程中使用了 AI 辅助生成代码，作者负责需求设计、测试和调整。

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
pip install -r requirements.txt
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

## 设计取向

本项目最初是按智能体 skill / 自动化调用场景设计的，因此输出目录和缓存目录默认固定为 `~/Downloads/Bangdream_Temp/`。这样可以让调用方稳定地找到最近下载的卡面和运行缓存，也避免把下载图片、缓存文件写进仓库目录。

当前版本暂不提供交互式修改输出目录的功能。如果需要更改保存位置，可以直接修改脚本顶部的 `OUTPUT_DIR` 配置。

## Skill 版本

仓库中也包含一个面向智能体调用的 skill 版本，位于：

```text
skills/bangdream-card-draw/
```

该目录包含 skill 描述、使用说明和一份自包含的脚本副本，方便在支持 skill 的智能体环境中直接安装或引用。根目录脚本和 skill 内脚本应保持同步。

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

## 开发与维护说明

这个项目目前定位为轻量级脚本，而不是完整的软件包。它依赖 Bestdori API 和远程图片资源，如果 API 字段、图片地址或第三方库行为发生变化，脚本可能需要同步调整。

欢迎提交 issue 或 pull request，不过维护节奏会以个人使用需求为主。

## 免责声明

本项目不是 BanG Dream!、Craft Egg、Bushiroad 或 Bestdori 的官方项目，也不与上述实体存在关联。

脚本下载的卡面图片及相关角色、作品名称的版权归其各自权利方所有。本项目仅提供基于公开接口的个人使用脚本，请勿将下载内容用于违反相关权利方条款或当地法律法规的用途。

## 开源协议

本项目使用 WTFPL v2。简单说，就是你想怎么用就怎么用；完整条款见 [LICENSE](LICENSE)。
