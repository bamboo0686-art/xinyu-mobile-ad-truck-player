import json
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent

# Coordinate system for the authored model:
# X = vehicle length (front negative, rear positive)
# Y = up
# Z = vehicle width (left positive, right negative)


def mat(name, rgba, metallic=0.0, roughness=0.65, emissive=None):
    kwargs = {
        'name': name,
        'baseColorFactor': list(rgba),
        'metallicFactor': metallic,
        'roughnessFactor': roughness,
    }
    if emissive is not None:
        kwargs['emissiveFactor'] = list(emissive)
    return trimesh.visual.material.PBRMaterial(**kwargs)


MATS = {
    'blue': mat('XINYU_BLUE', (0.025, 0.22, 0.46, 1.0), metallic=0.15, roughness=0.42),
    'blue_dark': mat('XINYU_BLUE_DARK', (0.012, 0.075, 0.14, 1.0), metallic=0.2, roughness=0.38),
    'black': mat('STRUCTURE_BLACK', (0.015, 0.018, 0.022, 1.0), metallic=0.15, roughness=0.54),
    'screen': mat('LED_SCREEN_OFF', (0.012, 0.018, 0.025, 1.0), metallic=0.0, roughness=0.28, emissive=(0.02, 0.025, 0.035)),
    'glass': mat('DARK_GLASS', (0.025, 0.06, 0.09, 0.82), metallic=0.0, roughness=0.14),
    'silver': mat('METAL_SILVER', (0.52, 0.56, 0.60, 1.0), metallic=0.75, roughness=0.28),
    'tire': mat('TIRE_RUBBER', (0.012, 0.012, 0.014, 1.0), metallic=0.0, roughness=0.88),
    'light_white': mat('LIGHT_WHITE', (0.86, 0.90, 0.94, 1.0), metallic=0.0, roughness=0.22, emissive=(0.55, 0.58, 0.62)),
    'light_red': mat('LIGHT_RED', (0.62, 0.015, 0.012, 1.0), metallic=0.0, roughness=0.25, emissive=(0.7, 0.015, 0.01)),
    'light_orange': mat('LIGHT_ORANGE', (0.95, 0.24, 0.015, 1.0), metallic=0.0, roughness=0.22, emissive=(0.72, 0.13, 0.005)),
    'gold': mat('ACCENT_GOLD', (0.72, 0.48, 0.09, 1.0), metallic=0.7, roughness=0.25),
}


def add(scene, mesh, name, material=None):
    if material is not None:
        mesh.visual = trimesh.visual.TextureVisuals(material=material)
    scene.add_geometry(mesh, geom_name=name, node_name=name)
    return mesh


def box(scene, name, extents, center, material, transform=None):
    mesh = trimesh.creation.box(extents=extents)
    if transform is not None:
        mesh.apply_transform(transform)
    mesh.apply_translation(center)
    return add(scene, mesh, name, material)


def cyl(scene, name, radius, length, center, material, sections=32, axis='z'):
    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    # default cylinder axis is Z; rotate when another axis is requested
    if axis == 'x':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == 'y':
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    mesh.apply_translation(center)
    return add(scene, mesh, name, material)


def quad_mesh(vertices, normal_outward='auto'):
    vertices = np.asarray(vertices, dtype=float)
    # triangles 0-1-2 and 0-2-3
    faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)
    uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False, visual=trimesh.visual.TextureVisuals(uv=uv))


def screen_quad(scene, name, vertices):
    mesh = quad_mesh(vertices)
    mesh.visual.material = MATS['screen']
    return add(scene, mesh, name)


def frame_bars_side(scene, prefix, x_center, z, width_x, height_y, y_center, facing='left'):
    thickness = 0.045
    depth = 0.055
    # horizontal top/bottom
    box(scene, f'{prefix}_FRAME_TOP', (width_x + 0.10, thickness, depth), (x_center, y_center + height_y/2 + thickness/2, z), MATS['black'])
    box(scene, f'{prefix}_FRAME_BOTTOM', (width_x + 0.10, thickness, depth), (x_center, y_center - height_y/2 - thickness/2, z), MATS['black'])
    # vertical front/rear
    box(scene, f'{prefix}_FRAME_FRONT', (thickness, height_y + 0.10, depth), (x_center - width_x/2 - thickness/2, y_center, z), MATS['black'])
    box(scene, f'{prefix}_FRAME_REAR', (thickness, height_y + 0.10, depth), (x_center + width_x/2 + thickness/2, y_center, z), MATS['black'])


