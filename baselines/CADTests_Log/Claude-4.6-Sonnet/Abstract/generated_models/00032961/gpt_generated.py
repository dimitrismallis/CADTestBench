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
        rect_length = 90.0      # length of the straight rectangular portion
        width = 30.0            # width of the plate (also diameter of semicircles)
        radius = width / 2.0    # semicircle radius = 15
        thickness = 5.0         # extrusion thickness
        hole_diameter = 10.0    # diameter of mounting holes
        # Hole centers placed at the center of each semicircle end
        hole_offset = (rect_length / 2.0)  # distance from center to hole center = 45
    
        # Total bounding length = rect_length + 2 * radius = 90 + 30 = 120
        total_length = rect_length + 2 * radius  # 120
    
        # --- Step 1: Sketch the stadium profile (long rect + two semicircular ends) ---
        # Build the profile as a closed wire:
        # The shape is symmetric about origin.
        # Straight sides run along Y, semicircles cap the +X and -X ends.
        # We'll orient the long axis along X.
        #
        # Profile points (going clockwise from top-left):
        # - Line from (-rect_length/2, +radius) to (+rect_length/2, +radius)  [top edge]
        # - Semicircle from (+rect_length/2, +radius) around (+rect_length/2, 0) to (+rect_length/2, -radius)  [right cap]
        # - Line from (+rect_length/2, -radius) to (-rect_length/2, -radius)  [bottom edge]
        # - Semicircle from (-rect_length/2, -radius) around (-rect_length/2, 0) to (-rect_length/2, +radius)  [left cap]
    
        half_l = rect_length / 2.0  # 45
    
        profile = (
            cq.Workplane("XY")
            .moveTo(-half_l, radius)
            .lineTo(half_l, radius)
            .threePointArc((half_l + radius, 0), (half_l, -radius))
            .lineTo(-half_l, -radius)
            .threePointArc((-half_l - radius, 0), (-half_l, radius))
            .close()
        )
    
        # --- Step 2: Extrude the profile ---
        result = profile.extrude(thickness)
    
        # --- Step 3: Add two mounting holes near each semicircular end ---
        # Hole centers at (±hole_offset, 0) on the top face
        result = (
            result
            .faces(">Z")
            .workplane()
            .pushPoints([(hole_offset, 0), (-hole_offset, 0)])
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - total_length) < TOL, \
            f"X length: expected {total_length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, \
            f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, \
            f"Z thickness: expected {thickness}, got {bb.zlen}"
    
        # Symmetry: center of bounding box should be near origin in X and Y
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X should be ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y should be ~0, got {center.y}"
        assert abs(center.z - thickness / 2.0) < TOL, \
            f"Center Z should be ~{thickness/2.0}, got {center.z}"
    
        # Cylindrical faces: 2 holes (each hole has 1 cylindrical face) + 2 semicircular end caps
        # Each hole contributes 1 cylindrical face; each semicircular end contributes 1 cylindrical face
        # Total cylindrical faces = 2 (holes) + 2 (end caps) = 4
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces: expected 4, got {cyl_faces}"
    
        # Volume check:
        # Stadium area = rect_length * width + pi * radius^2
        stadium_area = rect_length * width + math.pi * radius ** 2
        hole_area = 2 * math.pi * (hole_diameter / 2.0) ** 2
        expected_vol = (stadium_area - hole_area) * thickness
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Two holes: verify points inside holes are NOT inside the solid
        # Check that the center of each hole (at mid-thickness) is empty
        solid = result.val()
        hole1_center = (hole_offset, 0, thickness / 2.0)
        hole2_center = (-hole_offset, 0, thickness / 2.0)
        assert not solid.isInside(hole1_center), \
            f"Point {hole1_center} should be inside hole (not solid)"
        assert not solid.isInside(hole2_center), \
            f"Point {hole2_center} should be inside hole (not solid)"
    
        # Verify a point in the solid body is inside
        body_point = (0, 0, thickness / 2.0)
        assert solid.isInside(body_point), \
            f"Point {body_point} should be inside the solid body"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00032961/gpt_generated.stl')
