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
        # --- Step 1: Define the 2D profile vertices ---
        # Rectangle: 0.75 (X) × 0.0018 (Y)
        # Square1: 0.021 × 0.021, bottom-right at top-right of rectangle
        #   → x: [0.75-0.021, 0.75] = [0.729, 0.75], y: [0.0018, 0.0228]
        # Square2: 0.0192 × 0.0192, bottom-right at top-right of square1
        #   → x: [0.75-0.0192, 0.75] = [0.7308, 0.75], y: [0.0228, 0.042]
        # Closed polygon (counter-clockwise):
    
        rect_w = 0.75
        rect_h = 0.0018
        sq1 = 0.021
        sq2 = 0.0192
        extrude_depth = 0.84
    
        # Vertices of the closed profile (CCW)
        pts = [
            (0.0,           0.0),           # 1: bottom-left of rectangle
            (rect_w,        0.0),           # 2: bottom-right of rectangle
            (rect_w,        rect_h + sq1 + sq2),  # 3: top-right of square2
            (rect_w - sq2,  rect_h + sq1 + sq2),  # 4: top-left of square2
            (rect_w - sq2,  rect_h + sq1),         # 5: step between sq2 and sq1
            (rect_w - sq1,  rect_h + sq1),         # 6: top-left of square1
            (rect_w - sq1,  rect_h),               # 7: bottom-left of square1
            (0.0,           rect_h),               # 8: top-left of rectangle
        ]
    
        # --- Step 2: Build the profile as a closed wire and extrude ---
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        total_height = rect_h + sq1 + sq2  # 0.0018 + 0.021 + 0.0192 = 0.042
        assert abs(bb.xlen - rect_w) < TOL, f"X length: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - total_height) < TOL, f"Y height: expected {total_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, f"Z depth: expected {extrude_depth}, got {bb.zlen}"
    
        # Volume check
        # Profile area = rectangle area + square1 area + square2 area
        area_rect = rect_w * rect_h
        area_sq1 = sq1 * sq1
        area_sq2 = sq2 * sq2
        expected_area = area_rect + area_sq1 + area_sq2
        expected_vol = expected_area * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: extruded polygon with 8 sides → 8 side faces + 2 end faces = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check bounding box origin
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Check that the solid contains a point inside the rectangle portion
        mid_rect = cq.Vector(rect_w / 2, rect_h / 2, extrude_depth / 2)
        assert result.val().isInside(mid_rect), "Point in rectangle portion should be inside solid"
    
        # Check that a point above the rectangle but not in the squares is OUTSIDE
        outside_pt = cq.Vector(rect_w / 4, rect_h + sq1 / 2, extrude_depth / 2)
        assert not result.val().isInside(outside_pt), "Point above rectangle left portion should be outside solid"
    
        # Check that a point inside square1 is inside
        sq1_mid = cq.Vector(rect_w - sq1 / 2, rect_h + sq1 / 2, extrude_depth / 2)
        assert result.val().isInside(sq1_mid), "Point in square1 portion should be inside solid"
    
        # Check that a point inside square2 is inside
        sq2_mid = cq.Vector(rect_w - sq2 / 2, rect_h + sq1 + sq2 / 2, extrude_depth / 2)
        assert result.val().isInside(sq2_mid), "Point in square2 portion should be inside solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997040/gpt_generated.stl')
