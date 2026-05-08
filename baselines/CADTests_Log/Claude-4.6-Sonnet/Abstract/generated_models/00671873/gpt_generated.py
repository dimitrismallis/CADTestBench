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
        base_width  = 100.0   # total width of base step
        base_height = 30.0    # height of base step
        top_width   = 60.0    # width of top step (centered on base)
        top_height  = 40.0    # height of top step
        depth       = 80.0    # extrusion depth (Y direction)
    
        # Derived
        top_left_x  = (base_width - top_width) / 2.0   # = 20
        top_right_x = top_left_x + top_width            # = 80
        total_height = base_height + top_height          # = 70
    
        # --- Step 1: Draw the two-step side profile in XY plane ---
        # Profile vertices (counter-clockwise):
        # (0,0) -> (100,0) -> (100,30) -> (80,30) -> (80,70) -> (20,70) -> (20,30) -> (0,30) -> close
        profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(base_width, 0)
            .lineTo(base_width, base_height)
            .lineTo(top_right_x, base_height)
            .lineTo(top_right_x, total_height)
            .lineTo(top_left_x, total_height)
            .lineTo(top_left_x, base_height)
            .lineTo(0, base_height)
            .close()
        )
    
        # --- Step 2: Extrude the profile in Z direction ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_width) < TOL, \
            f"X length: expected {base_width}, got {bb.xlen}"
        assert abs(bb.ylen - total_height) < TOL, \
            f"Y length (height): expected {total_height}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, \
            f"Z length (depth): expected {depth}, got {bb.zlen}"
    
        # Bounding box origin checks
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Volume check:
        # Base block: 100 x 30 x 80 = 240000
        # Top block:   60 x 40 x 80 = 192000
        # Total = 432000
        base_vol = base_width * base_height * depth
        top_vol  = top_width  * top_height  * depth
        expected_vol = base_vol + top_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count check:
        # The two-step pedestal extruded from an 8-vertex polygon should have:
        # 2 end faces (front/back) + 8 side faces = 10 planar faces total
        face_count = result.faces().size()
        assert face_count == 10, \
            f"Face count: expected 10, got {face_count}"
    
        # All faces should be planar (no cylinders)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Planar face count: expected 10, got {planar_count}"
    
        # Check the bottom face is at y=0 (min Y)
        bottom_faces = result.faces("<Y").size()
        assert bottom_faces >= 1, f"Expected at least 1 bottom face, got {bottom_faces}"
    
        # Check top face is at y = total_height = 70
        top_faces = result.faces(">Y").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
    
        # Verify the step geometry: a point inside the base but outside the top step
        # should be inside the solid
        # Point in base region (outside top step X range) at mid-depth
        base_only_point = (5, 15, depth / 2)   # x=5 is in base but not top step
        assert result.val().isInside(base_only_point), \
            f"Point {base_only_point} should be inside the base region"
    
        # Point in top step region should also be inside
        top_step_point = (50, base_height + 20, depth / 2)  # center of top step
        assert result.val().isInside(top_step_point), \
            f"Point {top_step_point} should be inside the top step region"
    
        # Point above the top step should be outside
        above_point = (50, total_height + 10, depth / 2)
        assert not result.val().isInside(above_point), \
            f"Point {above_point} should be outside (above top step)"
    
        # Point in the "notch" region (beside top step, above base) should be outside
        notch_point = (5, base_height + 10, depth / 2)  # x=5 is beside top step, above base
        assert not result.val().isInside(notch_point), \
            f"Point {notch_point} should be outside (notch region beside top step)"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm")
        print(f"  Volume: {actual_vol:.1f} mm³ (expected {expected_vol:.1f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00671873/gpt_generated.stl')
