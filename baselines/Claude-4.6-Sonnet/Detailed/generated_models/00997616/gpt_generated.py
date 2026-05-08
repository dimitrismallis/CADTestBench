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
        # --- Parameters ---
        rect_w = 1.30586
        rect_h = 0.616516
        total_h = 1.25576
        tri_h = total_h - rect_h  # 0.639244
        corner_base = 0.019678
        corner_height = 0.101205
        extrude_h = 0.023051
    
        # --- Step 1: Define the pentagon profile vertices ---
        # Rectangle corners (centered at origin):
        # Bottom-left: (-rect_w/2, -rect_h/2)
        # Bottom-right: (rect_w/2, -rect_h/2)
        # Top-right: (rect_w/2, rect_h/2)
        # Top-left: (-rect_w/2, rect_h/2)
        # Triangle apex: (0, rect_h/2 + tri_h)
    
        half_w = rect_w / 2   # 0.65293
        half_h = rect_h / 2   # 0.308258
        apex_y = half_h + tri_h  # 0.947502
    
        # Corner cutouts: small right triangles at bottom-left and bottom-right
        # Bottom-left corner: cut triangle with base along bottom (going right) and height along left side (going up)
        # The cut removes a triangle from (-half_w, -half_h) corner
        # Cut vertices: (-half_w, -half_h), (-half_w + corner_base, -half_h), (-half_w, -half_h + corner_height)
        # So the profile skips the corner and goes through the cut points
    
        # Full pentagon profile with corner cuts (clockwise or counter-clockwise):
        # Starting from bottom-left, going counter-clockwise:
        # After cutting bottom-left corner:
        #   (-half_w + corner_base, -half_h)  [bottom edge, just right of cut]
        #   (half_w - corner_base, -half_h)   [bottom edge, just left of right cut]
        #   (half_w, -half_h + corner_height) [right edge, just above right cut]
        #   (half_w, half_h)                  [top-right of rectangle]
        #   (0, apex_y)                        [triangle apex]
        #   (-half_w, half_h)                 [top-left of rectangle]
        #   (-half_w, -half_h + corner_height)[left edge, just above left cut]
    
        pts = [
            (-half_w + corner_base, -half_h),
            (half_w - corner_base, -half_h),
            (half_w, -half_h + corner_height),
            (half_w, half_h),
            (0, apex_y),
            (-half_w, half_h),
            (-half_w, -half_h + corner_height),
        ]
    
        # --- Step 2: Build the 2D profile using Workplane polygon ---
        # Use a closed wire from the points
        profile = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .close()
        )
    
        # --- Step 3: Extrude the profile ---
        result = profile.extrude(extrude_h)
    
        # --- Step 4: Rotate -90 degrees around Z-axis ---
        result = result.rotate((0, 0, 0), (0, 0, 1), -90)
    
        # --- Step 5: Translate to center at (0.605354, -0.75, 0) ---
        # After rotation and extrusion, find current center and translate
        # The shape is extruded from z=0 to z=extrude_h, centered in XY
        # Current center of bounding box:
        bb_before = result.val().BoundingBox()
        cx = (bb_before.xmin + bb_before.xmax) / 2
        cy = (bb_before.ymin + bb_before.ymax) / 2
        cz = (bb_before.zmin + bb_before.zmax) / 2
    
        target_cx = 0.605354
        target_cy = -0.75
        target_cz = 0.0
    
        dx = target_cx - cx
        dy = target_cy - cy
        dz = target_cz - cz
    
        result = result.translate((dx, dy, dz))
    
        # --- Final object verification ---
        TOL = 0.01
        bb = result.val().BoundingBox()
    
        # After -90° rotation around Z: x and y swap (with sign change)
        # Original (before rotation): xlen = rect_w = 1.30586, ylen = total_h = 1.25576, zlen = extrude_h
        # After -90° rotation: xlen = total_h = 1.25576, ylen = rect_w = 1.30586, zlen = extrude_h
        expected_xlen = total_h   # 1.25576
        expected_ylen = rect_w    # 1.30586
        expected_zlen = extrude_h # 0.023051
    
        assert abs(bb.xlen - expected_xlen) < TOL, f"xlen: expected ~{expected_xlen:.5f}, got {bb.xlen:.5f}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"ylen: expected ~{expected_ylen:.5f}, got {bb.ylen:.5f}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"zlen: expected ~{expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Center of bounding box should be near (0.605354, -0.75, 0)
        center_x = (bb.xmin + bb.xmax) / 2
        center_y = (bb.ymin + bb.ymax) / 2
        center_z = (bb.zmin + bb.zmax) / 2
    
        assert abs(center_x - 0.605354) < TOL, f"center_x: expected 0.605354, got {center_x:.6f}"
        assert abs(center_y - (-0.75)) < TOL, f"center_y: expected -0.75, got {center_y:.6f}"
        assert abs(center_z - 0.0) < TOL, f"center_z: expected 0.0, got {center_z:.6f}"
    
        # Volume check: approximate area of profile * extrude_h
        # Profile area = rectangle + triangle - 2 corner triangles
        rect_area = rect_w * rect_h
        tri_area = 0.5 * rect_w * tri_h
        corner_area = 2 * 0.5 * corner_base * corner_height
        expected_area = rect_area + tri_area - corner_area
        expected_vol = expected_area * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 7-sided polygon extruded = 7 side faces + 2 end faces = 9 total
        face_count = result.faces().size()
        assert face_count == 9, f"Face count: expected 9, got {face_count}"
    
        # Should have exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        print(f"All assertions passed!")
        print(f"BBox: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Center: ({center_x:.6f}, {center_y:.6f}, {center_z:.6f})")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Faces: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997616/gpt_generated.stl')
