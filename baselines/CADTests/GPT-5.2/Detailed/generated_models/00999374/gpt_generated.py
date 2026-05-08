import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters from prompt ---
        pts = [
            (-0.215997, -0.071707),
            (0.283196/2 - 0.086266, -0.571139/2 + 0.128415),
            (0.283196/2 + 0.154673, 0.571139/2 - 0.103869),
            (0.283196/3 - 0.094331, 0.571139 - 0.45031),
        ]
        body_h = 0.493701
    
        prism_x = 0.1323
        prism_y = 0.78659
        prism_z = 0.203642
        rot_deg = -41.7
        target_translation = (0.223543, -0.361526, 0.301748)
    
        # --- Main body: irregular rhombus extruded ---
        body = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(body_h)
        )
    
        # --- Choose a vertical side edge and compute its midpoint (for "attach to edge center") ---
        # Get all vertical edges (parallel to Z). Pick the longest one.
        solid = body.val()
        vert_edges = [e for e in solid.Edges() if e.tangentAt(0).Length < 1e-9 or abs(e.tangentAt(0).z) > 0.999]  # fallback
        # More robust: use bounding box of each edge to detect verticality
        vert_edges = []
        for e in solid.Edges():
            bb = e.BoundingBox()
            dx, dy, dz = (bb.xlen, bb.ylen, bb.zlen)
            if dz > 0.9 * body_h and dx < 1e-6 and dy < 1e-6:
                vert_edges.append(e)
    
        if not vert_edges:
            # If detection fails, just use all edges and pick the one with largest z-span
            edges = list(solid.Edges())
            vert_edges = sorted(edges, key=lambda ed: ed.BoundingBox().zlen, reverse=True)[:1]
    
        # Pick the longest vertical edge by length
        edge = max(vert_edges, key=lambda ed: ed.Length())
        mid = edge.Center()  # midpoint-ish for straight edge; for safety use Center()
    
        # --- Prism: create centered box, then attach its center to the edge midpoint ---
        prism = cq.Workplane("XY").box(prism_x, prism_y, prism_z, centered=True)
    
        # Move prism so its center is at the selected edge midpoint
        prism = prism.translate((mid.x, mid.y, mid.z))
    
        # Apply requested rotation about global Z (around origin), then translate to requested position.
        # To keep the "attached" intent, we treat the requested translation as an additional offset.
        prism = prism.rotate((0, 0, 0), (0, 0, 1), rot_deg).translate(target_translation)
    
        # --- Union to complete model ---
        result = body.union(prism)
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00999374/gpt_generated.stl')
