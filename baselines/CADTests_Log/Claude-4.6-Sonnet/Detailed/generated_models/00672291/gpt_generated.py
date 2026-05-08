import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length   = 0.75   # extrusion depth (along Y)
        width    = 0.015  # thickness of the bracket material
        height   = 0.3    # total height of the main vertical leg
        ext_w    = 0.15   # horizontal extension width
        ext_h    = width  # horizontal extension height = 0.015
    
        # --- Step 1: Draw the L-shaped profile in the XZ plane ---
        # The L-shape:
        #   Vertical leg: X in [0, width], Z in [0, height]
        #   Horizontal flange: X in [0, ext_w], Z in [height-ext_h, height]
        #
        # 6 vertices (counter-clockwise when viewed from +Y):
        #   A = (0,       0)
        #   B = (width,   0)
        #   C = (width,   height - ext_h)
        #   D = (ext_w,   height - ext_h)
        #   E = (ext_w,   height)
        #   F = (0,       height)
    
        # --- Step 2: Build the profile using a polyline and extrude along Y ---
        result = (
            cq.Workplane("XZ")
            .polyline([
                (0,       0),
                (width,   0),
                (width,   height - ext_h),
                (ext_w,   height - ext_h),
                (ext_w,   height),
                (0,       height),
            ])
            .close()
            .extrude(length)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - ext_w) < TOL, \
            f"X extent: expected {ext_w}, got {bb.xlen}"
        assert abs(bb.ylen - length) < TOL, \
            f"Y extent (extrusion): expected {length}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # L-shape area = vertical_leg_area + flange_area - overlap_area
        # vertical leg: width * height
        # flange: ext_w * ext_h
        # overlap (top of vertical leg = bottom of flange): width * ext_h
        area_L = width * height + ext_w * ext_h - width * ext_h
        expected_vol = area_L * length
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Face count: L-profile has 6 edges → 6 side faces + 2 end faces = 8 total
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # All faces should be planar (no curves in an L-bracket)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 8, \
            f"Planar face count: expected 8, got {planar_count}"
    
        # Top face at Z = height
        top_z = result.faces(">Z").val().BoundingBox().zmax
        assert abs(top_z - height) < TOL, \
            f"Top Z: expected {height}, got {top_z}"
    
        # Bottom face at Z = 0
        bot_z = result.faces("<Z").val().BoundingBox().zmin
        assert abs(bot_z - 0.0) < TOL, \
            f"Bottom Z: expected 0.0, got {bot_z}"
    
        # Extrusion extent in Y: ylen must equal length
        assert abs(bb.ylen - length) < TOL, \
            f"Y length: expected {length}, got {bb.ylen}"
    
        # Center of mass checks (robust — check coordinates individually)
        com = cq.Shape.centerOfMass(result.val())
    
        # COM X must be between 0 and ext_w
        assert 0.0 <= com.x <= ext_w, \
            f"COM X={com.x:.6f} should be in [0, {ext_w}]"
    
        # COM Y must be between bb.ymin and bb.ymax (inside extrusion range)
        assert bb.ymin <= com.y <= bb.ymax, \
            f"COM Y={com.y:.6f} should be in [{bb.ymin:.4f}, {bb.ymax:.4f}]"
    
        # COM Z must be between 0 and height
        assert 0.0 <= com.z <= height, \
            f"COM Z={com.z:.6f} should be in [0, {height}]"
    
        # COM Y should be at the midpoint of the extrusion
        expected_com_y = (bb.ymin + bb.ymax) / 2.0
        assert abs(com.y - expected_com_y) < TOL, \
            f"COM Y: expected {expected_com_y:.6f}, got {com.y:.6f}"
    
        # Verify the step feature: there should be a face at X = width (inner step of L)
        x_faces_at_width = [
            f for f in result.faces("|X").vals()
            if abs(f.BoundingBox().xmax - width) < TOL or abs(f.BoundingBox().xmin - width) < TOL
        ]
        assert len(x_faces_at_width) >= 1, \
            f"Expected at least 1 face at X={width} (the step), found {len(x_faces_at_width)}"
    
        # Verify the step feature: face at Z = height - ext_h (the horizontal step)
        z_step_faces = [
            f for f in result.faces("|Z").vals()
            if abs(f.BoundingBox().zmax - (height - ext_h)) < TOL
            or abs(f.BoundingBox().zmin - (height - ext_h)) < TOL
        ]
        assert len(z_step_faces) >= 1, \
            f"Expected at least 1 face at Z={height - ext_h} (the L step), found {len(z_step_faces)}"
    
        return result
    
    final_result = create_cad()
    print("All assertions passed!")
    print(f"Bounding box: {final_result.val().BoundingBox().xlen:.4f} x "
          f"{final_result.val().BoundingBox().ylen:.4f} x "
          f"{final_result.val().BoundingBox().zlen:.4f}")
    print(f"Volume: {final_result.val().Volume():.8f}")
    print(f"Face count: {final_result.faces().size()}")
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672291/gpt_generated.stl')
