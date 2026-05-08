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
        L = 0.75        # length (X)
        W = 0.28043     # width (Y)
        H = 0.02045     # height (Z)
    
        cut_L = 0.318403   # cut-out length (X)
        cut_W = 0.157741   # cut-out width (Y)
    
        # Cut-out offset above midpoint of width
        cut_offset_y = 0.021963
    
        # --- Step 1: Create the base rectangular prism centered at origin ---
        result = cq.Workplane("XY").box(L, W, H)
    
        # --- Step 2: Create the cut-out ---
        # Centered along length (X center = 0)
        # Offset above midpoint of width: Y center = cut_offset_y
        # Cut through full height
        result = (
            result
            .faces(">Z").workplane()
            .center(0, cut_offset_y)
            .rect(cut_L, cut_W)
            .cutThruAll()
        )
    
        # --- Step 3: Rotate -90 degrees around X-axis ---
        # This transforms: Y -> Z, Z -> -Y (or Y -> -Z depending on convention)
        # rotate(axisStart, axisEnd, angleDegrees)
        result = result.rotate((0, 0, 0), (1, 0, 0), -90)
    
        # --- Step 4: Center and align in 3D space ---
        # After rotation, check bounding box and translate to center at origin
        bb = result.val().BoundingBox()
        cx = (bb.xmin + bb.xmax) / 2
        cy = (bb.ymin + bb.ymax) / 2
        cz = (bb.zmin + bb.zmax) / 2
        result = result.translate((-cx, -cy, -cz))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # After -90° rotation around X: 
        # Original X stays X, original Y becomes Z, original Z becomes -Y (or +Y)
        # So: xlen = L = 0.75, ylen = H = 0.02045, zlen = W = 0.28043
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - H) < TOL, f"Y length (was Z): expected {H}, got {bb.ylen}"
        assert abs(bb.zlen - W) < TOL, f"Z length (was Y): expected {W}, got {bb.zlen}"
    
        # After centering, bounding box should be symmetric about origin
        assert abs(bb.xmin + bb.xmax) < TOL, f"X not centered: xmin={bb.xmin}, xmax={bb.xmax}"
        assert abs(bb.ymin + bb.ymax) < TOL, f"Y not centered: ymin={bb.ymin}, ymax={bb.ymax}"
        assert abs(bb.zmin + bb.zmax) < TOL, f"Z not centered: zmin={bb.zmin}, zmax={bb.zmax}"
    
        # Volume check: base box minus cut-out
        base_vol = L * W * H
        cut_vol = cut_L * cut_W * H
        expected_vol = base_vol - cut_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the cut-out exists (cylindrical or planar faces from the cut)
        # The cut creates additional planar faces
        face_count = result.faces("%Plane").size()
        assert face_count >= 6, f"Expected at least 6 planar faces, got {face_count}"
    
        # Check the cut-out by verifying a point inside the cut region is NOT inside the solid
        # Cut-out center in original coords: (0, cut_offset_y, 0) -> after rotation and centering
        # After -90° around X: (x, y, z) -> (x, z, -y) ... let's verify with isInside
        # A point at the center of the cut-out should be outside the solid
        # Original cut center: (0, cut_offset_y, 0) -> after -90° rot around X: (0, 0, -cut_offset_y)
        # After centering (center was already at origin before centering step): (0, 0, -cut_offset_y)
        solid = result.val()
    
        # Point inside the cut-out (should be outside solid)
        cut_center_after_rot = cq.Vector(0, 0, -cut_offset_y)
        assert not solid.isInside(cut_center_after_rot), \
            f"Point at cut-out center should be outside solid"
    
        # Point at solid corner (should be inside solid)
        # Use a point near the edge of the prism but not in the cut-out
        corner_point = cq.Vector(L/2 - 0.05, 0, W/2 - 0.05)
        assert solid.isInside(corner_point), \
            f"Point near corner should be inside solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Planar faces: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00002298/gpt_generated.stl')
