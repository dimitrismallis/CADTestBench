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
        rect_w = 0.399631   # rectangle width (long dimension)
        rect_h = 0.091591   # rectangle height (short dimension)
        extrude_d = 0.133054  # extrusion depth
    
        semi_hex_len = (2.0 / 3.0) * rect_w   # 2/3 of rectangle length = 0.266421
        semi_hex_max_w = 0.188808              # max protrusion width
    
        # --- Step 1: Build the combined 2D profile ---
        # Rectangle occupies x: [0, rect_w], y: [0, rect_h]
        # Semi-hexagonal section attached to the bottom edge (y=0),
        # starting at x=0, extending to x=semi_hex_len, protruding downward (y < 0).
        #
        # Semi-hexagon vertices (trapezoid-style half-hex, 4 points on non-base sides):
        # P0 = (0, 0)                                  <- shared with rect corner
        # P1 = (semi_hex_len/4, -semi_hex_max_w)       <- first angled point
        # P2 = (3*semi_hex_len/4, -semi_hex_max_w)     <- second angled point (top of semi-hex)
        # P3 = (semi_hex_len, 0)                       <- end of semi-hex base, on rect bottom edge
        #
        # Full profile (counter-clockwise):
        # Start at (0, 0), go along semi-hex downward, come back up to (semi_hex_len, 0),
        # continue along bottom edge to (rect_w, 0), up to (rect_w, rect_h),
        # across top to (0, rect_h), back down to (0, 0).
    
        p0 = (0.0, 0.0)
        p1 = (semi_hex_len / 4.0, -semi_hex_max_w)
        p2 = (3.0 * semi_hex_len / 4.0, -semi_hex_max_w)
        p3 = (semi_hex_len, 0.0)
        p4 = (rect_w, 0.0)
        p5 = (rect_w, rect_h)
        p6 = (0.0, rect_h)
    
        # Build the profile using CadQuery's polyline
        result = (
            cq.Workplane("XY")
            .moveTo(p0[0], p0[1])
            .lineTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .lineTo(p3[0], p3[1])
            .lineTo(p4[0], p4[1])
            .lineTo(p5[0], p5[1])
            .lineTo(p6[0], p6[1])
            .close()
            .extrude(extrude_d)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_xlen = rect_w
        expected_ylen = rect_h + semi_hex_max_w  # rect_h upward + semi_hex_max_w downward
        expected_zlen = extrude_d
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Bounding box extents
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0.0, got {bb.xmin:.6f}"
        assert abs(bb.xmax - rect_w) < TOL, f"xmax: expected {rect_w:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.ymin - (-semi_hex_max_w)) < TOL, \
            f"ymin: expected {-semi_hex_max_w:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - rect_h) < TOL, \
            f"ymax: expected {rect_h:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0.0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - extrude_d) < TOL, \
            f"zmax: expected {extrude_d:.6f}, got {bb.zmax:.6f}"
    
        # Volume check
        # Rectangle area = rect_w * rect_h
        # Semi-hex (trapezoid) area = 0.5 * (base1 + base2) * height
        #   base1 = semi_hex_len (bottom base at y=0)
        #   base2 = 3*semi_hex_len/4 - semi_hex_len/4 = semi_hex_len/2 (top flat edge)
        #   height = semi_hex_max_w
        rect_area = rect_w * rect_h
        semi_hex_base1 = semi_hex_len
        semi_hex_base2 = semi_hex_len / 2.0  # top edge from p1 to p2
        semi_hex_area = 0.5 * (semi_hex_base1 + semi_hex_base2) * semi_hex_max_w
        total_area = rect_area + semi_hex_area
        expected_vol = total_area * extrude_d
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: extruded polygon with 7 edges → 2 flat faces (top/bottom) + 7 side faces = 9
        face_count = result.faces().size()
        assert face_count == 9, f"Face count: expected 9, got {face_count}"
    
        # Check that the semi-hex protrusion exists (point inside the semi-hex region)
        mid_semi_hex_x = semi_hex_len / 2.0
        mid_semi_hex_y = -semi_hex_max_w / 2.0
        mid_z = extrude_d / 2.0
        assert result.val().isInside(
            cq.Vector(mid_semi_hex_x, mid_semi_hex_y, mid_z)
        ), "Point inside semi-hex region should be inside the solid"
    
        # Check that a point outside the semi-hex (beyond its length) is NOT inside
        outside_x = semi_hex_len + 0.01
        outside_y = -semi_hex_max_w / 2.0
        assert not result.val().isInside(
            cq.Vector(outside_x, outside_y, mid_z)
        ), "Point outside semi-hex region should NOT be inside the solid"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996368/gpt_generated.stl')
