import subprocess, re, json, sys

result = subprocess.run(
    ['git', 'show', 'HEAD:docs/index.html'],
    cwd=r'D:\设计演化档案',
    capture_output=True
)
content = result.stdout.decode('utf-8', errors='replace')

# Find the INLINE_REPORT_DATA JSON - need to handle nested JS object
# Find start and match braces carefully
start = content.find('const INLINE_REPORT_DATA = {')
if start == -1:
    print('INLINE_REPORT_DATA not found')
    sys.exit(1)

# Count braces to find the matching end
brace_count = 0
in_string = False
escape_next = False
i = start + len('const INLINE_REPORT_DATA = ')
json_end = -1

for j in range(i, len(content)):
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
    print('Could not find end of JSON')
    sys.exit(1)

json_str = content[start + len('const INLINE_REPORT_DATA = '):json_end]

data = json.loads(json_str)
checklist = data['checklist']

# Find，集火与保护
for dim in checklist:
    if dim['dimension'] == '\u96c6\u706b\u4e0e\u4fdd\u62a4':
        with open(r'D:\设计演化档案\orig_decision_logic.txt', 'w', encoding='utf-8') as f:
            for item in dim['items']:
                fid = item['id']
                dlogic = item.get('decision_logic', 'N/A')
                f.write(f'=== {fid} ===\n')
                f.write(dlogic)
                f.write('\n\n')
        print('Written to orig_decision_logic.txt')
        break
