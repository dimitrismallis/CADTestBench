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
        length = 100.0   # along X
        width  = 30.0    # along Y
        height = 20.0    # along Z
        semi_r = 10.0    # semi-circle radius (fits within width=30)
    
        # --- Step 1: Create the long rectangular prism ---
        # Centered at origin: X in [-50,50], Y in [-15,15], Z in [-10,10]
        prism = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Cut a semi-circle along the length (X-axis) ---
        # The semi-circle profile is on the YZ plane.
        # We draw the profile on the YZ plane (perpendicular to X),
        # then extrude/cut it through the full length along X.
        #
        # Profile: a semi-circle on the top of the cross-section.
        # The cross-section is Y in [-15,15], Z in [-10,10].
        # Semi-circle: center at (Y=0, Z=10) [top center], radius=10,
        # opening downward (into the prism).
        #
        # We build the cutter as a cylinder (half) oriented along X.
        # Use a full cylinder and intersect, or build the profile directly.
        #
        # Approach: On the "right" face (YZ plane at X=50), draw the
        # semi-circle profile and cut through all along -X direction.
        #
        # Profile wire on YZ plane:
        #   - Start at (Y=-10, Z=10), arc through (Y=0, Z=0) to (Y=10, Z=10)
        #     Wait — that's a semi-circle opening downward with center at (0,10).
        #   - Actually center at Z=10 (top), radius=10, arc goes from
        #     (Y=-10, Z=10) down through (Y=0, Z=0) up to (Y=10, Z=10).
        #   - Then close with a line from (Y=10,Z=10) to (Y=-10,Z=10).
        #
        # In the YZ workplane, local coords are (u=Y, v=Z).
        # Center of arc at (u=0, v=10), radius=10.
        # Arc from (-10, 10) through (0, 0) to (10, 10) — semi-circle below center.
    
        cutter = (
            cq.Workplane("YZ")          # workplane on YZ, X is the extrusion axis
            .moveTo(-semi_r, height/2)  # start at (-10, 10) in (Y,Z)
            .threePointArc((0, height/2 - semi_r), (semi_r, height/2))  # arc through (0,0) to (10,10)
            .close()                    # line back from (10,10) to (-10,10)
            .extrude(length, both=True) # extrude along X through full length
        )
    
        # --- Step 3: Subtract the cutter from the prism ---
        result = prism.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.5  # slightly relaxed for curved geometry
    
        # Bounding box: X stays [-50,50], Y stays [-15,15], Z: bottom at -10,
        # top is now cut — the top flat parts remain at Z=10 but the center is removed.
        # The overall bounding box Z should still be from -10 to 10 (the flat sides remain).
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # Prism volume = 100 * 30 * 20 = 60000
        # Semi-cylinder volume = (1/2) * pi * r^2 * L = 0.5 * pi * 100 * 100 = 15707.96
        prism_vol    = length * width * height
        semicyl_vol  = 0.5 * math.pi * semi_r**2 * length
        expected_vol = prism_vol - semicyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The semi-circle cut should create a cylindrical face along the length
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check that a point inside the semi-circle cut is NOT inside the solid
        # Semi-circle center at (X=0, Y=0, Z=10), going down to Z=0.
        # Point at (0, 0, 5) should be inside the cut (outside the solid).
        solid_shape = result.val()
        point_in_cut = (0, 0, 5)
        assert not solid_shape.isInside(point_in_cut), \
            f"Point {point_in_cut} should be in the cut-out region, not inside the solid"
    
        # Check that a point in the solid body is inside
        point_in_solid = (0, 0, -5)  # bottom half, well inside
        assert solid_shape.isInside(point_in_solid), \
            f"Point {point_in_solid} should be inside the solid"
    
        # Check that a corner point of the original prism is still solid
        point_corner = (40, 10, 8)  # near top corner, away from semi-circle
        assert solid_shape.isInside(point_corner), \
            f"Point {point_corner} should be inside the solid (corner region)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00006892/gpt_generated.stl')
