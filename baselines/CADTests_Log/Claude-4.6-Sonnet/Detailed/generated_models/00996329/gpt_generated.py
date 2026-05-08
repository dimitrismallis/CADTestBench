import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        width     = 0.333333   # extrusion depth (Y direction)
        thickness = 0.083333   # arm thickness
        length    = 0.666667   # horizontal arm length (0.75 - thickness)
        total_h   = 0.75       # total height of vertical arm = thickness + length
    
        # --- Step 1: Draw the L-shaped profile on the XY plane ---
        # The L consists of:
        #   - A vertical arm: thickness wide, total_h tall (left side)
        #   - A horizontal arm: (thickness + length) wide, thickness tall (bottom)
        # We draw the outline as a closed wire using lineTo/close
    
        # Corners of the L (starting bottom-left, going counter-clockwise):
        # (0, 0) -> (total_h, 0) -> (total_h, thickness) -> (thickness, thickness)
        # -> (thickness, total_h) -> (0, total_h) -> back to (0, 0)
        # Here X = horizontal extent, Y = vertical extent in the sketch plane
    
        total_w = thickness + length  # = 0.083333 + 0.666667 = 0.75
    
        profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(total_w, 0)
            .lineTo(total_w, thickness)
            .lineTo(thickness, thickness)
            .lineTo(thickness, total_h)
            .lineTo(0, total_h)
            .close()
        )
    
        # --- Step 2: Extrude the L profile along Z by the width ---
        result = profile.extrude(width)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - total_w) < TOL, f"X length: expected {total_w}, got {bb.xlen}"
        assert abs(bb.ylen - total_h) < TOL, f"Y length: expected {total_h}, got {bb.ylen}"
        assert abs(bb.zlen - width) < TOL,   f"Z length (width): expected {width}, got {bb.zlen}"
    
        # Volume check: L-area = total_w * thickness + thickness * (total_h - thickness)
        #             = thickness * (total_w + total_h - thickness)
        l_area = total_w * thickness + thickness * (total_h - thickness)
        expected_vol = l_area * width
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: an L-shaped extrusion has 8 faces
        # (6 for a box minus the notch = 6 planar faces + the notch adds 2 more = 8 total)
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # Check planar faces only (all faces of an L extrusion are planar)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 8, f"Planar face count: expected 8, got {planar_count}"
    
        # Check top face is at Z = width
        top_z = result.faces(">Z").val().Center().z
        assert abs(top_z - width) < TOL, f"Top face Z: expected {width}, got {top_z}"
    
        # Check bottom face is at Z = 0
        bot_z = result.faces("<Z").val().Center().z
        assert abs(bot_z - 0.0) < TOL, f"Bottom face Z: expected 0, got {bot_z}"
    
        # Verify the notch: a point inside the missing corner should be outside the solid
        # The missing corner is at (thickness + epsilon, thickness + epsilon, width/2)
        notch_point = (thickness + 0.1, thickness + 0.1, width / 2)
        assert not result.val().isInside(notch_point), \
            f"Notch point {notch_point} should be outside the L-bracket"
    
        # Verify a point inside the vertical arm is inside the solid
        inside_vert = (thickness / 2, total_h / 2, width / 2)
        assert result.val().isInside(inside_vert), \
            f"Point {inside_vert} should be inside the vertical arm"
    
        # Verify a point inside the horizontal arm is inside the solid
        inside_horiz = (total_w / 2, thickness / 2, width / 2)
        assert result.val().isInside(inside_horiz), \
            f"Point {inside_horiz} should be inside the horizontal arm"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996329/gpt_generated.stl')
