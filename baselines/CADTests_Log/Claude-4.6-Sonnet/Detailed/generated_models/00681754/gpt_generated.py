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
        block_length = 1.09115
        block_width  = 1.5
        block_height = 0.361568
        cyl_diameter = 0.427203
        cyl_radius   = cyl_diameter / 2.0   # 0.2136015
        cyl_height   = 0.271176
    
        # --- Step 1: Create the rectangular block centered at origin ---
        result = cq.Workplane("XY").rect(block_length, block_width).extrude(block_height)
    
        # --- Step 2: On the top face, sketch a circle at center and extrude upward ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        total_height = block_height + cyl_height  # 0.632744
    
        assert abs(bb.xlen - block_length) < TOL, \
            f"BBox X: expected {block_length}, got {bb.xlen}"
        assert abs(bb.ylen - block_width) < TOL, \
            f"BBox Y: expected {block_width}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"BBox Z: expected {total_height}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"BBox zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, \
            f"BBox zmax: expected {total_height}, got {bb.zmax}"
    
        # Volume check
        block_vol = block_length * block_width * block_height
        cyl_vol   = math.pi * cyl_radius**2 * cyl_height
        expected_vol = block_vol + cyl_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-3, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical face check — the cylinder side wall
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Cylindrical faces: expected at least 1, got {cyl_faces}"
    
        # Planar face count:
        # Block contributes: bottom (1) + 4 sides (4) + top annular ring (1) = 6
        # Cylinder contributes: top cap (1) = 1
        # Total planar faces = 7
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 7, \
            f"Planar faces: expected 7, got {planar_faces}"
    
        # Total face count: 7 planar + 1 cylindrical = 8
        total_faces = result.faces().size()
        assert total_faces == 8, \
            f"Total faces: expected 8, got {total_faces}"
    
        # Center of mass should be near X=0, Y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y}"
    
        # The cylinder top face should be at z = total_height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_height) < TOL, \
            f"Top face Z center: expected {total_height}, got {top_face_z}"
    
        # Check that a point inside the cylinder (above block top) is inside the solid
        test_point_inside = (0.0, 0.0, block_height + cyl_height / 2.0)
        assert result.val().isInside(test_point_inside), \
            f"Point {test_point_inside} should be inside the solid (cylinder region)"
    
        # Check that a point outside the cylinder but above the block is NOT inside
        test_point_outside = (block_length / 2.0 - 0.01, 0.0, block_height + cyl_height / 2.0)
        assert not result.val().isInside(test_point_outside), \
            f"Point {test_point_outside} should be outside the solid (outside cylinder)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681754/gpt_generated.stl')
