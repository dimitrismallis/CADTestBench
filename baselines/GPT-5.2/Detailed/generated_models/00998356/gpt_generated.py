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
        # --- Parameters (units as given) ---
        base = 1.19143
        tri_h = 0.85714
        thickness = 0.085714
    
        # Bottom corner rounding: interpret "outer diameter" as fillet diameter
        fillet_r = 0.214604 / 2.0  # 0.107302
    
        hole_d = 0.094286
        hole_r = hole_d / 2.0
    
        # Top truncation: flat edge slightly below apex (prompt: "near the top")
        top_flat_y = tri_h - 0.06
        top_flat_y = max(0.0, min(top_flat_y, tri_h - 1e-3))
    
        # Hole placement offsets from each corner (heuristic, kept inside boundary)
        corner_offset = 0.12
    
        # Extra cuts
        top_rect_cut_depth = thickness + 0.5
        top_rect_w = base * 0.35
        top_rect_h = 0.06
    
        base_center_hole_d = 0.12
        base_center_hole_depth = thickness + 0.5
    
        # --- Geometry helpers ---
        half_base = base / 2.0
    
        # Triangle vertices (base on y=0, apex at y=tri_h)
        pL = (-half_base, 0.0)
        pR = ( half_base, 0.0)
        pT = (0.0, tri_h)
    
        # Compute intersection of the two sides with horizontal line y=top_flat_y
        # Left side from pL to pT: x(y) = -half_base + (half_base/tri_h)*y
        # Right side from pR to pT: x(y) =  half_base - (half_base/tri_h)*y
        x_at_flat = half_base * (1.0 - top_flat_y / tri_h)
        pTL = (-x_at_flat, top_flat_y)
        pTR = ( x_at_flat, top_flat_y)
    
        # --- Build 2D face using Sketch API (supports 2D vertex fillet) ---
        # Polygon order: pL -> pR -> pTR -> pTL
        sk = (
            cq.Sketch()
            .polygon([pL, pR, pTR, pTL])
            .vertices()  # select all vertices, then filter to bottom ones by Y
        )
    
        # Sketch selectors are limited; easiest: fillet bottom corners by tagging points via proximity.
        # We'll fillet all vertices except the two top-flat vertices by using two passes:
        # 1) fillet all vertices with a small radius, then "unfillet" isn't possible.
        # So instead: fillet only the two bottom corners by selecting them via nearest-to-point.
        sk = sk.reset()
        sk = sk.vertices(cq.selectors.NearestToPointSelector(pL)).fillet(fillet_r)
        sk = sk.reset()
        sk = sk.vertices(cq.selectors.NearestToPointSelector(pR)).fillet(fillet_r)
    
        # Add three corner holes (subtract circles)
        hole_pts = [
            (pL[0] + corner_offset, pL[1] + corner_offset * 0.35),
            (pR[0] - corner_offset, pR[1] + corner_offset * 0.35),
            (0.0, top_flat_y - corner_offset * 0.45),
        ]
        sk = sk.reset().push(hole_pts).circle(hole_r, mode="s")
    
        # Extrude to 3D
        solid = cq.Workplane("XY").placeSketch(sk).extrude(thickness)
    
        # --- Rectangular cut from the top flat edge ---
        # Cut a small rectangle centered on X, positioned just below the top flat edge
        solid = (
            solid.faces(">Z").workplane(centerOption="ProjectedOrigin")
            .center(0, top_flat_y - top_rect_h / 2.0)
            .rect(top_rect_w, top_rect_h)
            .cutBlind(-top_rect_cut_depth)
        )
    
        # --- Cylindrical hole near base center ---
        solid = (
            solid.faces(">Z").workplane(centerOption="ProjectedOrigin")
            .center(0, 0.12)  # slightly above base
            .hole(base_center_hole_d, depth=base_center_hole_depth)
        )
    
        # --- Rotate and translate final object (generic) ---
        solid = solid.rotate((0, 0, 0), (0, 0, 1), 180).translate((0.0, 0.0, thickness / 2.0))
    
        return solid
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad_detailed/generation_20260225_155749/generated_models/00998356/gpt_generated.stl')
