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
        main_length = 0.982759   # X dimension
        main_width  = 0.124138   # Y dimension
        cut_length  = 0.444828   # X dimension of each corner cutout
        cut_width   = 0.124138   # Y dimension of each corner cutout (same as main width)
        extrude_h   = 0.827586   # extrusion height
        translate_z = 0.077586   # height adjustment
    
        # --- Step 1: Build the 2D sketch ---
        # Main rectangle centered at origin: X from -main_length/2 to +main_length/2
        #                                    Y from -main_width/2  to +main_width/2
        # Corner cutouts (same full width in Y):
        #   Bottom-left:  X from -main_length/2 to -main_length/2 + cut_length
        #   Bottom-right: X from +main_length/2 - cut_length to +main_length/2
        # Since cut_width == main_width, the cutouts span the full Y extent.
        # Remaining shape: central rectangle of (main_length - 2*cut_length) x main_width
    
        # Use the Sketch API: start with main rect, subtract two corner rects
        # The sketch is on the XY plane, centered at origin
        half_L = main_length / 2.0
        half_W = main_width  / 2.0
        half_CL = cut_length / 2.0
        half_CW = cut_width  / 2.0
    
        # Center of left cutout in X: -half_L + half_CL
        left_cx  = -half_L + half_CL
        # Center of right cutout in X: +half_L - half_CL
        right_cx = +half_L - half_CL
        # Both cutouts are centered in Y (cy = 0) since cut_width == main_width
    
        sketch = (
            cq.Sketch()
            .rect(main_length, main_width)                          # main rectangle
            .rect(cut_length, cut_width, mode="s")                  # won't work centered - need to move
        )
    
        # Better approach: use Workplane with explicit polygon subtraction
        # Build the profile as a closed wire using lineTo operations
        # The remaining shape after cuts is a single central rectangle:
        # X: from -(main_length/2 - cut_length) to +(main_length/2 - cut_length)
        # Y: from -main_width/2 to +main_width/2
        central_length = main_length - 2.0 * cut_length  # 0.093103
        # central_width = main_width  # 0.124138
    
        # Actually, let me reconsider the shape more carefully.
        # The description says cut from bottom-left and bottom-right CORNERS.
        # If the cutout width equals the full rectangle width, the result is just the center strip.
        # But maybe "bottom" refers to the Z direction after extrusion, and the cuts are partial in Y?
        # 
        # Most natural interpretation: the sketch is a rectangle, and we cut rectangular notches
        # from two corners. If cut_width == main_width, the notches span the full width.
        # Result: a single central rectangle.
        #
        # Let's build it as a simple rectangle (the central strip):
    
        result = (
            cq.Workplane("XY")
            .rect(central_length, main_width)
            .extrude(extrude_h)
        )
    
        # --- Step 2: Translate ---
        # "center it properly with respect to its width" - already centered in XY
        # "adjust its height by 0.077586 units" - translate in Z by translate_z
        result = result.translate((0, 0, translate_z))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - central_length) < TOL, \
            f"X length: expected {central_length:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - main_width) < TOL, \
            f"Y width: expected {main_width:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z height: expected {extrude_h:.6f}, got {bb.zlen:.6f}"
    
        # Z position check: bottom at translate_z, top at translate_z + extrude_h
        assert abs(bb.zmin - translate_z) < TOL, \
            f"Z min: expected {translate_z:.6f}, got {bb.zmin:.6f}"
        assert abs(bb.zmax - (translate_z + extrude_h)) < TOL, \
            f"Z max: expected {translate_z + extrude_h:.6f}, got {bb.zmax:.6f}"
    
        # Centered in X and Y
        assert abs(bb.xmin + bb.xmax) < TOL, \
            f"X center: expected 0, got {(bb.xmin + bb.xmax):.6f}"
        assert abs(bb.ymin + bb.ymax) < TOL, \
            f"Y center: expected 0, got {(bb.ymin + bb.ymax):.6f}"
    
        # Volume check
        expected_vol = central_length * main_width * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a simple box has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        print(f"central_length = {central_length:.6f}")
        print(f"main_width     = {main_width:.6f}")
        print(f"extrude_h      = {extrude_h:.6f}")
        print(f"translate_z    = {translate_z:.6f}")
        print(f"Volume         = {actual_vol:.6f}")
        print(f"BBox: x=[{bb.xmin:.4f},{bb.xmax:.4f}] y=[{bb.ymin:.4f},{bb.ymax:.4f}] z=[{bb.zmin:.4f},{bb.zmax:.4f}]")
        print("All assertions passed.")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00984234/gpt_generated.stl')
