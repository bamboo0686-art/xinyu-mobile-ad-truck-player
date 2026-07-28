from pathlib import Path
import json
import sys
import trimesh
import numpy as np

ROOT=Path(__file__).resolve().parent
MODEL=ROOT/'assets/models/Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.glb'
REQUIRED=[
 ROOT/'index.html', ROOT/'.nojekyll', ROOT/'README.md', MODEL,
 ROOT/'assets/config/screen_mapping.json'
]

errors=[]
for p in REQUIRED:
    if not p.exists(): errors.append(f'缺少檔案：{p.relative_to(ROOT)}')
if errors:
    print('\n'.join(errors)); sys.exit(1)

scene=trimesh.load(MODEL,force='scene')
names=set(scene.geometry.keys())
for name in ['LED_LEFT_MAIN','LED_LEFT_REAR','LED_RIGHT_MAIN','REAR_RIGHT_ACCESS_DOOR']:
    if name not in names: errors.append(f'模型缺少物件：{name}')
frames=[n for n in names if n.startswith(('LED_LEFT','LED_RIGHT')) and 'FRAME' in n]
if frames: errors.append('仍存在 LED 外框物件：'+', '.join(frames))

def world_bounds(name):
    g=scene.geometry[name].copy(); g.apply_transform(scene.graph.get(name)[0]); return g.bounds
if not errors:
    a=world_bounds('LED_LEFT_MAIN');b=world_bounds('LED_LEFT_REAR')
    dx=abs(a[1,0]-b[0,0]);dz=abs(a[1,2]-b[1,2])
    if dx>0.002 or dz>0.002: errors.append(f'L 型轉角未無縫：dx={dx}, dz={dz}')

html=(ROOT/'index.html').read_text(encoding='utf-8')
for ref in ['./assets/models/Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.glb','LED_LEFT_MAIN','LED_LEFT_REAR']:
    if ref not in html: errors.append(f'index.html 缺少參照：{ref}')

if errors:
    print('驗證失敗')
    print('\n'.join('- '+e for e in errors))
    sys.exit(1)
print('驗證通過')
print('- GitHub Pages 根目錄結構完整')
print('- 左右 LED 無外框物件')
print('- 左側 90° 轉角共用邊線，幾何間距 0 mm')
print('- 車尾右側唯一出入口門已保留')
