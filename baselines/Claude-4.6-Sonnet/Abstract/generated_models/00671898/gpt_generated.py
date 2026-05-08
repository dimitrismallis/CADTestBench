import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define key parameters ---
        # Center equilateral triangle
        center_base = 40.0          # base width of center triangle
        half_center = center_base / 2.0  # = 20
        center_height = center_base * math.sqrt(3) / 2.0  # ≈ 34.64
    
        # Left acute scalene triangle vertices:
        # A=(-50,0), B=(-20,0), C=(-38,25)
        left_x_outer = -50.0
        left_apex_x  = -38.0
        left_apex_y  =  25.0
    
        # Right acute scalene triangle (mirror of left):
        right_x_outer = 50.0
        right_apex_x  =  38.0
        right_apex_y  =  25.0
    
        # Extrusion depth
        depth = 20.0
    
        # --- Step 2: Define the 2D mountain profile outline ---
        # The outer boundary traces the silhouette of three mountains:
        # Bottom-left corner → left peak → valley between left & center →
        # center peak → valley between center & right → right peak → bottom-right corner
        # Then close along the base back to start.
        #
        # Points (counter-clockwise when viewed from front):
        # P0 = (-50, 0)  bottom-left
        # P1 = (-38, 25) left mountain apex
        # P2 = (-20, 0)  valley between left and center
        # P3 = (  0, center_height) center mountain apex
        # P4 = ( 20, 0)  valley between center and right
        # P5 = ( 38, 25) right mountain apex
        # P6 = ( 50, 0)  bottom-right
        # Close back to P0 along the base
    
        profile_points = [
            (left_x_outer,  0.0),           # P0
            (left_apex_x,   left_apex_y),   # P1 - left peak
            (-half_center,  0.0),           # P2 - valley left-center
            (0.0,           center_height), # P3 - center peak
            (half_center,   0.0),           # P4 - valley center-right
            (right_apex_x,  right_apex_y),  # P5 - right peak
            (right_x_outer, 0.0),           # P6
        ]
    
        # --- Step 3: Build the 2D profile using lineTo and close ---
        profile = (
            cq.Workplane("XY")
            .moveTo(profile_points[0][0], profile_points[0][1])
            .lineTo(profile_points[1][0], profile_points[1][1])
            .lineTo(profile_points[2][0], profile_points[2][1])
            .lineTo(profile_points[3][0], profile_points[3][1])
            .lineTo(profile_points[4][0], profile_points[4][1])
            .lineTo(profile_points[5][0], profile_points[5][1])
            .lineTo(profile_points[6][0], profile_points[6][1])
            .close()  # closes back to P0 along the base
        )
    
        # --- Step 4: Extrude the profile to create the 3D mountain object ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 4a. Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: from -50 to +50 → xlen = 100
        assert abs(bb.xlen - 100.0) < TOL, f"X length: expected 100.0, got {bb.xlen}"
        assert abs(bb.xmin - (-50.0)) < TOL, f"X min: expected -50.0, got {bb.xmin}"
        assert abs(bb.xmax - 50.0) < TOL, f"X max: expected 50.0, got {bb.xmax}"
    
        # Y extent: from 0 to center_height ≈ 34.64
        assert abs(bb.ymin - 0.0) < TOL, f"Y min: expected 0.0, got {bb.ymin}"
        assert abs(bb.ymax - center_height) < TOL, f"Y max: expected {center_height:.4f}, got {bb.ymax}"
        assert abs(bb.ylen - center_height) < TOL, f"Y length: expected {center_height:.4f}, got {bb.ylen}"
    
        # Z extent: from 0 to depth = 20
        assert abs(bb.zlen - depth) < TOL, f"Z length (depth): expected {depth}, got {bb.zlen}"
    
        # 4b. Volume check
        # The 2D profile area = area of three triangles
        # Center equilateral triangle: base=40, height=center_height
        area_center = 0.5 * center_base * center_height
    
        # Left scalene triangle: base=30 (from -50 to -20), height=25 (apex y)
        area_left = 0.5 * 30.0 * left_apex_y
    
        # Right scalene triangle: base=30 (from 20 to 50), height=25 (apex y)
        area_right = 0.5 * 30.0 * right_apex_y
    
        total_area = area_center + area_left + area_right
        expected_volume = total_area * depth
    
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.2f}, got {actual_volume:.2f}"
    
        # 4c. Face count check
        # The extruded mountain profile should have:
        # - 1 bottom face (base rectangle-ish, planar)
        # - 1 back face (same profile shape, planar)
        # - 1 front face (same profile shape, planar)  [front and back are the profile faces]
        # - 7 side faces (one per edge of the profile: 6 sloped + 1 base = 7 edges → 7 side faces)
        # Total = 2 profile faces + 7 side faces = 9 faces
        # Wait: the profile has 7 line segments (P0→P1, P1→P2, P2→P3, P3→P4, P4→P5, P5→P6, P6→P0)
        # So 7 side faces + 2 end faces = 9 total
        face_count = result.faces().size()
        assert face_count == 9, f"Face count: expected 9, got {face_count}"
    
        # 4d. The object should be a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # 4e. Verify the center of mass is at x≈0 (symmetric left-right) and z≈depth/2
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0) < TOL, f"Center of mass X: expected 0.0 (symmetric), got {com.x}"
        assert abs(com.z - depth / 2.0) < TOL, f"Center of mass Z: expected {depth/2.0}, got {com.z}"
    
        # 4f. Verify the apex points are on the surface (isInside check just inside)
        # The center apex at (0, center_height, depth/2) should be on the boundary
        # Check a point just below the center apex is inside
        inside_pt = (0.0, center_height - 1.0, depth / 2.0)
        assert result.val().isInside(inside_pt), \
            f"Point just below center apex should be inside the solid: {inside_pt}"
    
        # A point above the center apex should be outside
        outside_pt = (0.0, center_height + 1.0, depth / 2.0)
        assert not result.val().isInside(outside_pt), \
            f"Point above center apex should be outside the solid: {outside_pt}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen}, Y={bb.ylen:.4f}, Z={bb.zlen}")
        print(f"Volume: {actual_volume:.2f} (expected {expected_volume:.2f})")
        print(f"Face count: {face_count}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00671898/gpt_generated.stl')
