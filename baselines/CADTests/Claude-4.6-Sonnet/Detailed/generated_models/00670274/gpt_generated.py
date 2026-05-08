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
        length  = 0.333015   # X dimension
        width   = 0.908225   # Y dimension
        height  = 0.006055   # Z dimension
        cut_sz  = 0.090822   # square cutout side length
    
        # --- Step 1: Main rectangular box centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Compute corner cutout centers ---
        # Each cutout is flush with the corner, so its center is at:
        # x = ±(length/2 - cut_sz/2), y = ±(width/2 - cut_sz/2)
        cx = length / 2 - cut_sz / 2
        cy = width  / 2 - cut_sz / 2
    
        corner_positions = [
            ( cx,  cy),
            (-cx,  cy),
            ( cx, -cy),
            (-cx, -cy),
        ]
    
        # --- Step 3: Cut square corners using properly centered cutters ---
        # Use box() with centered=True so the cutter spans the full height of the main box
        for (px, py) in corner_positions:
            cutter = (
                cq.Workplane("XY")
                .box(cut_sz, cut_sz, height, centered=True)
                .translate((px, py, 0))
            )
            result = result.cut(cutter)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        # Bounding box should still match the original box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Volume check: main box minus 4 corner cutouts
        main_vol     = length * width * height
        cutout_vol   = 4 * cut_sz * cut_sz * height
        expected_vol = main_vol - cutout_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Should have exactly 1 solid
        assert result.solids().size() == 1, \
            f"Solid count: expected 1, got {result.solids().size()}"
    
        # Face count should be more than 6 (original box faces)
        face_count = result.faces().size()
        assert face_count > 6, f"Face count should be > 6, got {face_count}"
    
        # Check that corner points are NOT inside the solid (cutouts removed material)
        # A point well inside a corner cutout region should be outside the solid
        corner_pt = (length/2 - 0.001, width/2 - 0.001, 0.0)
        assert not result.val().isInside(corner_pt), \
            f"Corner point {corner_pt} should be outside (cutout), but is inside"
    
        # Check that center of the solid IS inside
        center_pt = (0.0, 0.0, 0.0)
        assert result.val().isInside(center_pt), \
            f"Center point {center_pt} should be inside the solid"
    
        # Check that a mid-edge point (not at corner) IS inside
        mid_pt = (0.0, width/2 - 0.001, 0.0)
        assert result.val().isInside(mid_pt), \
            f"Mid-edge point {mid_pt} should be inside the solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.8f} (expected {expected_vol:.8f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670274/gpt_generated.stl')
