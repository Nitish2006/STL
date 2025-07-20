import cv2
import numpy as np
import trimesh
import re

def image_to_heightmap(image_path, max_height=5.0):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found or invalid")
    img = cv2.resize(img, (512, 512))
    heightmap = (img / 255.0) * max_height
    return heightmap

def heightmap_to_mesh(heightmap, width=10.0, height=10.0):
    h, w = heightmap.shape
    vertices = []
    for i in range(h):
        for j in range(w):
            x = (j / w) * width
            y = (i / h) * height
            z = heightmap[i, j]
            vertices.append([x, y, z])
    vertices = np.array(vertices)

    faces = []
    for i in range(h-1):
        for j in range(w-1):
            v0 = i * w + j
            v1 = v0 + 1
            v2 = (i + 1) * w + j
            v3 = v2 + 1
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
    faces = np.array(faces)

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    return mesh

def parse_text_prompt(prompt):
    extrusion_height = 5.0
    add_base = False
    match = re.search(r"extrude\s+(\d+)mm", prompt, re.IGNORECASE)
    if match:
        extrusion_height = float(match.group(1))
    if "base" in prompt.lower():
        add_base = True
    return {"extrusion_height": extrusion_height, "add_base": add_base}

def apply_text_modifiers(mesh, params):
    if params["add_base"]:
        base = trimesh.creation.box(extents=[10, 10, 1])
        mesh = trimesh.util.concatenate([mesh, base])
    mesh.apply_scale([1, 1, params["extrusion_height"]/5.0])
    return mesh

def check_printability(mesh):
    if not mesh.is_watertight:
        mesh.fill_holes()
        mesh.fix_normals()
    return mesh

def convert_to_stl(image_path, prompt, output_path="static/output.stl"):
    heightmap = image_to_heightmap(image_path)
    mesh = heightmap_to_mesh(heightmap)
    params = parse_text_prompt(prompt)
    mesh = apply_text_modifiers(mesh, params)
    mesh = check_printability(mesh)
    mesh.export(output_path)
    return output_path