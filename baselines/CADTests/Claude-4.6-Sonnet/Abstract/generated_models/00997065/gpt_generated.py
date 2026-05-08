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
        sq = 10.0        # half-side of square (square is 20x20)
        rw = 4.0         # rectangle width (horizontal protrusion from square edge)
        rh = 4.0         # rectangle half-height (full height = 8 = 2 * rw)
        depth = 5.0      # extrusion depth
    
        # The profile: a 20x20 square with two 4x8 rectangles on left and right edges,
        # centered on the horizontal centerline (Y=0).
        # Rectangle height (8mm) = 2 × rectangle width (4mm)
    
        # --- Step 1: Build the closed profile using explicit line segments ---
        # Trace the outline clockwise starting from top-left corner of square
        result = (
            cq.Workplane("XY")
            .moveTo(-sq, sq)           # top-left of square
            .lineTo( sq, sq)           # top-right of square
            .lineTo( sq, rh)           # step down to top of right rectangle notch
            .lineTo( sq + rw, rh)      # go right to outer top of right rectangle
            .lineTo( sq + rw, -rh)     # go down to outer bottom of right rectangle
            .lineTo( sq, -rh)          # go left back to square right edge
            .lineTo( sq, -sq)          # step down to bottom-right of square
            .lineTo(-sq, -sq)          # go left to bottom-left of square
            .lineTo(-sq, -rh)          # step up to bottom of left rectangle notch
            .lineTo(-sq - rw, -rh)     # go left to outer bottom of left rectangle
            .lineTo(-sq - rw, rh)      # go up to outer top of left rectangle
            .lineTo(-sq, rh)           # go right back to square left edge
            .close()                   # close back to (-sq, sq)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: from -(sq + rw) to +(sq + rw) = -14 to +14 → xlen = 28
        expected_xlen = 2 * (sq + rw)  # 28
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: from -sq to +sq = -10 to +10 → ylen = 20
        expected_ylen = 2 * sq  # 20
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: extrusion depth = 5
        assert abs(bb.zlen - depth) < TOL, \
            f"Z length: expected {depth}, got {bb.zlen}"
    
        # Volume check:
        # Square area = 20 * 20 = 400
        # Two rectangles area = 2 * (rw * 2*rh) = 2 * (4 * 8) = 64
        # Total profile area = 464
        # Volume = 464 * depth = 464 * 5 = 2320
        sq_area = (2 * sq) ** 2
        rect_area = 2 * (rw * 2 * rh)
        total_area = sq_area + rect_area
        expected_vol = total_area * depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: extruded 12-sided polygon → 12 side faces + 1 top + 1 bottom = 14
        face_count = result.faces().size()
        assert face_count == 14, f"Face count: expected 14, got {face_count}"
    
        # Check the object is symmetric about X=0, Y=0
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - depth / 2) < TOL, \
            f"Center Z: expected {depth/2}, got {center.z}"
    
        # Check top and bottom faces at correct Z positions
        top_z = result.faces(">Z").val().BoundingBox().zmax
        bot_z = result.faces("<Z").val().BoundingBox().zmin
        assert abs(top_z - depth) < TOL, f"Top face Z: expected {depth}, got {top_z}"
        assert abs(bot_z - 0.0) < TOL, f"Bottom face Z: expected 0.0, got {bot_z}"
    
        # Verify the right rectangular tab exists (point inside it)
        right_tab_pt = cq.Vector(sq + rw / 2, 0, depth / 2)  # (12, 0, 2.5)
        assert result.val().isInside(right_tab_pt), \
            f"Right tab point {right_tab_pt} should be inside the solid"
    
        # Verify the left rectangular tab exists (point inside it)
        left_tab_pt = cq.Vector(-sq - rw / 2, 0, depth / 2)  # (-12, 0, 2.5)
        assert result.val().isInside(left_tab_pt), \
            f"Left tab point {left_tab_pt} should be inside the solid"
    
        # Verify a point outside the tabs (above tab height, within square X) is outside
        outside_pt = cq.Vector(sq + rw / 2, sq / 2, depth / 2)  # (12, 5, 2.5)
        assert not result.val().isInside(outside_pt), \
            f"Point {outside_pt} should be outside the solid"
    
        # Verify center of square is inside
        center_pt = cq.Vector(0, 0, depth / 2)
        assert result.val().isInside(center_pt), \
            f"Center point {center_pt} should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997065/gpt_generated.stl')
