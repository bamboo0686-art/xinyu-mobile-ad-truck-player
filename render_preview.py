from pathlib import Path
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parent
scene=trimesh.load(ROOT/'assets/models/Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.glb', force='scene')

def color_for(name):
    n=name.upper()
    if n.startswith('LED_'):
        return '#111a24'
    if 'WINDOW' in n or 'WINDSHIELD' in n:
        return '#18384d'
    if 'WHEEL' in n:
        return '#111318'
    if 'HUB' in n or 'SILVER' in n or 'BUMPER' in n or 'STEP' in n or 'HANDLE' in n or 'HINGE' in n:
        return '#9aa3aa'
    if 'TAIL' in n:
        return '#d42c27'
    if 'INDICATOR' in n or 'SIGNAL' in n:
        return '#ee861a'
    if 'ACCENT' in n:
        return '#c99735'
    if 'CAB_' in n:
        return '#0862a7'
    if 'CARGO' in n or 'PANEL' in n or 'DOOR' in n or 'GENERATOR' in n:
        return '#082947'
    return '#26384a'

fig=plt.figure(figsize=(16,10), dpi=140)
ax=fig.add_subplot(111, projection='3d')
for name, geom in scene.geometry.items():
    T=scene.graph.get(name)[0]
    g=geom.copy(); g.apply_transform(T)
    if len(g.triangles):
        ax.add_collection3d(Poly3DCollection(g.triangles, facecolor=color_for(name), edgecolor='#090d12', linewidths=0.12, alpha=1.0))
xx, zz=np.meshgrid(np.linspace(-4.2,4.2,2),np.linspace(-3.2,3.2,2)); yy=np.zeros_like(xx)
ax.plot_surface(xx,yy,zz,color='#e7ebef',alpha=.7,shade=False)
ax.set_xlim(-3.8,3.8);ax.set_ylim(0,3.8);ax.set_zlim(-3,3)
ax.view_init(elev=22,azim=-42);ax.set_box_aspect((7.6,3.8,6.0));ax.set_axis_off()
fig.patch.set_facecolor('#f5f7f9');ax.set_facecolor('#f5f7f9')
plt.tight_layout(pad=0)
plt.savefig(ROOT/'assets/images/Xinyu_truck_preview_V2.png',bbox_inches='tight',pad_inches=.05)
