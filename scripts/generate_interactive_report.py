"""
从 docs/report_data.json 读取结构化数据，生成 docs/index.html（单文件，内联 JS）。

Usage:
    python scripts/generate_interactive_report.py

工作流程：
    python scripts/generate_report_data.py    # 从 Markdown 提取数据 → docs/report_data.json
    python scripts/generate_interactive_report.py  # 更新 index.html 中的数据区段
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent
REPORT_DATA_PATH = PROJECT_DIR / "docs" / "report_data.json"
OUTPUT_HTML_PATH = PROJECT_DIR / "docs" / "index.html"


def read_report_data():
    with open(REPORT_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_data_js(data):
    """从 JSON 数据生成新的 INLINE_REPORT_DATA JS 变量"""
    inline = {
        "meta": data["meta"],
        "principles": data["principles"],
        "checklist": data["checklist"],
        "scenarios": data.get("scenarios", []),
        "timelines": data["timelines"],
        "comparison": data["comparison"],
        "decision_tree": data.get("decision_tree", {}),
    }
    json_str = json.dumps(inline, ensure_ascii=False)
    return f"const INLINE_REPORT_DATA = {json_str};"


def find_and_replace_data(html, new_data_js):
    """通过括号计数精确定位 INLINE_REPORT_DATA 对象的起止位置"""
    marker = "const INLINE_REPORT_DATA = "
    start = html.find(marker)
    if start == -1:
        raise ValueError("未找到 INLINE_REPORT_DATA")

    # Skip past the marker to the opening brace
    brace_start = start + len(marker)
    if html[brace_start] != "{":
        raise ValueError("INLINE_REPORT_DATA 后面不是 {{")

    # Count brackets to find the matching closing brace
    depth = 0
    i = brace_start
    while i < len(html):
        c = html[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                old_str = html[start:end]
                return html[:start] + new_data_js + html[end:]
        elif c == '"':
            # Skip string literals to avoid counting braces inside strings
            i += 1
            while i < len(html):
                if html[i] == "\\":
                    i += 2
                    continue
                if html[i] == '"':
                    break
                i += 1
        i += 1

    raise ValueError("无法匹配 INLINE_REPORT_DATA 的括号")


def main():
    print(f"读取数据: {REPORT_DATA_PATH}")
    data = read_report_data()
    print(f"  版本: {data['meta'].get('version', '?')}")
    print(f"  原则: {len(data['principles'])} 条")
    total_items = sum(len(d["items"]) for d in data["checklist"])
    print(f"  清单: {len(data['checklist'])} 个维度, {total_items} 条")
    print(f"  Pokemon 时间轴: {len(data['timelines']['pokemon'])} 个节点")
    print(f"  Palworld 时间轴: {len(data['timelines']['palworld'])} 个节点")

    print(f"\n读取 HTML: {OUTPUT_HTML_PATH}")
    with open(OUTPUT_HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    new_data_js = generate_data_js(data)
    print(f"  生成新数据 JS: {len(new_data_js)} 字符 ({len(new_data_js) / 1024:.1f} KB)")

    new_html = find_and_replace_data(html, new_data_js)
    print(f"  生成新 HTML: {len(new_html) / 1024:.1f} KB")

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"\n已更新: {OUTPUT_HTML_PATH}")


if __name__ == "__main__":
    main()
