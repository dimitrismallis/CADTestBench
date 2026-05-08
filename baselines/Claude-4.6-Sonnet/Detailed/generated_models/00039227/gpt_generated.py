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
        diameter = 1.27949
        radius = diameter / 2.0          # 0.639745
        rect_length = 0.787604
        rect_width = 0.506095
        height = 0.5                     # reasonable height for the cylinder
    
        # --- Step 1: Create the base cylinder ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Step 2: Cut a rectangular slot through the center of the cylinder ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(rect_length, rect_width)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - diameter) < TOL, f"X bounding box: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y bounding box: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z bounding box: expected {height}, got {bb.zlen}"
    
        # Check volume: cylinder volume minus rectangular prism volume
        cyl_vol = math.pi * radius**2 * height
        rect_vol = rect_length * rect_width * height
        expected_vol = cyl_vol - rect_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the rectangular cutout exists by verifying interior points are outside the solid
        solid = result.val()
        # Center of the solid should be empty (inside the rectangular cut)
        center_point = (0, 0, 0)
        assert not solid.isInside(center_point), \
            f"Center point should be outside (inside the rectangular cut), but isInside returned True"
    
        # A point inside the cylinder but outside the rectangle should be inside the solid
        # Point near the edge of cylinder, away from rectangle
        test_point = (radius * 0.8, 0, 0)  # along X axis, inside cylinder but outside rect (rect_width/2 = 0.253)
        # rect_width/2 = 0.253, so y=0 and x=0.511 is outside the rect (rect_length/2 = 0.394)
        # Actually x=0.511 > rect_length/2=0.394, so this point IS outside the rectangle
        assert solid.isInside(test_point), \
            f"Point {test_point} should be inside the solid (cylinder minus rectangle)"
    
        # Check face counts: cylinder has top, bottom (2 planar faces split by rectangle),
        # curved cylindrical face, and rectangular cut walls (2 long + 2 short sides)
        # The rectangular cut creates additional faces
        num_faces = result.faces().size()
        assert num_faces >= 6, f"Expected at least 6 faces, got {num_faces}"
    
        # Check cylindrical faces exist (the curved surface of the cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check planar faces exist
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 4, f"Expected at least 4 planar faces, got {planar_faces}"
    
        # Verify the rectangular cut dimensions by checking faces intersected by a vertical line
        # A line through the center should intersect the top and bottom faces (not blocked by solid)
        faces_hit = solid.facesIntersectedByLine((0, 0, -1), (0, 0, 1))
        # Since center is cut out, the line through center hits the cut walls or nothing
        # Let's check a line through a solid region
        faces_hit_solid = solid.facesIntersectedByLine((radius * 0.8, 0, -1), (0, 0, 1))
        assert len(faces_hit_solid) >= 2, \
            f"Line through solid region should hit at least 2 faces (top and bottom), got {len(faces_hit_solid)}"
    
        print(f"All assertions passed!")
        print(f"Cylinder diameter: {diameter}, radius: {radius}")
        print(f"Rectangle: {rect_length} x {rect_width}")
        print(f"Height: {height}")
        print(f"Volume: {actual_vol:.6f} (expected: {expected_vol:.6f})")
        print(f"Number of faces: {num_faces}")
        print(f"Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00039227/gpt_generated.stl')
