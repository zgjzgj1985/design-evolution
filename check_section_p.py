# -*- coding: utf-8 -*-
f = open(r'd:\vibe codeing\design-evolution\docs\index.html', 'r', encoding='utf-8')
c = f.read()
f.close()

# Find section-principles
idx = c.find('id="section-principles"')
if idx != -1:
    line = c[:idx].count('\n') + 1
    print("section-principles at line", line)
    print(repr(c[idx:idx+500]))
