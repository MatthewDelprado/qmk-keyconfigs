"""Regenerates the Corne fixtures from corne-v4/tools/gen_print.py, the code that draws the printed keymaps.
Run from anywhere: python3 make_fixtures.py. The Swift tests check that the app agrees with it."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '../../../../..'))
TOOLS = os.path.join(REPO, 'corne-v4/tools')
READBACK = os.path.join(REPO, 'corne-v4/backup/corne-v4-vial-split-thumbs-2026-11-27.json')
src = open(os.path.join(TOOLS, 'gen_print.py')).read().split('FILL = {')[0]
sys.argv = ['gen_print.py', READBACK, os.devnull, 'split']
g = {'__file__': os.path.join(TOOLS, 'gen_print.py')}
exec(compile(src, 'gen_print', 'exec'), g)
km = g['km']
json.dump({
    'keys': [{'x': k[0], 'y': k[1], 'w': k[2], 'h': k[3], 'r': k[4], 'rx': k[5], 'ry': k[6], 'row': k[7][0], 'col': k[7][1]} for k in g['keys']],
    'keymap': km,
    'labels': [[[list(g['label'](v)[:3]) for v in row] for row in layer] for layer in km],
}, open(os.path.join(HERE, 'corne-v4.json'), 'w'), ensure_ascii=False, indent=0)
print('wrote corne-v4.json:', len(g['keys']), 'keys,', len(km), 'layers')
