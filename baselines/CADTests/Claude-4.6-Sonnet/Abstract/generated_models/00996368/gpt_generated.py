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
        L = 60.0    # length of rectangle (longer edge)
        W = 30.0    # width of rectangle (shorter edge)
        H = 10.0    # extrusion height
    
        # Semi-hexagon: length = 2/3 * L = 40
        semi_hex_len = (2.0 / 3.0) * L  # = 40.0
        # For a regular hexagon with side s, the base spans 2s
        # So 2s = semi_hex_len => s = 20
        s = semi_hex_len / 2.0  # = 20.0
        # Height of semi-hexagon = s * sqrt(3) / 2 * 2 = s * sqrt(3)
        # Actually for a regular hexagon, the distance from center to flat side = s*sqrt(3)/2
        # The semi-hexagon height (from base to apex row) = s * sqrt(3)/2
        hex_h = s * math.sqrt(3) / 2.0  # height of semi-hexagon
    
        # --- Step 1: Build the 2D profile as a closed wire ---
        # The profile lies in the XY plane.
        # Rectangle occupies: x in [0, L], y in [-W, 0]
        # Semi-hexagon occupies: x in [0, semi_hex_len], y in [0, hex_h]
        # Semi-hexagon starts at one end (x=0) of the rectangle's longer edge (y=0)
    
        # Semi-hexagon vertices (regular hexagon, top half):
        # With side s=20, base from x=0 to x=40:
        # (0, 0) -> (s/2, hex_h) -> (3*s/2, hex_h) -> (2*s, 0)
        # = (0,0) -> (10, 10√3) -> (30, 10√3) -> (40, 0)
    
        # Full closed profile (counter-clockwise):
        # Start at (0, 0), go along semi-hex, then rectangle perimeter back
    
        pts = [
            (0.0, 0.0),                    # start / junction left
            (s / 2.0, hex_h),              # semi-hex upper-left vertex
            (3.0 * s / 2.0, hex_h),        # semi-hex upper-right vertex
            (semi_hex_len, 0.0),           # junction right of semi-hex
            (L, 0.0),                      # rectangle top-right
            (L, -W),                       # rectangle bottom-right
            (0.0, -W),                     # rectangle bottom-left
        ]
        # Close back to (0, 0)
    
        # --- Step 2: Create the profile using CadQuery ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .close()
            .extrude(H)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - L) < TOL, f"X length: expected {L}, got {bb.xlen}"
        assert abs(bb.ylen - (W + hex_h)) < TOL, f"Y length: expected {W + hex_h:.4f}, got {bb.ylen:.4f}"
        assert abs(bb.zlen - H) < TOL, f"Z length: expected {H}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.xmax - L) < TOL, f"xmax: expected {L}, got {bb.xmax}"
        assert abs(bb.ymin - (-W)) < TOL, f"ymin: expected {-W}, got {bb.ymin}"
        assert abs(bb.ymax - hex_h) < TOL, f"ymax: expected {hex_h:.4f}, got {bb.ymax:.4f}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - H) < TOL, f"zmax: expected {H}, got {bb.zmax}"
    
        # Volume check
        # Area of cross-section = rectangle area + semi-hexagon area
        rect_area = L * W  # 60 * 30 = 1800
        # Semi-hexagon area = (3 * sqrt(3) / 4) * s^2 (half of regular hexagon)
        semi_hex_area = (3.0 * math.sqrt(3) / 4.0) * (s ** 2)  # = 3*sqrt(3)/4 * 400
        total_area = rect_area + semi_hex_area
        expected_vol = total_area * H
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: the extruded profile should have:
        # 2 flat end faces (top and bottom) + 7 side faces (one per edge of the profile)
        # Total = 9 faces
        face_count = result.faces().size()
        assert face_count == 9, f"Face count: expected 9, got {face_count}"
    
        # Check the semi-hexagon region: a point inside the semi-hex area should be inside the solid
        # Point at (10, hex_h/2, H/2) should be inside
        test_pt_inside = cq.Vector(10.0, hex_h / 2.0, H / 2.0)
        assert result.val().isInside(test_pt_inside), \
            f"Point {test_pt_inside} should be inside the solid (semi-hex region)"
    
        # Point outside the semi-hex (beyond x=40 in the semi-hex y region) should be outside
        test_pt_outside = cq.Vector(50.0, hex_h / 2.0, H / 2.0)
        assert not result.val().isInside(test_pt_outside), \
            f"Point {test_pt_outside} should be outside the solid"
    
        # Point inside the rectangle region
        test_pt_rect = cq.Vector(50.0, -W / 2.0, H / 2.0)
        assert result.val().isInside(test_pt_rect), \
            f"Point {test_pt_rect} should be inside the solid (rectangle region)"
    
        print(f"All assertions passed!")
        print(f"Rectangle: {L} x {W}, Semi-hex side: {s}, Semi-hex height: {hex_h:.4f}")
        print(f"Bounding box: {bb.xlen} x {bb.ylen:.4f} x {bb.zlen}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00996368/gpt_generated.stl')
