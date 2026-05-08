import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 80.0   # longer side (X)
        width  = 40.0   # shorter side (Y)
        height = 20.0   # extrusion height (Z)
        radius = 15.0   # semi-circle radius
    
        # --- Step 1: Create the base rectangular box ---
        # Box centered at origin: X in [-40, 40], Y in [-20, 20], Z in [0, 20]
        result = cq.Workplane("XY").box(length, width, height, centered=(True, True, False))
    
        # --- Step 2: Create the semi-circular cutout ---
        # The flat edge of the semi-circle lies on the longer side (front face, Y = -width/2 = -20).
        # The semi-circle is centered at (0, -20) on the top face workplane,
        # with the flat edge along Y = -20 and the arc extending inward (+Y direction).
        # We draw the semi-circle profile on the top face and cut downward through the solid.
    
        result = (
            result
            .faces(">Z")          # select top face
            .workplane()          # set workplane on top face
            # Draw the semi-circle: flat edge at y = -width/2 (front), arc going inward
            # In workplane coords: center at (0, -width/2), flat edge at y = -width/2
            # Semi-circle: start at (-radius, -width/2), arc through (0, -width/2 + radius), end at (radius, -width/2)
            .moveTo(-radius, -width / 2)
            .lineTo(radius, -width / 2)
            .threePointArc((0, -width / 2 + radius), (-radius, -width / 2))
            .close()
            .cutBlind(-height)    # cut downward through the full height
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box: should still be 80 x 40 x 20 (cutout doesn't change outer bounds)
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2. Volume: box minus half-cylinder
        box_vol        = length * width * height
        half_cyl_vol   = 0.5 * math.pi * radius**2 * height
        expected_vol   = box_vol - half_cyl_vol
        actual_vol     = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical face: the semi-circular cutout should produce exactly one cylindrical face
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 4. The cutout should be open at the front face (Y = -20):
        #    A point inside the semi-cylinder region should be OUTSIDE the solid
        test_point_outside = (0, -width / 2 + radius / 2, height / 2)  # inside semi-circle, mid-height
        assert not result.val().isInside(test_point_outside), \
            f"Point {test_point_outside} should be outside (in cutout) but is inside"
    
        # 5. A point in the rectangular body away from the cutout should be INSIDE
        test_point_inside = (length / 4, width / 4, height / 2)
        assert result.val().isInside(test_point_inside), \
            f"Point {test_point_inside} should be inside the solid but is not"
    
        # 6. The flat edge of the semi-circle is on the front face (Y = -20):
        #    Check that there is a planar face at Y = -width/2 (front face)
        front_faces = result.faces("<Y").size()
        assert front_faces >= 1, f"Front face(s) at min Y: expected >= 1, got {front_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00995759/gpt_generated.stl')
