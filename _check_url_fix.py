import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:\设计演化档案\app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Check indentation of st.markdown for 原文链接
print('Line 1140:', repr(lines[1139][:80]))
print('Line 1141:', repr(lines[1140][:80]))
print('Line 1142:', repr(lines[1141][:80]))

# The issue: line 1142 is at 16-space indent but should be at 16-space WITHOUT the else:
# Fix: the '                    else:' (16 spaces) at line 1141 closes the 'if llm_ready' block
# and the st.markdown for URL should NOT be inside it
# We need: 1) closing '                ' of the AI analysis section, then '                if patch.get("url"):'
# Current: it's inside the else block of if llm_ready

# Let's fix it by adding proper structure
# Lines 1139-1142 need to be:
# '                    else:'
# '                        st.warning("请先在侧边栏配置 LLM API Key...")'
# '                ' (end of AI section)
# '                if patch.get("url"):'
# '                    st.markdown(...)'
# '

print('\nBefore fix, lines 1139-1144:')
for i in range(1138, 1144):
    print(f'Line {i+1} (idx {i}): {repr(lines[i])}')
