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
        # --- Parameters ---
        length       = 1.5
        width        = 0.40625
        height       = 0.023438
        hole_dia     = 0.046875
        hole_r       = hole_dia / 2.0
    
        side_padding  = 0.048699   # Y-axis padding from long edge for the pair
        width_padding = 0.039062   # Y-axis padding from long edge (alternate)
        left_padding  = 0.242188   # X offset from left end for single hole
        right_padding = 0.242228   # X offset from right end for the pair
    
        # Box is centered at origin: X in [-0.75, 0.75], Y in [-0.203125, 0.203125]
        half_l = length / 2.0   # 0.75
        half_w = width  / 2.0   # 0.203125
    
        # --- Step 1: Create base rectangular box ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Define hole positions ---
        # Hole 1: single hole near left end, centered in width
        h1_x = -half_l + left_padding   # -0.75 + 0.242188 = -0.507812
        h1_y = 0.0
    
        # Holes 2 & 3: pair near right end, symmetrically placed in Y
        h23_x = half_l - right_padding  # 0.75 - 0.242228 = 0.507772
        h23_y = half_w - width_padding  # 0.203125 - 0.039062 = 0.164063
    
        # --- Step 3: Cut three cylindrical holes through the box ---
        # Work on the top face
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(h1_x, h1_y), (h23_x, h23_y), (h23_x, -h23_y)])
            .hole(hole_dia)
        )
    
        # --- Step 4: Translate so base aligns with Z=0 ---
        # Currently box center is at Z=0, so base is at Z=-height/2
        # Move up by height/2 so base is at Z=0
        result = result.translate((0, 0, height / 2.0))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Base at Z=0 after translation
        assert abs(bb.zmin - 0.0) < TOL, f"Z base: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"Z top: expected {height}, got {bb.zmax}"
    
        # Volume check: box minus 3 cylinders
        box_vol  = length * width * height
        cyl_vol  = 3 * math.pi * hole_r**2 * height
        expected_vol = box_vol - cyl_vol
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Should have 3 cylindrical faces (one per hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # Check holes exist by verifying points inside hole cylinders are NOT inside solid
        # Center of hole 1 at mid-height
        mid_z = height / 2.0
        h1_center = (h1_x, h1_y, mid_z)
        assert not solid.isInside(h1_center), \
            f"Hole 1 center should be outside solid (inside hole), but isInside returned True"
    
        h2_center = (h23_x, h23_y, mid_z)
        assert not solid.isInside(h2_center), \
            f"Hole 2 center should be outside solid (inside hole), but isInside returned True"
    
        h3_center = (h23_x, -h23_y, mid_z)
        assert not solid.isInside(h3_center), \
            f"Hole 3 center should be outside solid (inside hole), but isInside returned True"
    
        # Verify a point in the solid body is inside
        body_center = (0.0, 0.0, mid_z)
        assert solid.isInside(body_center), \
            f"Body center should be inside solid, but isInside returned False"
    
        # Check circular edges count: 3 holes × 2 circles (top + bottom) = 6
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 6, f"Circular edges: expected 6, got {circ_edges}"
    
        print("All assertions passed!")
        print(f"  BBox: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Hole 1 position: ({h1_x:.6f}, {h1_y:.6f})")
        print(f"  Holes 2&3 position: ({h23_x:.6f}, ±{h23_y:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996473/gpt_generated.stl')
