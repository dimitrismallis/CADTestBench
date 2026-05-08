import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a long cylinder (radius=10, height=100) ---
        radius = 10.0
        height = 100.0
    
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * radius) < TOL, f"X extent: expected {2*radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * radius) < TOL, f"Y extent: expected {2*radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Center of mass should be at origin (cylinder is centered)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Volume check: V = pi * r^2 * h
        expected_vol = math.pi * radius**2 * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Face count: 1 curved cylindrical face + 2 flat circular caps = 3
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Cylindrical face count: 1
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 1, f"Cylindrical faces: expected 1, got {cyl_face_count}"
    
        # Circular edge count: 2 (top and bottom circles)
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 2, f"Circular edges: expected 2, got {circ_edge_count}"
    
        # Top and bottom face positions
        top_z = result.faces(">Z").val().Center().z
        bot_z = result.faces("<Z").val().Center().z
        assert abs(top_z - height / 2) < TOL, f"Top face Z: expected {height/2}, got {top_z}"
        assert abs(bot_z + height / 2) < TOL, f"Bottom face Z: expected {-height/2}, got {bot_z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00003219/gpt_generated.stl')
