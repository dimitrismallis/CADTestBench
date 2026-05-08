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
        # --- Step 1: Create rectangular box 0.9 x 1.5 x 0.75 ---
        length = 0.9
        width = 1.5
        height = 0.75
        hole_diameter = 0.45
        hole_radius = hole_diameter / 2  # 0.225
        # Offset 0.075 units to the left (negative X)
        hole_offset_x = -0.075
        hole_offset_y = 0.0
    
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Add circular hole offset 0.075 to the left from center ---
        # Select top face, create workplane, move to hole center, drill hole through
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(hole_offset_x, hole_offset_y)
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Box is centered at origin by default, so extents are ±half in each axis
        assert abs(bb.xmin - (-length/2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - (length/2)) < TOL, f"xmax: expected {length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width/2)) < TOL, f"ymin: expected {-width/2}, got {bb.ymin}"
        assert abs(bb.ymax - (width/2)) < TOL, f"ymax: expected {width/2}, got {bb.ymax}"
        assert abs(bb.zmin - (-height/2)) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (height/2)) < TOL, f"zmax: expected {height/2}, got {bb.zmax}"
    
        # Check volume: box volume minus cylinder hole volume
        box_vol = length * width * height
        hole_vol = math.pi * (hole_radius ** 2) * height
        expected_vol = box_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there is exactly 1 cylindrical face (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check that the hole passes through the solid at the offset position
        solid = result.val()
        # Point inside the hole (should NOT be inside the solid)
        hole_center_point = (hole_offset_x, hole_offset_y, 0.0)
        assert not solid.isInside(hole_center_point), \
            f"Point at hole center {hole_center_point} should be outside (in hole), but is inside solid"
    
        # Point clearly inside the solid (far from hole, right side)
        inside_point = (0.35, 0.6, 0.0)
        assert solid.isInside(inside_point), \
            f"Point {inside_point} should be inside solid, but is outside"
    
        # Verify the hole is offset to the left: point at x=0.3 (right of center)
        # should be inside the solid (hole is at x=-0.075, not at x=0.3)
        right_of_center = (0.3, 0.0, 0.0)
        assert solid.isInside(right_of_center), \
            f"Point {right_of_center} (right of center, away from hole) should be inside solid"
    
        # Verify a point just left of hole center is outside (inside the hole)
        in_hole_left = (hole_offset_x - 0.05, hole_offset_y, 0.0)
        assert not solid.isInside(in_hole_left), \
            f"Point {in_hole_left} (inside hole) should be outside solid"
    
        # Check faces intersected by a vertical line through a solid region
        faces_through_solid = solid.facesIntersectedByLine(
            (0.35, 0.0, -1.0),
            (0, 0, 1)
        )
        assert len(faces_through_solid) >= 2, \
            f"Line through solid should intersect at least 2 faces, got {len(faces_through_solid)}"
    
        print("All assertions passed!")
        print(f"  Box: {length} x {width} x {height}")
        print(f"  Hole diameter: {hole_diameter}, offset X: {hole_offset_x}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670231/gpt_generated.stl')
