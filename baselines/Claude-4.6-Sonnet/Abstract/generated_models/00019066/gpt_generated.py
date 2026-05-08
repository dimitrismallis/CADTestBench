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
        rect_length = 30.0   # length of base rectangle
        rect_width  = 20.0   # width  (~1.5x ratio: 30/20 = 1.5)
        rect_thick  = 2.0    # marginal (thin) extrusion thickness
        rod_size    = 2.0    # small square cross-section of rod
        rod_height  = 3 * rect_length  # = 90, rod height is 3x the length
    
        # --- Step 1: Create the marginally extruded base rectangle ---
        # Centered at origin, extends from -15 to +15 in X, -10 to +10 in Y, 0 to 2 in Z
        base = (
            cq.Workplane("XY")
            .box(rect_length, rect_width, rect_thick, centered=(True, True, False))
        )
    
        # --- Step 2: Add a small rectangular rod at one corner of the top surface ---
        # The top surface is at Z = rect_thick = 2
        # Corner of the rectangle (top face) is at (±15, ±10)
        # We'll use the corner at (+15, +10) — i.e., max X, max Y corner
        # Rod cross-section: rod_size × rod_size = 2×2
        # Rod is placed so its corner aligns with the rectangle corner
        # Rod center in XY: (rect_length/2 - rod_size/2, rect_width/2 - rod_size/2)
        rod_cx = rect_length / 2 - rod_size / 2   # = 14
        rod_cy = rect_width  / 2 - rod_size / 2   # = 9
    
        rod = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(rod_cx, rod_cy, rect_thick))
            .box(rod_size, rod_size, rod_height, centered=(True, True, False))
        )
    
        # --- Step 3: Union base and rod ---
        result = base.union(rod)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: from -rect_length/2 to +rect_length/2 = -15 to +15 → xlen = 30
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
    
        # Y: from -rect_width/2 to +rect_width/2 = -10 to +10 → ylen = 20
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y length: expected {rect_width}, got {bb.ylen}"
    
        # Z: from 0 to rect_thick + rod_height = 2 + 90 = 92
        expected_zlen = rect_thick + rod_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be 0 (base starts at Z=0)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin}"
    
        # Z max should be rect_thick + rod_height = 92
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # Length/width ratio check: 30/20 = 1.5
        ratio = rect_length / rect_width
        assert abs(ratio - 1.5) < TOL, \
            f"Length/width ratio: expected 1.5, got {ratio}"
    
        # Rod height = 3 × rect_length
        assert abs(rod_height - 3 * rect_length) < TOL, \
            f"Rod height: expected {3 * rect_length}, got {rod_height}"
    
        # Volume check: base volume + rod volume (they share a face, no overlap)
        base_vol = rect_length * rect_width * rect_thick   # 30*20*2 = 1200
        rod_vol  = rod_size * rod_size * rod_height         # 2*2*90 = 360
        expected_vol = base_vol + rod_vol                   # 1560
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Rod is inside the bounding box of the base in XY (corner placement)
        # Rod outer X edge should be at rect_length/2 = 15
        rod_xmax = rod_cx + rod_size / 2   # 14 + 1 = 15
        assert abs(rod_xmax - rect_length / 2) < TOL, \
            f"Rod X max: expected {rect_length/2}, got {rod_xmax}"
    
        rod_ymax = rod_cy + rod_size / 2   # 9 + 1 = 10
        assert abs(rod_ymax - rect_width / 2) < TOL, \
            f"Rod Y max: expected {rect_width/2}, got {rod_ymax}"
    
        # Check that a point inside the rod (above the base) is inside the solid
        rod_interior = (rod_cx, rod_cy, rect_thick + rod_height / 2)
        assert result.val().isInside(rod_interior), \
            f"Point {rod_interior} should be inside the rod"
    
        # Check that a point outside the rod (above the base, away from corner) is NOT inside
        outside_pt = (0.0, 0.0, rect_thick + 1.0)
        assert not result.val().isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid (above base center, not in rod)"
    
        print("All assertions passed!")
        print(f"  Base: {rect_length} x {rect_width} x {rect_thick}")
        print(f"  Rod:  {rod_size} x {rod_size} x {rod_height} at corner ({rod_cx}, {rod_cy})")
        print(f"  Total volume: {actual_vol:.1f}")
        print(f"  Bounding box: {bb.xlen} x {bb.ylen} x {bb.zlen}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00019066/gpt_generated.stl')
