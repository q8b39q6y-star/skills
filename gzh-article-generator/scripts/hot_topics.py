#!/usr/bin/env python3
"""微博热搜抓取脚本 — 配合 gzh 内容工作台技能使用

用法:
    python hot_topics.py              # 抓取微博热搜，存到 ~/.weibo_hot/
    python hot_topics.py --limit 30   # 自定义抓取条数
    python hot_topics.py --json       # 直接输出 JSON 到 stdout（不写磁盘）
    python hot_topics.py --out DIR    # 自定义输出目录

数据存储（按日期存档）:
    ~/.weibo_hot/YYYY-MM-DD.json   # 当日快照
    ~/.weibo_hot/latest.json       # 最新一份（下游直接读这个路径）
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

WEIBO_API = "https://weibo.com/ajax/side/hotSearch"
DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), ".weibo_hot")
DEFAULT_LIMIT = 30
TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_weibo_hot(limit=DEFAULT_LIMIT):
    """从微博热搜 API 抓取实时热榜，返回 list[dict]"""
    request = urllib.request.Request(
        WEIBO_API,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://weibo.com",
            "Accept": "application/json, text/plain, */*",
        },
    )
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(f"[warn] 微博 API HTTP 错误: {exc.code}", file=sys.stderr)
        return []
    except urllib.error.URLError as exc:
        print(f"[warn] 网络请求失败: {exc.reason}", file=sys.stderr)
        return []
    except TimeoutError:
        print("[warn] 微博 API 请求超时", file=sys.stderr)
        return []
    except json.JSONDecodeError as exc:
        print(f"[warn] 微博 API 返回非 JSON: {exc}", file=sys.stderr)
        return []
    except Exception as exc:  # noqa: BLE001 - 网络层兜底
        print(f"[warn] 未知错误: {exc}", file=sys.stderr)
        return []

    if payload.get("ok") != 1:
        message = payload.get("error") or payload.get("msg") or "unknown"
        print(f"[warn] 微博 API 返回异常: {message}", file=sys.stderr)
        return []

    results = []
    for item in payload.get("data", {}).get("realtime", [])[:limit]:
        word = item.get("word", "")
        results.append(
            {
                "rank": item.get("realpos"),
                "word": word,
                "note": item.get("note", ""),
                "heat": item.get("num"),
                "label": item.get("label_name") or "",
                "url": f"https://s.weibo.com/weibo?q={word}",
            }
        )
    return results


def save_results(results, data_dir):
    """保存结果到数据目录，返回 (日期文件路径, latest 路径)"""
    os.makedirs(data_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc)
    today = timestamp.strftime("%Y-%m-%d")

    payload = {
        "source": "weibo",
        "fetch_time": timestamp.isoformat(),
        "count": len(results),
        "topics": results,
    }

    date_path = os.path.join(data_dir, f"{today}.json")
    latest_path = os.path.join(data_dir, "latest.json")

    for path in (date_path, latest_path):
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    return date_path, latest_path


def output_summary(results):
    """打印可读摘要"""
    print(f"\n微博热搜 TOP{len(results)}  ({datetime.now().strftime('%m-%d %H:%M')})\n")
    print(f"{'排名':<6}{'话题':<30}{'热度'}")
    print("-" * 60)
    for row in results:
        rank = f"#{row['rank'] or '?'}"
        word = row["word"][:28]
        heat = row["heat"] or 0
        note = f" — {row['note'][:20]}" if row["note"] else ""
        print(f"{rank:<6}{word:<30}{heat:>6,}{note}")


def main():
    parser = argparse.ArgumentParser(description="微博热搜抓取")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="抓取条数 (默认30)")
    parser.add_argument("--json", action="store_true", help="直接输出 JSON 到 stdout")
    parser.add_argument("--out", default=DEFAULT_DATA_DIR, help="输出目录 (默认 ~/.weibo_hot)")
    args = parser.parse_args()

    results = fetch_weibo_hot(limit=args.limit)

    if not results:
        print("[warn] 未获取到热搜数据", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    output_summary(results)
    date_path, latest_path = save_results(results, args.out)
    print(f"\n已保存: {date_path}")
    print(f"  最新: {latest_path}")


if __name__ == "__main__":
    main()
