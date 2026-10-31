#!/usr/bin/env python3
"""微博热搜抓取脚本 — 配合 gzh 内容工作台技能使用

用法:
    python hot_topics.py              # 抓取微博热搜，存到 $WEIBO_HOT_DATA_DIR（默认 ~/.weibo_hot）
    python hot_topics.py --limit 30   # 自定义抓取条数
    python hot_topics.py --json       # 直接输出 JSON 到 stdout（不写磁盘）

数据存储（可用 WEIBO_HOT_DATA_DIR 环境变量覆盖）:
    ~/.weibo_hot/YYYY-MM-DD.json   # 按日期存档
    ~/.weibo_hot/latest.json       # 最新一份（下游直接读这个路径）
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

DATA_DIR = os.environ.get(
    "WEIBO_HOT_DATA_DIR",
    os.path.expanduser("~/.weibo_hot"),
)
TIMEOUT = 15


def fetch_weibo_hot(limit: int = 30) -> list[dict]:
    """从微博热搜 API 抓取实时热榜"""
    cmd = [
        "curl", "-s",
        "https://weibo.com/ajax/side/hotSearch",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H", "Referer: https://weibo.com",
        "-H", "Accept: application/json, text/plain, */*",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        if out.returncode != 0 or not out.stdout.strip():
            return []
        data = json.loads(out.stdout)
        if data.get("ok") != 1:
            err_msg = data.get("error", data.get("msg", "unknown"))
            print(f"[warn] 微博 API 返回异常: {err_msg}", file=sys.stderr)
            return []
        realtime = data["data"].get("realtime", [])
        results = []
        for item in realtime[:limit]:
            results.append({
                "rank": item.get("realpos"),
                "word": item.get("word", ""),
                "note": item.get("note", ""),
                "heat": item.get("num"),
                "label": item.get("label_name") or "",
                "url": f"https://s.weibo.com/weibo?q={item.get('word', '')}",
            })
        return results
    except subprocess.TimeoutExpired:
        print("[warn] 微博 API 请求超时", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[warn] 微博 API 返回非 JSON: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[warn] 未知错误: {e}", file=sys.stderr)
        return []


def save_results(results: list[dict]) -> str:
    """保存结果到数据目录"""
    os.makedirs(DATA_DIR, exist_ok=True)

    ts = datetime.now(timezone.utc)
    today = ts.strftime("%Y-%m-%d")
    full_ts = ts.isoformat()

    payload = {
        "source": "weibo",
        "fetch_time": full_ts,
        "count": len(results),
        "topics": results,
    }

    # 写入按日期命名的文件
    date_path = os.path.join(DATA_DIR, f"{today}.json")
    with open(date_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # 更新 latest.json（方便下游读取）
    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return date_path


def output_summary(results: list[dict]):
    """打印可读摘要"""
    print(f"\n📡 微博热搜 TOP{len(results)}  ({datetime.now().strftime('%m-%d %H:%M')})\n")
    print(f"{'排名':<6}{'话题':<30}{'热度'}")
    print("-" * 60)
    for r in results:
        rank = f"#{r['rank'] or '?'}"
        word = r["word"][:28]
        heat = r["heat"] or 0
        note = f" — {r['note'][:20]}" if r["note"] else ""
        print(f"{rank:<6}{word:<30}{heat:>6,}{note}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="微博热搜抓取")
    parser.add_argument("--limit", type=int, default=30, help="抓取条数 (默认30)")
    parser.add_argument("--json", action="store_true", help="直接输出 JSON 到 stdout")
    args = parser.parse_args()

    results = fetch_weibo_hot(limit=args.limit)

    if not results:
        print("[warn] 未获取到热搜数据", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    output_summary(results)
    saved_path = save_results(results)
    print(f"\n✅ 已保存: {saved_path}")
    print(f"   最新:   {os.path.join(DATA_DIR, 'latest.json')}")


if __name__ == "__main__":
    main()