def frame_bars_rear(scene, prefix, x, z_center, width_z, height_y, y_center):
    thickness = 0.045
    depth = 0.055
    box(scene, f'{prefix}_FRAME_TOP', (depth, thickness, width_z + 0.10), (x, y_center + height_y/2 + thickness/2, z_center), MATS['black'])
    box(scene, f'{prefix}_FRAME_BOTTOM', (depth, thickness, width_z + 0.10), (x, y_center - height_y/2 - thickness/2, z_center), MATS['black'])
    box(scene, f'{prefix}_FRAME_LEFT', (depth, height_y + 0.10, thickness), (x, y_center, z_center + width_z/2 + thickness/2), MATS['black'])
    box(scene, f'{prefix}_FRAME_RIGHT', (depth, height_y + 0.10, thickness), (x, y_center, z_center - width_z/2 - thickness/2), MATS['black'])


def wedge_cab(scene):
    # Low-poly cab upper shell with slightly sloped windshield/roof.
    x0, x1 = -2.95, -1.18
    y0, y1 = 1.28, 2.50
    z0, z1 = -0.93, 0.93
    # front top is pulled rearward for a subtle cab-over slope
    verts = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0+0.20, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0+0.20, y1, z1],
    ])
    faces = np.array([
        [0,1,2],[0,2,3],
        [4,7,6],[4,6,5],
        [0,4,5],[0,5,1],
        [3,2,6],[3,6,7],
        [0,3,7],[0,7,4],
        [1,5,6],[1,6,2],
    ])
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)
    add(scene, mesh, 'CAB_UPPER_SHELL', MATS['blue'])


