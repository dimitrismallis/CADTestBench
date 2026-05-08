import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        # Base rectangle dimensions
        base_length = 0.74801   # X direction (the long dimension)
        base_width  = 0.03125   # Y direction (height of the 2D profile)
        base_height = 0.00875   # Z direction (extrusion depth)
    
        # Cutout dimensions
        cut_width  = 0.1625     # X dimension of cutout
        cut_height = 0.0125     # Y dimension of cutout
        cut_offset = 0.01875    # distance from left edge of base rectangle
    
        # --- Step 1: Create base box ---
        # Use centered=False so left edge is at X=0, bottom at Y=0, base at Z=0
        result = (
            cq.Workplane("XY")
            .box(base_length, base_width, base_height, centered=False)
        )
    
        # --- Step 2: Add rectangular cutout towards bottom-right side ---
        # Cutout positioned:
        #   X: from cut_offset to cut_offset + cut_width (from left edge)
        #   Y: from 0 to cut_height (bottom of the rectangle)
        #   Z: through the full height (cutThruAll)
        #
        # Box occupies: X=[0, base_length], Y=[0, base_width], Z=[0, base_height]
        # Workplane on top face (>Z) has its origin projected to world (base_length/2, base_width/2, base_height)
        #
        # Cutout center in world coords:
        #   cx_world = cut_offset + cut_width/2
        #   cy_world = cut_height/2
        #
        # Offset from workplane center:
        #   dx = cx_world - base_length/2
        #   dy = cy_world - base_width/2
    
        cut_cx_world = cut_offset + cut_width / 2
        cut_cy_world = cut_height / 2
    
        dx = cut_cx_world - base_length / 2
        dy = cut_cy_world - base_width / 2
    
        # Build a cutter box in world coordinates and subtract it
        cutter = (
            cq.Workplane("XY")
            .box(cut_width, cut_height, base_height, centered=False)
            .translate((cut_offset, 0, 0))
        )
    
        result = result.cut(cutter)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        bb = result.val().BoundingBox()
    
        # Bounding box should still match base dimensions (cutout doesn't change outer bounds)
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Y width: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, \
            f"Z height: expected {base_height}, got {bb.zlen}"
    
        # Volume check: base volume minus cutout volume
        base_vol     = base_length * base_width * base_height
        cut_vol      = cut_width * cut_height * base_height
        expected_vol = base_vol - cut_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check cutout is approximately 1/4 of the base length
        ratio = cut_width / base_length
        assert abs(ratio - 0.25) < 0.15, \
            f"Cutout width ratio to base length: expected ~0.25, got {ratio:.4f}"
    
        # Verify the cutout exists: a point inside the cutout region should NOT be inside the solid
        # Cutout occupies X=[cut_offset, cut_offset+cut_width], Y=[0, cut_height], Z=[0, base_height]
        solid = result.val()
    
        cutout_point = (cut_offset + cut_width / 2, cut_height / 2, base_height / 2)
        assert not solid.isInside(cutout_point, tolerance=1e-6), \
            f"Point {cutout_point} should be in the cutout (outside solid), but isInside returned True"
    
        # Point in the solid body (far right, middle height) should be inside
        solid_point = (base_length * 0.9, base_width / 2, base_height / 2)
        assert solid.isInside(solid_point, tolerance=1e-6), \
            f"Point {solid_point} should be inside the solid, but isInside returned False"
    
        # Face count: base box has 6 faces, cutout adds faces
        # A rectangular cutout on one face adds net faces
        face_count = result.faces().size()
        assert face_count >= 8, \
            f"Face count: expected at least 8 (cutout adds faces), got {face_count}"
    
        print(f"All assertions passed!")
        print(f"Base volume:     {base_vol:.8f}")
        print(f"Cutout volume:   {cut_vol:.8f}")
        print(f"Expected volume: {expected_vol:.8f}")
        print(f"Actual volume:   {actual_vol:.8f}")
        print(f"Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
        print(f"Face count: {face_count}")
        print(f"Cutout/length ratio: {ratio:.4f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997068/gpt_generated.stl')
