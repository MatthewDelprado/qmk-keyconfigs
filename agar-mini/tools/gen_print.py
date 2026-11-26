"""Draw a ZMK Studio dump as a printable keymap sheet: python3 gen_print.py NOW.json BACKUP.json OUT.html"""
import json,sys,html
from decode import usage
NOW,OLD,OUT=sys.argv[1:4]
SHORT={'Play/Pause':'⏯','Next':'⏭','Prev':'⏮','Mute(kb)':'Mute','Mute':'Mute'}
SYM={'LCtrl':'⌃','RCtrl':'⌃','LShift':'⇧','RShift':'⇧','LAlt':'⌥','RAlt':'⌥','LGui':'⌘','RGui':'⌘'}
UNSH={'1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')','-':'_','=':'+','[':'{',']':'}','\\':'|',';':':',"'":'"','`':'~',',':'<','.':'>','/':'?'}
def nice(v):
    mods=(v>>24)&0xff; base=usage(v&0xffffff)
    if base in SYM and base[1:] in('Ctrl','Shift','Alt','Gui'):
        mods|={'Ctrl':1,'Shift':2,'Alt':4,'Gui':8}[base[1:]]<<(4 if base[0]=='R' else 0); base=''
    if not mods: return SHORT.get(base,SYM.get(base,base))
    ms={m for i,m in enumerate(['Ctrl','Shift','Alt','Gui']) if (mods|mods>>4)>>i&1}
    if ms=={'Ctrl','Shift','Alt','Gui'} and not base: return 'Hyper'
    if ms=={'Shift'} and base in UNSH: return UNSH[base]
    return ''.join(SYM['L'+m] for m in ['Ctrl','Shift','Alt','Gui'] if m in ms)+base
def shifted(b,beh):
    """Shifted character for an unmodified number/symbol key (the tap side of a hold-tap too)."""
    n=beh.get(str(b['behaviorId']),{}).get('displayName','') or ''
    v=b.get('param1',0) if n=='Key Press' else b.get('param2',0) if n.startswith(('Mod-Tap','Layer-Tap')) else None
    if v is None or (v>>24)&0xff: return ''
    return UNSH.get(usage(v&0xffffff),'')
def label(b,beh,names):
    bid,p1,p2=b['behaviorId'],b.get('param1',0),b.get('param2',0)
    n=beh.get(str(bid),{}).get('displayName')
    if n is None: return ('','','fw')
    if n=='_Trans': return ('','','')
    if n=='Key(None)': return ('','','none')
    if n=='Key Press':
        t=nice(p1); return (t,'', 'mod' if t in '⌃⇧⌥⌘' else 'act' if len(t)>1 and t not in('⌘H',) else 'key')
    if n.startswith('Mod-Tap'): return (nice(p2),'hold '+nice(p1),'key')
    if n.startswith('Layer-Tap'): return (nice(p2),'hold '+names.get(p1,f'L{p1}'),'key')
    if n=='Layer Momentary': return (names.get(p1,f'L{p1}'),'hold','mod')
    if n.startswith('Device_'): return (n[7:].replace('BT','BT '),'device','act')
    return (n,'','act')
def board(d,lid,names,title,how,held=None):
    beh=d['behaviors']; lay=d['layouts']['layouts'][d['layouts'].get('activeLayoutIndex',0)]['keys']
    L=[l for l in d['keymap']['layers'] if l['id']==lid][0]['bindings']
    W=max(k['x']+k['width'] for k in lay); H=max(k.get('y',0)+k['height'] for k in lay)
    base=[l for l in d['keymap']['layers'] if l['id']==0][0]['bindings']
    keys=[]
    for k,b,b0 in zip(lay,L,base):
        m,s,t=label(b,beh,names)
        n0=beh.get(str(b0['behaviorId']),{}).get('displayName','')
        pos=len(keys)
        sh=shifted(b,beh)
        if held is not None:
            if pos in held: m,s,t=held[pos]+('held',); sh=''
        elif lid and t=='' and (n0.startswith('Layer') and b0.get('param1')==lid):
            m,s,t=(label(b0,beh,names)[0],'held','held')
        shtag=f'<em>{html.escape(sh)}</em>' if sh else ''
        keys.append(f'<div class="k {t}{" empty" if not m and t not in ("fw","none") else ""}" style="left:{k["x"]/W*100:.3f}%;top:{k.get("y",0)/H*100:.3f}%;width:{k["width"]/W*100:.3f}%;height:{k["height"]/H*100:.3f}%"><span>{shtag}<b{" class=sm" if len(m)>4 else ""}>{html.escape(m)}</b><i>{html.escape(s)}</i></span></div>')
    return f'<section><h3>{title}<small>{how}</small></h3><div class="kb" style="aspect-ratio:{W}/{H}">{"".join(keys)}</div></section>'
now=json.load(open(NOW)); old=json.load(open(OLD))
NN={1:'L1',2:'Nav',3:'Fn',4:'System'}
ON={1:'L1',2:'L2',3:'L3',4:'L4'}
p1=''.join(board(now,i,NN,t,h,hk) for i,t,h,hk in [(0,'Base','always on',None),(3,'Fn','hold the Fn key, or both Spaces',{36:('Fn','held')}),(2,'Nav','hold either Space (the other one taps Bksp, holds Fn)',{}),(4,'System','hold Fn + either Space',{36:('Fn','held'),39:('Space','either'),40:('Space','either')})])
p2=''.join(board(old,i,ON,f'Layer {i}','') for i in range(5))
open(OUT,'w').write(f'''<!doctype html><meta charset=utf-8><title>Agar Mini keymap</title><style>
@page{{size:letter landscape;margin:.4in}}
*{{box-sizing:border-box}}body{{font:11px -apple-system,"Helvetica Neue",sans-serif;color:#111;margin:0;background:#fff}}
.page{{page-break-after:always;break-after:page}}.page:last-child{{break-after:auto}}
header{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1.5px solid #111;padding-bottom:4px;margin-bottom:10px}}
header h1{{font-size:17px;margin:0}}header p{{margin:0;color:#555}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px 22px}}.grid.old{{grid-template-columns:1fr 1fr 1fr}}
h3{{font-size:13px;margin:0 0 4px}}h3 small{{font-weight:400;color:#666;margin-left:8px;font-size:10.5px}}
.kb{{position:relative;width:100%}}
.k{{position:absolute;padding:1.5px}}.k span{{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;border:1px solid #999;border-radius:4px;background:#fff;text-align:center;line-height:1.05;overflow:hidden}}
.k span{{position:relative}}.k em{{position:absolute;top:1.5px;left:3px;font-style:normal;font-size:8px;color:#666;line-height:1}}.old .k em{{font-size:6px;left:2px;top:1px}}.k b{{font-size:12px;font-weight:600}}.k i{{font-style:normal;font-size:7.5px;color:#555;margin-top:1px}}
.k.mod span{{background:#ececec}}.k.act span{{background:#e3edf9;border-color:#8fb0d8}}.k.fw span{{background:repeating-linear-gradient(45deg,#fff 0 3px,#eee 3px 6px);color:#888}}
.k b.sm{{font-size:9.5px}}.k.held span{{background:#222;color:#fff;border-color:#222}}.k.held i{{color:#ccc}}
/* none: does nothing */.k.none span{{background:#f6f6f6;border-color:#ddd}}.k.empty span{{border-style:dashed;border-color:#ccc;background:#fff}}
.old .k b{{font-size:9px}}.old .k i{{font-size:6px}}
footer{{margin-top:12px;color:#444;font-size:10px;line-height:1.45}}footer b{{color:#111}}
.legend{{display:flex;gap:12px;margin-top:6px}}.legend span{{display:inline-flex;align-items:center;gap:4px}}.legend i{{display:inline-block;width:14px;height:10px;border:1px solid #999;border-radius:2px}}
</style>
<div class="page"><header><h1>KBDfans Agar Mini BLE · master keymap</h1><p>ZMK Studio · written 2026-11-22</p></header>
<div class="grid">{p1}</div>
<footer><b>Small text</b> is the hold action; the corner legend is what Shift + that key types. Dashed keys pass through to the layer below. <b>/</b> is Fn + the key after P and <b>?</b> is Fn + comma. Del is Nav + Bksp, with = beside it. Both Shifts stay Shift on Nav. Hold either Space for Nav; while one Space is held, the other is Backspace on a tap and Fn on a hold (Fn is the higher layer, so it wins). Media is on Fn: Enter ⏯, Bksp ⏭, Right Shift Vol+, right ⌃ Vol−, right ⌘ Mute. Hold Fn + either Space for System: USB and Bluetooth 1–3. Brackets mirror under the index and middle fingers: [ ] on R U, {{ }} on D K, ( ) on F J. Striped keys were set in firmware, so ZMK Studio can't show or change them. (Since 2026-11-27 Nav is ZMK layer 2 and Fn layer 3, so Fn sits above Nav; layer 1 is no longer used.)
<div class="legend"><span><i style="background:#ececec"></i>modifier / layer</span><span><i style="background:#e3edf9;border-color:#8fb0d8"></i>action</span><span><i style="background:#222;border-color:#222"></i>held to reach this layer</span><span><i style="border-style:dashed"></i>pass-through</span><span><i style="background:#f6f6f6;border-color:#ddd"></i>does nothing</span><span><i style="background:repeating-linear-gradient(45deg,#fff 0 3px,#eee 3px 6px)"></i>firmware</span></div></footer></div>
<div class="page"><header><h1>Before: Agar Mini as it was</h1><p>Backup saved 2026-11-22 · agar-mini/backup/</p></header>
<div class="grid old">{p2}</div>
<footer>L1 was held from right Space, L3 from left Space, L4 from the → key. Layer numbers are ZMK layer ids. Striped keys came from firmware: Restore Stock Settings in ZMK Studio brings them back.</footer></div>''')
print('wrote',OUT)
