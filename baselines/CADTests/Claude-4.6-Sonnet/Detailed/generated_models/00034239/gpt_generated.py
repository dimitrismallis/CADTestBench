import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 1.5       # X dimension
        width  = 1.2       # Y dimension
        height = 0.15      # Z dimension
    
        large_hole_d  = 0.675
        small_hole_d  = 0.1968
        edge_gap      = 0.033   # gap from rectangle edge to hole edge
    
        # --- Step 1: Create the base rectangular prism (centered at origin) ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Cut the large central hole (centered at origin) ---
        result = result.faces(">Z").workplane().hole(large_hole_d)
    
        # --- Step 3: Compute positions of the two smaller holes ---
        # Rectangle half-length in X = 0.75
        # Small hole radius = 0.1968 / 2 = 0.0984
        # Center X = half_length - edge_gap - small_hole_radius
        half_length = length / 2.0          # 0.75
        small_hole_r = small_hole_d / 2.0   # 0.0984
        cx = half_length - edge_gap - small_hole_r  # 0.75 - 0.033 - 0.0984 = 0.6186
    
        # --- Step 4: Cut the two smaller holes ---
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(cx, 0), (-cx, 0)])
            .hole(small_hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check
        # Base volume minus holes
        base_vol  = length * width * height
        large_vol = math.pi * (large_hole_d / 2.0) ** 2 * height
        small_vol = 2 * math.pi * (small_hole_d / 2.0) ** 2 * height
        expected_vol = base_vol - large_vol - small_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: 1 large + 2 small = 3 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, f"Cylindrical faces: expected 3, got {cyl_faces}"
    
        # Check that the large hole center is at (0, 0) — line through center should intersect 2 faces (top + bottom of hole)
        faces_hit = result.val().facesIntersectedByLine((0, 0, 1), (0, 0, -1))
        # The line through the center of the large hole should pass through the hole (no solid material)
        # So it should NOT intersect any face at the center (it's a hole)
        # Actually it will intersect the cylindrical wall tangentially — let's check differently:
        # Point at center of large hole should NOT be inside the solid
        center_point = (0, 0, 0)
        assert not result.val().isInside(center_point), \
            "Center of large hole should be empty (not inside solid)"
    
        # Check that a point inside the solid (away from holes) IS inside
        solid_point = (0, 0.55, 0)  # near the top edge, away from holes
        assert result.val().isInside(solid_point), \
            f"Point {solid_point} should be inside the solid"
    
        # Check small hole centers are empty
        assert not result.val().isInside((cx, 0, 0)), \
            f"Center of right small hole at ({cx}, 0, 0) should be empty"
        assert not result.val().isInside((-cx, 0, 0)), \
            f"Center of left small hole at ({-cx}, 0, 0) should be empty"
    
        # Check bounding box center is at origin
        cx_bb = (bb.xmin + bb.xmax) / 2.0
        cy_bb = (bb.ymin + bb.ymax) / 2.0
        cz_bb = (bb.zmin + bb.zmax) / 2.0
        assert abs(cx_bb) < TOL, f"Bounding box center X: expected 0, got {cx_bb}"
        assert abs(cy_bb) < TOL, f"Bounding box center Y: expected 0, got {cy_bb}"
        assert abs(cz_bb) < TOL, f"Bounding box center Z: expected 0, got {cz_bb}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00034239/gpt_generated.stl')
