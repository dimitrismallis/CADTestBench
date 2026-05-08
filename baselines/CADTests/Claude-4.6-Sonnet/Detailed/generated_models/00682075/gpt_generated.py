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
        # --- Step 1: Define the staircase profile as a closed polygon ---
        # Three rectangles stacked vertically, each stepping inward:
        # Step 1 (bottom): x: 0 to 0.75, y: 0 to 0.5
        # Step 2 (middle): x: 0 to 0.50, y: 0.5 to 1.0
        # Step 3 (top):    x: 0 to 0.25, y: 1.0 to 1.5
        # Closed polygon vertices:
        pts = [
            (0.00, 0.00),
            (0.75, 0.00),
            (0.75, 0.50),
            (0.50, 0.50),
            (0.50, 1.00),
            (0.25, 1.00),
            (0.25, 1.50),
            (0.00, 1.50),
        ]
    
        # --- Step 2: Build the profile using lineTo and close ---
        profile = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .lineTo(pts[7][0], pts[7][1])
            .close()
        )
    
        # --- Step 3: Extrude the profile by 0.25 units ---
        result = profile.extrude(0.25)
    
        # --- Step 4: Translate to (0.375, -0.25, -0.020659) ---
        result = result.translate((0.375, -0.25, -0.020659))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After translation:
        # X: 0 + 0.375 = 0.375  to  0.75 + 0.375 = 1.125  → xlen = 0.75
        # Y: 0 + (-0.25) = -0.25  to  1.5 + (-0.25) = 1.25  → ylen = 1.5
        # Z: 0 + (-0.020659) = -0.020659  to  0.25 + (-0.020659) = 0.229341  → zlen = 0.25
        assert abs(bb.xlen - 0.75) < TOL, f"X length: expected 0.75, got {bb.xlen}"
        assert abs(bb.ylen - 1.50) < TOL, f"Y length: expected 1.50, got {bb.ylen}"
        assert abs(bb.zlen - 0.25) < TOL, f"Z length: expected 0.25, got {bb.zlen}"
    
        # Check bounding box position after translation
        assert abs(bb.xmin - 0.375) < TOL, f"xmin: expected 0.375, got {bb.xmin}"
        assert abs(bb.xmax - 1.125) < TOL, f"xmax: expected 1.125, got {bb.xmax}"
        assert abs(bb.ymin - (-0.25)) < TOL, f"ymin: expected -0.25, got {bb.ymin}"
        assert abs(bb.ymax - 1.25) < TOL, f"ymax: expected 1.25, got {bb.ymax}"
        assert abs(bb.zmin - (-0.020659)) < TOL, f"zmin: expected -0.020659, got {bb.zmin}"
        assert abs(bb.zmax - 0.229341) < TOL, f"zmax: expected 0.229341, got {bb.zmax}"
    
        # Volume check:
        # Profile area = 0.75*0.5 + 0.5*0.5 + 0.25*0.5 = 0.375 + 0.25 + 0.125 = 0.75
        # Volume = area * extrusion depth = 0.75 * 0.25 = 0.1875
        expected_vol = 0.75 * 0.25
        assert abs(solid.Volume() - expected_vol) < TOL, f"Volume: expected {expected_vol}, got {solid.Volume()}"
    
        # Face count: 8 profile edges → 8 side faces + 2 end faces (front/back) = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # All faces of this extruded polygon are planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, f"All faces should be planar: expected 10, got {planar_count}"
    
        # Check that the solid contains a point inside step 1 (bottom, widest)
        # Step 1 center (before translation): (0.375, 0.25, 0.125) → after: (0.75, 0.0, 0.104341)
        p1 = (0.75, 0.0, 0.104341)
        assert solid.isInside(p1), f"Point {p1} should be inside step 1"
    
        # Check that a point outside the staircase (in the cutout region) is NOT inside
        # x=0.625 > 0.5 (step 2 limit) and y=0.75 is in step 2 height range → outside
        # After translation: x=0.625+0.375=1.0, y=0.75-0.25=0.5
        p_outside = (1.0, 0.5, 0.104341)
        assert not solid.isInside(p_outside), f"Point {p_outside} should be outside (in staircase cutout)"
    
        # Check that a point inside step 2 IS inside
        # Step 2 center (before trans): (0.25, 0.75, 0.125) → after: (0.625, 0.5, 0.104341)
        p2 = (0.625, 0.5, 0.104341)
        assert solid.isInside(p2), f"Point {p2} should be inside step 2"
    
        # Check that a point inside step 3 IS inside
        # Step 3 center (before trans): (0.125, 1.25, 0.125) → after: (0.5, 1.0, 0.104341)
        p3 = (0.5, 1.0, 0.104341)
        assert solid.isInside(p3), f"Point {p3} should be inside step 3"
    
        # Check center of mass
        # Profile centroid X (before trans):
        #   Step 1: x_c=0.375, area=0.375; Step 2: x_c=0.25, area=0.25; Step 3: x_c=0.125, area=0.125
        #   x_com = (0.375*0.375 + 0.25*0.25 + 0.125*0.125) / 0.75
        #         = (0.140625 + 0.0625 + 0.015625) / 0.75 = 0.21875 / 0.75 = 0.291667
        #   After trans: 0.291667 + 0.375 = 0.666667
        # Profile centroid Y (before trans):
        #   Step 1: y_c=0.25, area=0.375; Step 2: y_c=0.75, area=0.25; Step 3: y_c=1.25, area=0.125
        #   y_com = (0.25*0.375 + 0.75*0.25 + 1.25*0.125) / 0.75
        #         = (0.09375 + 0.1875 + 0.15625) / 0.75 = 0.4375 / 0.75 = 0.583333
        #   After trans: 0.583333 - 0.25 = 0.333333
        # Z centroid: 0.125 - 0.020659 = 0.104341
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - 0.666667) < 0.01, f"CoM X: expected ~0.666667, got {com.x}"
        assert abs(com.y - 0.333333) < 0.01, f"CoM Y: expected ~0.333333, got {com.y}"
        assert abs(com.z - 0.104341) < 0.01, f"CoM Z: expected ~0.104341, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00682075/gpt_generated.stl')
