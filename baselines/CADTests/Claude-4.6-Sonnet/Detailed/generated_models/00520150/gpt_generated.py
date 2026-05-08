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
        total_length = 0.75   # X direction
        total_width  = 0.75   # Y direction
        height       = 0.1875 # Z direction (extrusion)
    
        # L-shape: full 0.75x0.75 minus top-right quadrant
        # Each bar of the L is 0.375 wide (half of 0.75)
        bar_thickness = total_length / 2.0  # 0.375
    
        # --- Step 1: Define L-shaped 2D profile using a closed polyline ---
        # Vertices traced counter-clockwise:
        #   (0, 0)           bottom-left
        #   (0.75, 0)        bottom-right
        #   (0.75, 0.375)    right side of horizontal bar top
        #   (0.375, 0.375)   inner corner of L
        #   (0.375, 0.75)    top of vertical bar right side
        #   (0, 0.75)        top-left
        #   back to (0, 0)
    
        pts = [
            (0.0,           0.0),
            (total_length,  0.0),
            (total_length,  bar_thickness),
            (bar_thickness, bar_thickness),
            (bar_thickness, total_width),
            (0.0,           total_width),
        ]
    
        # --- Step 2: Create the L-shaped profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .close()
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - total_length) < TOL, f"X length: expected {total_length}, got {bb.xlen}"
        assert abs(bb.ylen - total_width)  < TOL, f"Y width:  expected {total_width},  got {bb.ylen}"
        assert abs(bb.zlen - height)       < TOL, f"Z height: expected {height},       got {bb.zlen}"
    
        # Volume check:
        # L-shape area = full square minus top-right quadrant
        # = (0.75 * 0.75) - (0.375 * 0.375)
        # = 0.5625 - 0.140625 = 0.421875
        l_area = total_length * total_width - bar_thickness * bar_thickness
        expected_vol = l_area * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count check:
        # An L-extrusion has:
        #   - 1 bottom face (L-shaped planar)
        #   - 1 top face (L-shaped planar)
        #   - 6 side faces (one per edge of the L polygon)
        # Total = 8 faces
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # Check it's a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check bounding box origin (L starts at 0,0,0 since we used moveTo(0,0))
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0.0, got {bb.xmin}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0.0, got {bb.ymin}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0.0, got {bb.zmin}"
    
        # Check top and bottom planar faces exist
        top_faces    = result.faces(">Z").size()
        bottom_faces = result.faces("<Z").size()
        assert top_faces    == 1, f"Top faces: expected 1, got {top_faces}"
        assert bottom_faces == 1, f"Bottom faces: expected 1, got {bottom_faces}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520150/gpt_generated.stl')
