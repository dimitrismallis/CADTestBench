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
        horiz_len = 0.024896   # horizontal section length
        vert_len  = 0.752339   # vertical section length
        thickness = 0.024896   # thickness of the L arms (same as horiz_len)
        extrude_depth = 0.018672
    
        # --- Step 1: Build the L-shaped profile ---
        # The L-shape profile (viewed from above, in XY plane):
        # We define the outline of an L:
        #   - Vertical arm: width=thickness, height=vert_len (with slight curve on outer edge)
        #   - Horizontal arm: length=horiz_len, height=thickness
        #
        # Corner at origin. The L opens to the right and upward.
        #
        # Vertices of the L (going clockwise):
        # P0 = (0, 0)                          bottom-left corner
        # P1 = (horiz_len + thickness, 0)      bottom-right of horizontal arm
        # P2 = (horiz_len + thickness, thickness)  top-right of horizontal arm
        # P3 = (thickness, thickness)          inner corner of L
        # P4 = (thickness, vert_len)           top-right of vertical arm (with curve)
        # P5 = (0, vert_len)                   top-left of vertical arm
        # back to P0
        #
        # The vertical section outer edge (P3 -> P4) uses a spline with slight curve.
    
        # Define points
        P0 = (0, 0)
        P1 = (horiz_len + thickness, 0)
        P2 = (horiz_len + thickness, thickness)
        P3 = (thickness, thickness)
        P4 = (thickness, vert_len)
        P5 = (0, vert_len)
    
        # Spline control points for the curved vertical section (right edge of vertical arm)
        # Slight curve: bulge outward (in +X direction) in the middle
        spline_pts = [
            (thickness, thickness),                          # P3
            (thickness + 0.003, thickness + vert_len * 0.33), # slight bulge
            (thickness + 0.003, thickness + vert_len * 0.66), # slight bulge
            (thickness, vert_len),                           # P4
        ]
    
        # --- Step 2: Build the closed wire using CadQuery ---
        result = (
            cq.Workplane("XY")
            .moveTo(P0[0], P0[1])
            .lineTo(P1[0], P1[1])
            .lineTo(P2[0], P2[1])
            .lineTo(P3[0], P3[1])
            .spline(spline_pts[1:], includeCurrent=True)  # from P3 through intermediate to P4
            .lineTo(P5[0], P5[1])
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: from 0 to horiz_len + thickness (spline bulge is small, within tolerance)
        expected_xlen = horiz_len + thickness
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected ~{expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y: from 0 to vert_len
        expected_ylen = vert_len
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected ~{expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z: extrude depth
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z length (extrude): expected {extrude_depth:.6f}, got {bb.zlen:.6f}"
    
        # Volume check:
        # The L-shape base area (without spline bulge) as lower bound:
        #   full rect area = (horiz_len + thickness) * vert_len
        #   missing corner = horiz_len * (vert_len - thickness)
        #   L area = full_rect - missing_corner
        full_rect_area = (horiz_len + thickness) * vert_len
        missing_corner_area = horiz_len * (vert_len - thickness)
        l_shape_area = full_rect_area - missing_corner_area
        l_shape_vol = l_shape_area * extrude_depth
    
        # Upper bound: full bounding box volume
        full_bbox_vol = (horiz_len + thickness) * vert_len * extrude_depth
    
        actual_vol = result.val().Volume()
    
        # The actual volume should be between the pure L-shape volume and the full bbox volume
        # (spline bulge adds a small amount of material to the vertical arm)
        assert actual_vol >= l_shape_vol * 0.99, \
            f"Volume too small: expected >= {l_shape_vol:.8f}, got {actual_vol:.8f}"
        assert actual_vol <= full_bbox_vol * 1.01, \
            f"Volume too large: expected <= {full_bbox_vol:.8f}, got {actual_vol:.8f}"
    
        # Check it's a single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check the object has planar top and bottom faces
        assert result.faces("|Z").size() >= 2, \
            f"Expected at least 2 faces parallel to Z (top/bottom), got {result.faces('|Z').size()}"
    
        # Check the object contains the inner corner point (should be solid there)
        inner_pt = cq.Vector(thickness * 0.5, thickness * 0.5, extrude_depth * 0.5)
        assert result.val().isInside(inner_pt), \
            f"Inner corner point should be inside the solid"
    
        # Check the missing corner is NOT inside the solid
        missing_pt = cq.Vector(horiz_len + thickness * 0.5, vert_len * 0.5, extrude_depth * 0.5)
        assert not result.val().isInside(missing_pt), \
            f"Missing corner point should NOT be inside the solid"
    
        print(f"All assertions passed!")
        print(f"BBox: x={bb.xlen:.6f}, y={bb.ylen:.6f}, z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.8f} (L-shape lower bound: {l_shape_vol:.8f}, bbox upper bound: {full_bbox_vol:.8f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00995733/gpt_generated.stl')
