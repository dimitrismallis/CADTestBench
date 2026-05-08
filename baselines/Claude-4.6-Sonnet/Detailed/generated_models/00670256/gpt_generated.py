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
        outer_w = 0.1875      # width (X)
        outer_l = 0.1875      # length (Y)
        height  = 0.75        # extrusion height (Z before rotation)
        pad     = 0.014063    # wall padding on each side
    
        inner_w = outer_w - 2 * pad   # 0.1875 - 0.028126 = 0.159374
        inner_l = outer_l - 2 * pad   # same
    
        # --- Step 1: Create outer rectangular solid ---
        outer = cq.Workplane("XY").box(outer_w, outer_l, height)
    
        # --- Step 2: Create inner rectangular solid (the hollow core) ---
        inner = cq.Workplane("XY").box(inner_w, inner_l, height)
    
        # --- Step 3: Subtract inner from outer to form hollow pipe ---
        pipe = outer.cut(inner)
    
        # --- Step 4: Rotate 90 degrees around the X-axis ---
        # rotateAboutCenter rotates about the bounding box center
        result = pipe.rotateAboutCenter((1, 0, 0), 90)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After 90° rotation about X-axis:
        # Original: X=0.1875, Y=0.1875, Z=0.75
        # After rotation about X: X stays, Y becomes Z, Z becomes -Y
        # So new bounding box: xlen=0.1875, ylen=0.75, zlen=0.1875
        assert abs(bb.xlen - outer_w) < TOL, f"X length: expected {outer_w}, got {bb.xlen}"
        assert abs(bb.ylen - height)  < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - outer_l) < TOL, f"Z length: expected {outer_l}, got {bb.zlen}"
    
        # Volume check: outer box - inner box
        vol_outer = outer_w * outer_l * height
        vol_inner = inner_w * inner_l * height
        expected_vol = vol_outer - vol_inner
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The pipe should be hollow: check that the center of the pipe is NOT inside the solid
        # Center of bounding box
        cx = (bb.xmin + bb.xmax) / 2
        cy = (bb.ymin + bb.ymax) / 2
        cz = (bb.zmin + bb.zmax) / 2
        center_point = (cx, cy, cz)
        assert not solid.isInside(center_point), \
            f"Center point {center_point} should be inside the hollow, not the solid material"
    
        # Check that a point in the wall IS inside the solid
        # Wall point: near the outer edge in X, at center Y and Z
        wall_point_x = bb.xmin + pad / 2  # deep inside the wall
        wall_point = (wall_point_x, cy, cz)
        assert solid.isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid material"
    
        # Face count: a rectangular hollow pipe has 8 planar faces (4 outer + 4 inner) + 2 top + 2 bottom ring faces
        # Actually: outer 4 sides + inner 4 sides + 2 annular end faces = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Confirm it's a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670256/gpt_generated.stl')