def build_scene():
    scene = trimesh.Scene()

    # Main dimensions (meters), tuned to the actual blue 2.1t advertising truck references.
    overall_width = 2.05
    cargo_front = -1.05
    cargo_rear = 2.98
    cargo_center = (cargo_front + cargo_rear) / 2
    cargo_len = cargo_rear - cargo_front
    cargo_bottom = 0.82
    cargo_top = 3.08
    cargo_height = cargo_top - cargo_bottom

    # Chassis & bumpers
    box(scene, 'CHASSIS_MAIN', (5.75, 0.22, 1.62), (-0.10, 0.62, 0), MATS['black'])
    box(scene, 'FRONT_BUMPER', (0.20, 0.24, 1.88), (-3.03, 0.58, 0), MATS['black'])
    box(scene, 'REAR_BUMPER', (0.18, 0.23, 1.92), (3.07, 0.56, 0), MATS['silver'])

    # Cargo body / LED cabinet shell
    box(scene, 'CARGO_BODY', (cargo_len, cargo_height, overall_width), (cargo_center, (cargo_bottom+cargo_top)/2, 0), MATS['blue_dark'])
    box(scene, 'CARGO_ROOF_CAP', (cargo_len + 0.08, 0.09, overall_width + 0.08), (cargo_center, cargo_top + 0.045, 0), MATS['black'])
    box(scene, 'CARGO_LOWER_RAIL', (cargo_len + 0.08, 0.10, overall_width + 0.08), (cargo_center, cargo_bottom + 0.05, 0), MATS['black'])

    # Cab
    box(scene, 'CAB_LOWER_BODY', (1.95, 0.72, 1.90), (-2.05, 0.95, 0), MATS['blue'])
    wedge_cab(scene)
    box(scene, 'CAB_FRONT_GRILLE', (0.035, 0.50, 1.05), (-2.966, 0.95, 0), MATS['silver'])
    box(scene, 'CAB_FRONT_WINDSHIELD', (0.025, 0.68, 1.56), (-2.765, 2.06, 0), MATS['glass'])
    # side windows and doors
    box(scene, 'CAB_LEFT_WINDOW', (0.72, 0.58, 0.026), (-2.16, 2.04, 0.944), MATS['glass'])
    box(scene, 'CAB_RIGHT_WINDOW', (0.72, 0.58, 0.026), (-2.16, 2.04, -0.944), MATS['glass'])
    box(scene, 'CAB_LEFT_DOOR_PANEL', (0.76, 0.72, 0.028), (-2.10, 1.30, 0.956), MATS['blue_dark'])
    box(scene, 'CAB_RIGHT_DOOR_PANEL', (0.76, 0.72, 0.028), (-2.10, 1.30, -0.956), MATS['blue_dark'])
    # mirrors
    box(scene, 'MIRROR_LEFT_ARM', (0.16, 0.04, 0.20), (-2.72, 2.02, 1.04), MATS['black'])
    box(scene, 'MIRROR_RIGHT_ARM', (0.16, 0.04, 0.20), (-2.72, 2.02, -1.04), MATS['black'])
    box(scene, 'MIRROR_LEFT', (0.08, 0.27, 0.18), (-2.79, 2.02, 1.16), MATS['black'])
    box(scene, 'MIRROR_RIGHT', (0.08, 0.27, 0.18), (-2.79, 2.02, -1.16), MATS['black'])
    # roof fairing / front header panel visible above cab
    box(scene, 'FRONT_HEADER_STRUCTURE', (0.16, 0.72, 1.88), (-1.12, 2.67, 0), MATS['black'])
    screen_quad(scene, 'LED_FRONT_HEADER', [
        [-1.205, 2.33, -0.84], [-1.205, 2.33, 0.84], [-1.205, 2.97, 0.84], [-1.205, 2.97, -0.84]
    ])

    # Headlights / indicators
    for z in (-0.67, 0.67):
        box(scene, f'HEADLIGHT_{"R" if z < 0 else "L"}', (0.04, 0.20, 0.30), (-3.035, 1.10, z), MATS['light_white'])
        box(scene, f'INDICATOR_{"R" if z < 0 else "L"}', (0.045, 0.11, 0.18), (-3.04, 0.87, z), MATS['light_orange'])

    # Wheels (front and rear axle)
    for axle, x in [('FRONT', -2.08), ('REAR', 1.92)]:
        for side, z in [('LEFT', 1.035), ('RIGHT', -1.035)]:
            cyl(scene, f'WHEEL_{axle}_{side}', 0.43, 0.23, (x, 0.47, z), MATS['tire'], sections=40, axis='z')
            cyl(scene, f'HUB_{axle}_{side}', 0.18, 0.245, (x, 0.47, z), MATS['silver'], sections=32, axis='z')

    # Wheel arches / fenders (simple dark blue rails)
    for x in (-2.08, 1.92):
        box(scene, f'FENDER_LEFT_{x}', (0.95, 0.10, 0.12), (x, 0.91, 0.98), MATS['blue_dark'])
        box(scene, f'FENDER_RIGHT_{x}', (0.95, 0.10, 0.12), (x, 0.91, -0.98), MATS['blue_dark'])

    # LED screens — independent named meshes for video texture assignment.
    led_yc = 2.01
    led_h = 1.44

    # FULL-BLEED LED screens: no visible top, bottom, side or corner frame bars.
    # The left side and rear-left planes share the exact same 90-degree corner line,
    # so the L-shaped display has zero geometric gap at the joint.
    surface_offset = 0.014
    rear_x = cargo_rear + surface_offset
    left_z = overall_width/2 + surface_offset

    # Left side main screen: 3.69m x 1.44m, extending exactly to the rear corner.
    left_w = 3.69
    left_x_max = rear_x
    left_x_min = left_x_max - left_w
    left_xc = (left_x_min + left_x_max) / 2
    screen_quad(scene, 'LED_LEFT_MAIN', [
        [left_x_min, led_yc-led_h/2, left_z],
        [left_x_max, led_yc-led_h/2, left_z],
        [left_x_max, led_yc+led_h/2, left_z],
        [left_x_min, led_yc+led_h/2, left_z],
    ])

    # Rear-left screen forms the seamless 90-degree L wrap.
    # Its outer-left edge is exactly the same line as LED_LEFT_MAIN's rear edge.
    rear_screen_w = 1.12
    rear_z_max = left_z
    rear_z_min = rear_z_max - rear_screen_w
    rear_screen_zc = (rear_z_min + rear_z_max) / 2
    screen_quad(scene, 'LED_LEFT_REAR', [
        [rear_x, led_yc-led_h/2, rear_z_max],
        [rear_x, led_yc-led_h/2, rear_z_min],
        [rear_x, led_yc+led_h/2, rear_z_min],
        [rear_x, led_yc+led_h/2, rear_z_max],
    ])

    # Right side flat screen: 2.52m x 1.44m, also full-bleed with no frame bars.
    right_w = 2.52
    right_xc = cargo_front + 0.15 + right_w/2
    right_z = -overall_width/2 - surface_offset
    # reverse vertex order so the outward face is correctly oriented
    screen_quad(scene, 'LED_RIGHT_MAIN', [
        [right_xc+right_w/2, led_yc-led_h/2, right_z],
        [right_xc-right_w/2, led_yc-led_h/2, right_z],
        [right_xc-right_w/2, led_yc+led_h/2, right_z],
        [right_xc+right_w/2, led_yc+led_h/2, right_z],
    ])

    # Right-side rear equipment/service panel (not a door).
    equip_x0 = right_xc + right_w/2 + 0.10
    equip_w = cargo_rear - equip_x0 - 0.08
    if equip_w > 0.15:
        box(scene, 'RIGHT_REAR_SERVICE_PANEL', (equip_w, 1.65, 0.035), (equip_x0+equip_w/2, 1.96, right_z+0.006), MATS['blue_dark'])
        # ventilation slats
        for i in range(5):
            box(scene, f'RIGHT_SERVICE_VENT_{i+1}', (equip_w*0.64, 0.035, 0.018), (equip_x0+equip_w/2, 1.60+i*0.12, right_z-0.02), MATS['silver'])

    # Unique rear-right access door, full-height aligned with screen zone.
    door_w = 0.80
    door_h = 2.03
    door_zc = -overall_width/2 + door_w/2 + 0.08
    door_yc = cargo_bottom + door_h/2 + 0.08
    box(scene, 'REAR_RIGHT_ACCESS_DOOR', (0.035, door_h, door_w), (cargo_rear+0.022, door_yc, door_zc), MATS['blue_dark'])
    # door frame
    door_x = cargo_rear + 0.055
    dt = 0.04
    box(scene, 'REAR_DOOR_FRAME_TOP', (0.055, dt, door_w+0.08), (door_x, door_yc+door_h/2+dt/2, door_zc), MATS['silver'])
    box(scene, 'REAR_DOOR_FRAME_BOTTOM', (0.055, dt, door_w+0.08), (door_x, door_yc-door_h/2-dt/2, door_zc), MATS['silver'])
    box(scene, 'REAR_DOOR_FRAME_LEFT', (0.055, door_h+0.08, dt), (door_x, door_yc, door_zc+door_w/2+dt/2), MATS['silver'])
    box(scene, 'REAR_DOOR_FRAME_RIGHT', (0.055, door_h+0.08, dt), (door_x, door_yc, door_zc-door_w/2-dt/2), MATS['silver'])
    box(scene, 'REAR_DOOR_HANDLE', (0.07, 0.18, 0.035), (cargo_rear+0.095, door_yc, door_zc-0.23), MATS['silver'])
    # hinges
    for yy in (door_yc-0.65, door_yc, door_yc+0.65):
        box(scene, f'REAR_DOOR_HINGE_{yy:.2f}', (0.07, 0.12, 0.035), (cargo_rear+0.095, yy, door_zc+0.35), MATS['silver'])

    # Rear lights / plate holder
    for z in (-0.76, 0.76):
        box(scene, f'REAR_TAIL_{"R" if z < 0 else "L"}', (0.05, 0.20, 0.24), (3.115, 0.75, z), MATS['light_red'])
        box(scene, f'REAR_SIGNAL_{"R" if z < 0 else "L"}', (0.055, 0.10, 0.24), (3.12, 0.94, z), MATS['light_orange'])
    box(scene, 'REAR_PLATE_HOLDER', (0.06, 0.18, 0.52), (3.125, 0.69, 0), MATS['black'])

    # Steps and underbody equipment
    box(scene, 'CAB_LEFT_STEP', (0.62, 0.12, 0.22), (-1.92, 0.62, 1.03), MATS['silver'])
    box(scene, 'CAB_RIGHT_STEP', (0.62, 0.12, 0.22), (-1.92, 0.62, -1.03), MATS['silver'])
    box(scene, 'GENERATOR_BOX', (0.94, 0.55, 0.58), (0.74, 0.52, -0.70), MATS['blue_dark'])
    box(scene, 'FUEL_BOX', (0.70, 0.42, 0.48), (0.48, 0.51, 0.76), MATS['silver'])

    # Gold marker line / brand accent (logo intentionally omitted; official logo should be composited separately)
    box(scene, 'BRAND_ACCENT_LEFT', (0.96, 0.035, 0.018), (-2.08, 1.16, 0.973), MATS['gold'])
    box(scene, 'BRAND_ACCENT_RIGHT', (0.96, 0.035, 0.018), (-2.08, 1.16, -0.973), MATS['gold'])

    # Metadata for downstream player integrations.
    scene.metadata.update({
        'asset_name': 'Xinyu_2.1t_LED_Mobile_Advertising_Truck',
        'company': '心禹國際開發科技有限公司',
        'units': 'meters',
        'up_axis': 'Y',
        'screen_meshes': {
            'left_main': 'LED_LEFT_MAIN',
            'left_rear': 'LED_LEFT_REAR',
            'right_main': 'LED_RIGHT_MAIN',
            'front_header': 'LED_FRONT_HEADER',
        },
        'critical_structure': 'Only one cargo access door: rear-right side.',
        'screen_finish': 'Full-bleed frameless LED surfaces; seamless 90-degree left wrap.',
    })
    return scene


