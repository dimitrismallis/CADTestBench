import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length   = 1.5
        width    = 1.02857
        height   = 0.17143
        hole_d   = 0.095635
        inset_x  = 0.263507   # inset from edges along length
        inset_y  = 0.219429   # inset from edges along width
    
        # --- Step 1: Create the rectangular prism (centered at origin) ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Compute hole center positions ---
        # Box is centered, so half-extents are length/2 and width/2
        hx = length / 2 - inset_x   # 0.75 - 0.263507 = 0.486493
        hy = width  / 2 - inset_y   # 0.514285 - 0.219429 = 0.294856
    
        hole_positions = [
            ( hx,  hy),
            (-hx,  hy),
            ( hx, -hy),
            (-hx, -hy),
        ]
    
        # --- Step 3: Drill four holes from the top face through the prism ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_positions)
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box minus 4 cylindrical holes
        box_vol  = length * width * height
        hole_vol = 4 * math.pi * (hole_d / 2) ** 2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Four cylindrical faces (one per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces: expected 4, got {cyl_faces}"
    
        # Circular edges check: 4 holes × 2 circles (top + bottom) = 8 circular edges
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 8, f"Circular edges: expected 8, got {circ_edges}"
    
        # Check that hole centers are at the correct positions (via isInside on the solid)
        solid = result.val()
        # Points just inside the hole (should NOT be inside the solid)
        for (px, py) in hole_positions:
            pt_in_hole = (px, py, 0.0)   # at mid-height, center of hole
            assert not solid.isInside(pt_in_hole, tolerance=1e-4), \
                f"Point {pt_in_hole} should be inside a hole (not solid), but isInside returned True"
    
        # Points well away from holes (should be inside the solid)
        test_pts_inside = [(0.0, 0.0, 0.0)]
        for pt in test_pts_inside:
            assert solid.isInside(pt, tolerance=1e-4), \
                f"Point {pt} should be inside the solid, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00006578/gpt_generated.stl')
