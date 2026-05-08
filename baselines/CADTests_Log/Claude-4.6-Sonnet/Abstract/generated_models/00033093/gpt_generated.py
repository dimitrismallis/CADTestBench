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
        plate_length = 80.0   # X dimension
        plate_width  = 40.0   # Y dimension
        plate_height = 5.0    # Z dimension (thickness)
        hole_diameter = 6.0   # diameter of each circular cutout
        hole_radius   = hole_diameter / 2.0
        hole_offset_x = 15.0  # symmetric offset from centerline along X
        hole_offset_y = 0.0   # centered along Y
    
        # --- Step 1: Sketch rectangle and extrude to form the base plate ---
        result = (
            cq.Workplane("XY")
            .rect(plate_length, plate_width)
            .extrude(plate_height)
        )
    
        # --- Step 2: Cut two symmetric circular holes through the plate ---
        # Place holes at (+hole_offset_x, 0) and (-hole_offset_x, 0)
        result = (
            result
            .faces(">Z")
            .workplane()
            .pushPoints([
                ( hole_offset_x, hole_offset_y),
                (-hole_offset_x, hole_offset_y)
            ])
            .hole(hole_diameter)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - plate_length) < TOL, \
            f"X length: expected {plate_length}, got {bb.xlen}"
        assert abs(bb.ylen - plate_width) < TOL, \
            f"Y length: expected {plate_width}, got {bb.ylen}"
        assert abs(bb.zlen - plate_height) < TOL, \
            f"Z height: expected {plate_height}, got {bb.zlen}"
    
        # 2. Volume check: plate volume minus two cylindrical holes
        plate_vol = plate_length * plate_width * plate_height
        hole_vol  = 2 * math.pi * hole_radius**2 * plate_height
        expected_vol = plate_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: exactly 2 (one per hole)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical faces: expected 2, got {cyl_face_count}"
    
        # 4. Circular edges: 4 total (top + bottom rim for each of 2 holes)
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, \
            f"Circular edges: expected 4, got {circ_edge_count}"
    
        # 5. Symmetry: center of mass should be at (0, 0, plate_height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - plate_height / 2.0) < TOL, \
            f"Center of mass Z: expected {plate_height/2.0}, got {com.z}"
    
        # 6. Holes are through-holes: verify points inside hole cylinders are NOT inside solid
        # Check a point at the center of each hole (midway through thickness)
        mid_z = plate_height / 2.0
        point_in_hole_pos = (hole_offset_x, hole_offset_y, mid_z)
        point_in_hole_neg = (-hole_offset_x, hole_offset_y, mid_z)
        assert not result.val().isInside(point_in_hole_pos), \
            f"Point {point_in_hole_pos} should be inside a hole (not solid), but isInside returned True"
        assert not result.val().isInside(point_in_hole_neg), \
            f"Point {point_in_hole_neg} should be inside a hole (not solid), but isInside returned True"
    
        # 7. A point in the solid body (away from holes) should be inside
        point_in_solid = (plate_length/2.0 - 5.0, plate_width/2.0 - 5.0, mid_z)
        assert result.val().isInside(point_in_solid), \
            f"Point {point_in_solid} should be inside the solid, but isInside returned False"
    
        # 8. Planar faces: 2 (top + bottom) + 4 sides = 6 planar faces total
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, \
            f"Planar faces: expected 6, got {planar_face_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00033093/gpt_generated.stl')
