import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    from cadquery import selectors
    
    
    def create_cad() -> cq.Workplane:
        # --- Parameters (mm) ---
        base_w = 80.0
        tri_h = 70.0
        top_cut_y = 55.0
    
        thickness = 8.0
        bottom_fillet = 8.0
    
        hole_d = 3.0
        hole_offset = 7.0
    
        # --- Truncated triangle points in XY ---
        p_left = (-base_w / 2.0, 0.0)
        p_right = (base_w / 2.0, 0.0)
    
        x_left_cut = -base_w / 2.0 + (base_w / 2.0) * (top_cut_y / tri_h)
        x_right_cut = -x_left_cut
        p_top_left = (x_left_cut, top_cut_y)
        p_top_right = (x_right_cut, top_cut_y)
    
        # --- Base solid ---
        solid = (
            cq.Workplane("XY")
            .moveTo(*p_left)
            .lineTo(*p_right)
            .lineTo(*p_top_right)
            .lineTo(*p_top_left)
            .close()
            .extrude(thickness)
        )
    
        # --- Fillet the two bottom corner vertical edges robustly ---
        # Select all vertical edges, then pick the ones nearest to the two bottom corner points.
        # Use points slightly above the bottom to avoid ambiguity.
        z_probe = thickness * 0.5
        left_probe = (p_left[0], p_left[1], z_probe)
        right_probe = (p_right[0], p_right[1], z_probe)
    
        vert_edges = solid.edges("|Z")
    
        e_left = vert_edges.edges(selectors.NearestToPointSelector(left_probe))
        e_right = vert_edges.edges(selectors.NearestToPointSelector(right_probe))
    
        solid = solid.union(cq.Workplane("XY").newObject([]))  # no-op to keep chain style
    
        # Apply fillet to both edges (combine selections by adding objects)
        edges_to_fillet = cq.Workplane("XY").newObject(e_left.vals() + e_right.vals())
        solid = solid.newObject([solid.val()]).edges("|Z")  # reset selection context to solid
        solid = solid.newObject(edges_to_fillet.vals()).fillet(bottom_fillet)
    
        # --- Holes near each corner (cut through) ---
        hole_pts = [
            (p_left[0] + hole_offset, p_left[1] + hole_offset * 0.6),
            (p_right[0] - hole_offset, p_right[1] + hole_offset * 0.6),
            (0.0, top_cut_y - hole_offset),
        ]
    
        solid = (
            solid
            .faces(">Z").workplane(centerOption="CenterOfMass")
            .pushPoints(hole_pts)
            .hole(hole_d)
        )
    
        return solid
    
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/gpt52_react_cad/generation_20260217_113157/generated_models/00998356/gpt_generated.stl')