def create_placeholder(path: Path, title: str, subtitle: str, size=(1536, 1024)):
    img = Image.new('RGB', size, (5, 14, 28))
    d = ImageDraw.Draw(img)
    # tech grid
    for x in range(0, size[0], 64):
        d.line((x, 0, x, size[1]), fill=(12, 35, 61), width=1)
    for y in range(0, size[1], 64):
        d.line((0, y, size[0], y), fill=(12, 35, 61), width=1)
    # glow bands
    d.rectangle((0, int(size[1]*0.74), size[0], size[1]), fill=(4, 45, 82))
    d.rectangle((0, 0, size[0], 18), fill=(187, 132, 35))
    try:
        font_big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 92)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 42)
    except Exception:
        font_big = None
        font_small = None
    # Chinese may not render with DejaVu; use English-safe title in texture.
    d.text((90, 280), title, fill=(235, 197, 102), font=font_big)
    d.text((94, 410), subtitle, fill=(235, 240, 246), font=font_small)
    d.text((94, 800), 'VIDEO TEXTURE PLACEHOLDER', fill=(135, 180, 218), font=font_small)
    img.save(path, quality=95)


def main():
    scene = build_scene()
    glb_path = OUT / 'assets/models/Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.glb'
    glb_path.write_bytes(scene.export(file_type='glb'))

    # Compatibility OBJ (video surfaces remain identifiable by object/group name in most DCC tools).
    obj_export = scene.export(file_type='obj', include_texture=False)
    if isinstance(obj_export, dict):
        for filename, data in obj_export.items():
            p = OUT / filename
            if isinstance(data, str):
                p.write_text(data, encoding='utf-8')
            else:
                p.write_bytes(data)
    else:
        (OUT / 'assets/models/Xinyu_2.1t_LED_Mobile_Ad_Truck_V2.obj').write_text(obj_export, encoding='utf-8')

    config = {
        'model': glb_path.name,
        'coordinate_system': {'up': 'Y', 'units': 'meters'},
        'screens': [
            {'mesh': 'LED_LEFT_MAIN', 'role': 'left_main', 'physical_size_m': [3.69, 1.44], 'recommended_video': '1536x600 or proportional 2.5625:1'},
            {'mesh': 'LED_LEFT_REAR', 'role': 'left_rear_L_wrap', 'physical_size_m': [1.12, 1.44], 'recommended_video': 'same source crop or dedicated vertical crop'},
            {'mesh': 'LED_RIGHT_MAIN', 'role': 'right_main', 'physical_size_m': [2.52, 1.44], 'recommended_video': '1536x878 or proportional 1.75:1'},
            {'mesh': 'LED_FRONT_HEADER', 'role': 'front_header_optional', 'physical_size_m': [1.68, 0.64], 'recommended_video': 'wide logo/static content'},
        ],
        'non_negotiable': {
            'rear_right_door_mesh': 'REAR_RIGHT_ACCESS_DOOR',
            'note': 'The rear-right cargo access door is the only door on the LED cargo box.'
        },
        'runtime_notes': [
            'Apply THREE.VideoTexture to each named screen mesh material.',
            'Set texture.flipY = false for glTF UV orientation.',
            'Use MeshBasicMaterial or emissive material for an LED-like display.',
            'For L-wrap synchronized content, use one HTMLVideoElement and split the texture horizontally across LED_LEFT_MAIN and LED_LEFT_REAR.'
        ]
    }
    (OUT / 'assets/config/screen_mapping.json').write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')

    create_placeholder(OUT / 'assets/images/left_screen_placeholder.jpg', 'XINYU MOBILE MEDIA', 'LEFT L-SHAPED LED DISPLAY')
    create_placeholder(OUT / 'assets/images/right_screen_placeholder.jpg', 'XINYU MOBILE MEDIA', 'RIGHT FLAT LED DISPLAY')

    print(glb_path)
    print('bounds', scene.bounds)
    print('geometry_count', len(scene.geometry))


if __name__ == '__main__':
    main()
