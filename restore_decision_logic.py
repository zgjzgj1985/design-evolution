"""Restore the original decision_logic for A.1.1-A.1.8 from git, preserving all other content."""
import subprocess, re, json, os

# 1. Read current file
with open(r'D:\设计演化档案\docs\index.html', 'r', encoding='utf-8') as f:
    current_content = f.read()

# 2. Read original file from git
result = subprocess.run(
    ['git', 'show', 'HEAD:docs/index.html'],
    cwd=r'D:\设计演化档案',
    capture_output=True
)
orig_content = result.stdout.decode('utf-8', errors='replace')

# 3. Extract original decision_logic for A.1.1-A.1.8 from git version
def extract_json(content):
    """Extract and parse INLINE_REPORT_DATA JSON from content."""
    # Find the JSON start
    start = content.find('const INLINE_REPORT_DATA = ')
    if start == -1:
        return None
    start += len('const INLINE_REPORT_DATA = ')

    # Count braces to find the matching end
    brace_count = 0
    in_string = False
    escape_next = False
    json_end = -1

    for j in range(start, len(content)):
        c = content[j]
        if escape_next:
            escape_next = False
            continue
        if c == '\\':
            escape_next = True
            continue
        if c == '"' and not escape_next:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                json_end = j + 1
                break

    if json_end == -1:
        return None
    return content[start:json_end]

orig_json_str = extract_json(orig_content)
curr_json_str = extract_json(current_content)

if not orig_json_str or not curr_json_str:
    print('Could not extract JSON from one or both versions')
    exit(1)

print(f'Original JSON length: {len(orig_json_str)}')
print(f'Current JSON length: {len(curr_json_str)}')

orig_data = json.loads(orig_json_str)
curr_data = json.loads(curr_json_str)

# 4. Build a map of original decision_logic for，集火与保护 items
orig_dlogic = {}
for dim in orig_data['checklist']:
    if dim['dimension'] == '\u96c6\u706b\u4e0e\u4fdd\u62a4':
        for item in dim['items']:
            orig_dlogic[item['id']] = item.get('decision_logic', '')
        break

print(f'Found {len(orig_dlogic)} original decision_logic entries')

# 5. Replace decision_logic in current data for，集火与保护 items
replaced = 0
for dim in curr_data['checklist']:
    if dim['dimension'] == '\u96c6\u706b\u4e0e\u4fdd\u62a4':
        for item in dim['items']:
            item_id = item['id']
            if item_id in orig_dlogic:
                item['decision_logic'] = orig_dlogic[item_id]
                replaced += 1
                print(f'  Restored: {item_id}')
        break

print(f'Replaced {replaced} decision_logic entries')

# 6. Rebuild the file
new_json_str = json.dumps(curr_data, ensure_ascii=False, separators=(',', ':'))
new_content = current_content[:current_content.find('const INLINE_REPORT_DATA = ')] + 'const INLINE_REPORT_DATA = ' + new_json_str + ';' + current_content[current_content.find('const INLINE_REPORT_DATA = ') + len('const INLINE_REPORT_DATA = ') + len(curr_json_str) + 1:]

# Write back
with open(r'D:\设计演化档案\docs\index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done! Written to docs/index.html')

# Verify
with open(r'D:\设计演化档案\docs\index.html', 'r', encoding='utf-8') as f:
    verify = f.read()
idx = verify.find('\u96c6\u706b\u4e0e\u4fdd\u62a4')
chunk = verify[idx:idx+500]
print(f'Verify snippet: {chunk[:200]}')
