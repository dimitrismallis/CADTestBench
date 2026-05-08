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
        # Vertical section: tall part of L
        v_height = 60.0   # total height of vertical section
        v_width  = 20.0   # width of vertical section
    
        # Horizontal section: short arm of L
        h_width  = 40.0   # how far the horizontal arm extends (from right edge of vertical)
        h_height = 15.0   # height of horizontal arm (significantly smaller than v_height)
    
        # Extrusion depth
        depth = 10.0
    
        # Curve sag on the right side of the vertical section
        # The right edge of the vertical section bows outward (in +X) by `sag` mm
        sag = 5.0
    
        # --- Step 1: Build the L-shaped profile as a closed wire ---
        # Corners of the L, starting at bottom-left (0,0), going CCW:
        #
        #  (0, v_height) ---- (v_width, v_height)
        #       |                     |  <- curved right edge of vertical (bows outward in +X)
        #       |                     |
        #  (0, h_height)  (v_width, h_height) --- (v_width + h_width, h_height)
        #       |                                          |
        #  (0, 0) -------------------------------- (v_width + h_width, 0)
        #
        # The right edge of the vertical section uses threePointArc with an explicit
        # midpoint at (v_width + sag, mid_y) to bow outward in +X.
    
        mid_y = (h_height + v_height) / 2.0  # midpoint Y of the curved edge
        arc_mid = (v_width + sag, mid_y)      # arc midpoint bowing outward in +X
    
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)                                          # bottom-left corner
            .lineTo(v_width + h_width, 0)                         # bottom-right of horizontal arm
            .lineTo(v_width + h_width, h_height)                  # top-right of horizontal arm
            .lineTo(v_width, h_height)                            # inner corner of L (right side)
            # Go up the right side of the vertical section with a curve bowing outward (+X)
            .threePointArc(arc_mid, (v_width, v_height))          # curved right edge of vertical
            .lineTo(0, v_height)                                   # top-left corner
            .close()                                               # back to (0,0)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance due to curved face
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X: from 0 to v_width + h_width (horizontal arm dominates xmax since arc bows to v_width+sag=25,
        #    but horizontal arm goes to v_width + h_width = 60)
        expected_xmax = v_width + h_width  # = 60, horizontal arm is wider than arc bow
        assert abs(bb.xmin - 0) < TOL, f"xmin expected ~0, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax expected ~{expected_xmax}, got {bb.xmax}"
        assert abs(bb.xlen - expected_xmax) < TOL, f"xlen expected ~{expected_xmax}, got {bb.xlen}"
    
        # Y: from 0 to v_height
        assert abs(bb.ymin - 0) < TOL, f"ymin expected ~0, got {bb.ymin}"
        assert abs(bb.ymax - v_height) < TOL, f"ymax expected ~{v_height}, got {bb.ymax}"
        assert abs(bb.ylen - v_height) < TOL, f"ylen expected ~{v_height}, got {bb.ylen}"
    
        # Z: from 0 to depth
        assert abs(bb.zmin - 0) < TOL, f"zmin expected ~0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, f"zmax expected ~{depth}, got {bb.zmax}"
        assert abs(bb.zlen - depth) < TOL, f"zlen expected ~{depth}, got {bb.zlen}"
    
        # Volume check: L-shape area * depth
        # L area = vertical rect + horizontal rect + arc extra area
        v_rect_area = v_width * v_height
        h_rect_area = h_width * h_height
        # Arc adds area: for a circular arc with sagitta sag over chord (v_height - h_height),
        # extra area ≈ (2/3) * sag * chord
        chord = v_height - h_height
        arc_extra = (2.0 / 3.0) * sag * chord
        approx_area = v_rect_area + h_rect_area + arc_extra
        approx_vol = approx_area * depth
        actual_vol = solid.Volume()
        # Allow 15% tolerance for arc approximation
        assert abs(actual_vol - approx_vol) / approx_vol < 0.15, \
            f"Volume: expected ~{approx_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count: L-shape extruded
        # Faces: bottom(1) + top(1) + side faces (left vertical, top horizontal,
        #        curved right vertical, inner step horizontal, right horizontal, bottom horizontal)
        # Total planar faces = 7, curved = 1 → total = 8
        n_faces = result.faces().size()
        assert n_faces >= 7, f"Expected at least 7 faces, got {n_faces}"
    
        # Check there is exactly 1 cylindrical (curved) face
        n_cyl = result.faces("%Cylinder").size()
        assert n_cyl == 1, f"Expected 1 cylindrical face (curved side), got {n_cyl}"
    
        # Verify the L-shape: a point inside the vertical section should be inside the solid
        pt_vertical = cq.Vector(v_width / 2, v_height / 2, depth / 2)
        assert solid.isInside(pt_vertical), \
            f"Point in vertical section should be inside solid"
    
        # Verify the L-shape: a point inside the horizontal arm should be inside the solid
        pt_horizontal = cq.Vector(v_width + h_width / 2, h_height / 2, depth / 2)
        assert solid.isInside(pt_horizontal), \
            f"Point in horizontal arm should be inside solid"
    
        # Verify the L-shape: a point in the "missing" upper-right quadrant should be OUTSIDE
        pt_outside = cq.Vector(v_width + h_width / 2, v_height / 2, depth / 2)
        assert not solid.isInside(pt_outside), \
            f"Point in upper-right void should be OUTSIDE the L-shape"
    
        # Horizontal section is significantly smaller than vertical: h_height << v_height
        assert h_height < v_height * 0.5, \
            f"Horizontal height {h_height} should be < half of vertical height {v_height}"
    
        # The arc bows outward: check a point near the arc midpoint is inside the solid
        pt_arc_region = cq.Vector(v_width + sag * 0.8, mid_y, depth / 2)
        assert solid.isInside(pt_arc_region), \
            f"Point near arc bulge at {pt_arc_region} should be inside solid"
    
        print("All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} mm³")
        print(f"Faces: {n_faces}, Cylindrical faces: {n_cyl}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00995733/gpt_generated.stl')
