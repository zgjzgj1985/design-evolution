with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = [
    'const CATEGORY_CLASS',
    'const SECTION_TITLES',
    'const DIM_ICONS',
    'const DIM_COLORS',
    'let reportData = null',
    'let checkedItems = {}',
    'let currentFilter',
    'let currentTimelineGame',
    'let selectedSearchIndex',
    'function init()',
    'function renderPrinciplesGrid',
    'function openPrincipleModal',
    'function renderTimeline',
    'function renderChecklist',
    'function renderDecisionTree',
    'function openSearch',
    'function navigateToTarget',
    'init()',
    '"decision_tree"',
    '"confidence"',
    '"counter_example"',
    '"boundary_condition"',
    '"producer_note"',
    '"decision_logic"',
    '"related_principles"',
    'v0.7.0-0.7.3',
    '"Gen 3"',
    '"Gen 5"',
    '"year": 2026',
    '"data_verified"',
    'vgc-disclaimer-acknowledged',
    'exportBtn',
    'searchInput',
    'timelineFilterBar',
    'decisionTreeGrid',
    'breadcrumbCurrent',
    'disclaimerOverlay',
]

ok = 0
missing = []
for name in checks:
    found = name in content
    if found:
        ok += 1
    else:
        missing.append(name)

print('Passed: ' + str(ok) + '/' + str(len(checks)))
if missing:
    print('MISSING:')
    for m in missing:
        print('  - ' + m)
else:
    print('All checks passed!')
print('HTML file size: ' + str(len(content)/1024) + ' KB')
