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
        length = 80.0    # X dimension (longer side)
        width  = 30.0    # Y dimension (shorter side)
        height = 5.0     # Z dimension (extrusion thickness)
        hole_d = 4.0     # hole diameter
        hole_r = hole_d / 2.0
    
        # Holes arranged along Y (aligned with shorter side),
        # positioned towards the +X end of the rectangle.
        # Three holes spaced 8mm apart in Y, centered at Y=0,
        # placed at X = +25 (towards the +X end, which is at X=+40)
        hole_x = 25.0
        hole_spacing_y = 8.0
    
        # --- Step 1: Draw rectangle sketch and extrude ---
        result = cq.Workplane("XY").rect(length, width).extrude(height)
    
        # --- Step 2: Create three holes aligned with the shorter side (Y),
        #             towards one side (+X end) of the object ---
        # Push three points along Y at x=hole_x
        hole_points = [
            (hole_x, -hole_spacing_y),
            (hole_x,  0.0),
            (hole_x,  hole_spacing_y),
        ]
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints(hole_points)
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # 2. Volume check: box minus three cylindrical holes
        box_vol  = length * width * height
        hole_vol = 3 * math.pi * hole_r**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: 3 holes × 1 cylindrical face each = 3
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # 4. Circular edges: each hole has 2 circular edges (top + bottom) → 6 total
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 6, f"Circular edges: expected 6, got {circ_edges}"
    
        # 5. Holes are through-holes: check that a point at the center of each hole
        #    at mid-height is NOT inside the solid
        solid = result.val()
        for (hx, hy) in hole_points:
            mid_z = height / 2.0
            pt = (hx, hy, mid_z)
            assert not solid.isInside(pt), \
                f"Point {pt} should be inside a hole (not solid), but isInside returned True"
    
        # 6. Holes are towards the +X side: hole_x should be > 0 (positive X half)
        assert hole_x > 0, "Holes should be on the positive X side of the rectangle"
    
        # 7. A point in the solid body (away from holes) should be inside
        solid_pt = (-30.0, 0.0, height / 2.0)
        assert solid.isInside(solid_pt), \
            f"Point {solid_pt} should be inside the solid, but isInside returned False"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997373/gpt_generated.stl')
