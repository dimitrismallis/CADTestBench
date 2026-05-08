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
        outer_radius = 20.0
        inner_radius = 10.0
        height       = 15.0
    
        # --- Step 1: Draw the outer circle on the XY plane ---
        # --- Step 2: Subtract the inner circle to form the annulus profile ---
        # --- Step 3: Extrude the annulus profile to create a 3D ring/tube ---
        result = (
            cq.Workplane("XY")
            .circle(outer_radius)          # outer circle
            .circle(inner_radius)          # inner circle (creates a hole in the profile)
            .extrude(height)               # extrude the annular region
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # 2. Volume check: annulus volume = π * (R_outer² - R_inner²) * h
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count: 4 faces total
        #    - 1 outer cylindrical face
        #    - 1 inner cylindrical face
        #    - 1 top flat annular face
        #    - 1 bottom flat annular face
        face_count = result.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4, got {face_count}"
    
        # 4. Cylindrical faces: exactly 2 (inner wall and outer wall)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # 5. Planar faces: exactly 2 (top and bottom annular faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # 6. Circular edges: 4 total
        #    - 2 on top face (outer and inner circles)
        #    - 2 on bottom face (outer and inner circles)
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 4, \
            f"Circular edge count: expected 4, got {circ_edge_count}"
    
        # 7. Symmetry: center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # 8. The inner bore should be hollow: a point on the axis inside the tube
        #    should NOT be inside the solid
        inner_point = (0.0, 0.0, height / 2)
        assert not result.val().isInside(inner_point), \
            f"Inner bore should be hollow: point {inner_point} should not be inside the solid"
    
        # 9. A point in the annular wall should be inside the solid
        mid_radius = (outer_radius + inner_radius) / 2.0
        wall_point = (mid_radius, 0.0, height / 2)
        assert result.val().isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00003801/gpt_generated.stl')
