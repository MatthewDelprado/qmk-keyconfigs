import json,sys
K={0x04+i:chr(65+i) for i in range(26)}
K.update({0x1e+i:str((i+1)%10) for i in range(10)})
K.update({0x28:'Enter',0x29:'Esc',0x2a:'Bksp',0x2b:'Tab',0x2c:'Space',0x2d:'-',0x2e:'=',0x2f:'[',0x30:']',0x31:'\\',0x33:';',0x34:"'",0x35:'`',0x36:',',0x37:'.',0x38:'/',0x39:'Caps',
 0x46:'PrtSc',0x47:'ScrLk',0x48:'Pause',0x49:'Ins',0x4a:'Home',0x4b:'PgUp',0x4c:'Del',0x4d:'End',0x4e:'PgDn',0x4f:'→',0x50:'←',0x51:'↓',0x52:'↑',0x65:'Menu',0x7f:'Mute(kb)',
 0xe0:'LCtrl',0xe1:'LShift',0xe2:'LAlt',0xe3:'LGui',0xe4:'RCtrl',0xe5:'RShift',0xe6:'RAlt',0xe7:'RGui'})
K.update({0x3a+i:f'F{i+1}' for i in range(12)}); K.update({0x68+i:f'F{i+13}' for i in range(12)})
C={0xcd:'Play/Pause',0xb5:'Next',0xb6:'Prev',0xe9:'Vol+',0xea:'Vol−',0xe2:'Mute',0x6f:'Bright+',0x70:'Bright−',0xb7:'Stop'}
MODS=['Ctrl','Shift','Alt','Gui']
def usage(v):
    mods=(v>>24)&0xff; page=(v>>16)&0xff; uid=v&0xffff
    name=(K if page==7 else C if page==0x0c else {}).get(uid,f'p{page:x}:{uid:#x}')
    if mods:
        m=[('L' if i<4 else 'R')+MODS[i%4] for i in range(8) if mods>>i&1]
        name='+'.join(m)+'+'+name
    return name
def binding(b,beh):
    bid,p1,p2=b['behaviorId'],b.get('param1',0),b.get('param2',0)
    n=beh.get(str(bid),{}).get('displayName',f'UNKNOWN#{bid}')
    if n=='Key Press': return usage(p1)
    if n=='_Trans': return '▽'
    if n.startswith('Mod-Tap'): return f'{n}[hold {usage(p1)} / tap {usage(p2)}]'
    if n.startswith('Layer-Tap'): return f'{n}[hold L{p1} / tap {usage(p2)}]'
    if n in('Layer Momentary','Layer Toggle','Layer To'): return f'{n}(L{p1})'
    return f'{n}({p1},{p2})' if (p1 or p2) else n
if __name__=='__main__':
    d=json.load(open(sys.argv[1])); beh=d['behaviors']
    for l in d['keymap']['layers']:
        print(f"== layer index/id {l['id']} name={l['name']!r}")
        for i,b in enumerate(l['bindings']): print(f'  {i:2} {binding(b,beh)}')
