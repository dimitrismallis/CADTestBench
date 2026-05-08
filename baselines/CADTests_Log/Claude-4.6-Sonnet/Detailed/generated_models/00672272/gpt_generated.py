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
        rect_length = 0.647727   # X direction
        rect_width  = 0.051136   # Y direction
        rect_height = 0.025568   # Z direction
    
        sq_length = rect_length / 16   # ≈ 0.040483
        sq_width  = rect_width         # = 0.051136
        sq_height = rect_height / 3    # ≈ 0.008523
    
        # --- Step 1: Base rectangle (centered at origin) ---
        result = cq.Workplane("XY").box(rect_length, rect_width, rect_height)
    
        # --- Step 2: Two small squares on top of the shorter edges ---
        # The base rectangle spans X: [-rect_length/2, +rect_length/2]
        # Each square is placed so its outer face aligns with the short edge of the rectangle.
        # Square center X = ±(rect_length/2 - sq_length/2)
        sq_cx_pos = rect_length / 2 - sq_length / 2
        sq_cx_neg = -(rect_length / 2 - sq_length / 2)
    
        # Squares sit on top of the base rectangle (z starts at rect_height/2)
        # We work on the top face and place boxes
        sq_z_center = rect_height / 2 + sq_height / 2
    
        # Positive X end square
        sq_pos = (
            cq.Workplane("XY")
            .center(sq_cx_pos, 0)
            .box(sq_length, sq_width, sq_height, centered=True)
            .translate((0, 0, sq_z_center))
        )
    
        # Negative X end square
        sq_neg = (
            cq.Workplane("XY")
            .center(sq_cx_neg, 0)
            .box(sq_length, sq_width, sq_height, centered=True)
            .translate((0, 0, sq_z_center))
        )
    
        # --- Step 3: Union all parts ---
        result = result.union(sq_pos).union(sq_neg)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: should equal rect_length (squares are within the rectangle's X span)
        assert abs(bb.xlen - rect_length) < TOL, \
            f"X length: expected {rect_length}, got {bb.xlen}"
    
        # Bounding box Y: should equal rect_width
        assert abs(bb.ylen - rect_width) < TOL, \
            f"Y width: expected {rect_width}, got {bb.ylen}"
    
        # Bounding box Z: should equal rect_height + sq_height (squares sit on top)
        expected_zlen = rect_height + sq_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z height: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Base box volume
        vol_base = rect_length * rect_width * rect_height
        # Two squares volume (they sit on top, no overlap with base)
        vol_squares = 2 * sq_length * sq_width * sq_height
        expected_vol = vol_base + vol_squares
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check symmetry: center of mass should be at x=0, y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # Check that the top of the squares is at rect_height/2 + sq_height
        expected_zmax = rect_height / 2 + sq_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
    
        # Check that the bottom is at -rect_height/2
        expected_zmin = -rect_height / 2
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
    
        # Check face count: base box has 6 faces, each square adds faces but shares the top face
        # The two squares each add a top face, 2 side faces (outer short + 2 long sides),
        # and the inner short face. The top face of the base is partially covered.
        # This is complex to count exactly, so just verify we have more than 6 faces
        face_count = result.faces().size()
        assert face_count > 6, f"Face count: expected > 6, got {face_count}"
    
        # Verify the squares are positioned at the ends (check isInside for key points)
        # Point inside positive square
        pt_pos = (sq_cx_pos, 0, rect_height / 2 + sq_height / 2)
        assert result.val().isInside(pt_pos), \
            f"Point {pt_pos} should be inside the positive square"
    
        # Point inside negative square
        pt_neg = (sq_cx_neg, 0, rect_height / 2 + sq_height / 2)
        assert result.val().isInside(pt_neg), \
            f"Point {pt_neg} should be inside the negative square"
    
        # Point in the middle of the base (not in a square region above base)
        pt_mid_top = (0, 0, rect_height / 2 + sq_height / 2)
        assert not result.val().isInside(pt_mid_top), \
            f"Point {pt_mid_top} should NOT be inside (middle top, above base, no square there)"
    
        print(f"All assertions passed!")
        print(f"  rect_length={rect_length}, rect_width={rect_width}, rect_height={rect_height}")
        print(f"  sq_length={sq_length:.6f}, sq_width={sq_width}, sq_height={sq_height:.6f}")
        print(f"  BBox: x={bb.xlen:.6f}, y={bb.ylen:.6f}, z={bb.zlen:.6f}")
        print(f"  Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672272/gpt_generated.stl')
