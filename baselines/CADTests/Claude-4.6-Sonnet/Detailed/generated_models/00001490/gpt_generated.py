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
        height = 0.48649
        radius = 0.75
        hole_diameter = 0.243243243243244
        hole_radius = hole_diameter / 2.0  # 0.121621621621622
    
        # --- Step 1: Create the outer cylinder ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Step 2: Add central through-hole ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * radius) < TOL, f"X bounding box: expected {2*radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * radius) < TOL, f"Y bounding box: expected {2*radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z bounding box: expected {height}, got {bb.zlen}"
    
        # Volume check: outer cylinder minus inner hole cylinder
        outer_vol = math.pi * radius**2 * height
        hole_vol = math.pi * hole_radius**2 * height
        expected_vol = outer_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-3, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 
        # - 1 outer cylindrical face
        # - 1 inner cylindrical face (hole)
        # - 2 flat annular faces (top and bottom)
        # Total = 4 faces
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Cylindrical faces: outer cylinder + inner hole = 2
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar faces: top annular + bottom annular = 2
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar face count: expected 2, got {planar_face_count}"
    
        # Check that the center of the solid is at origin (symmetric)
        center = result.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check that a point at the center axis is NOT inside the solid (it's a hole)
        center_point = (0, 0, 0)
        assert not result.val().isInside(center_point), \
            "Center point should be inside the hole, not the solid"
    
        # Check that a point on the outer ring IS inside the solid
        outer_point = (radius * 0.5, 0, 0)
        assert result.val().isInside(outer_point), \
            f"Point at ({outer_point}) should be inside the solid"
    
        # Check circular edges: top face has 2 circles (outer + inner), bottom face has 2 circles
        circular_edge_count = result.edges("%Circle").size()
        assert circular_edge_count == 4, f"Circular edge count: expected 4, got {circular_edge_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00001490/gpt_generated.stl')
