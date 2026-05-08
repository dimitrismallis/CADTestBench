import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        radius = 5.0      # mm
        height = 500.0    # mm — "very long"
    
        # --- Step 1: Create the long cylinder centered at origin along Z axis ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - 2 * radius) < TOL, f"X extent: expected {2*radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * radius) < TOL, f"Y extent: expected {2*radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Centered at origin
        center = solid.Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Volume check: π * r² * h
        expected_vol = math.pi * radius**2 * height
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: 1 curved cylindrical face + 2 flat circular caps = 3
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Exactly 1 cylindrical face
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Exactly 2 planar (circular cap) faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Top and bottom caps at correct Z positions
        top_z = result.faces(">Z").val().Center().z
        bot_z = result.faces("<Z").val().Center().z
        assert abs(top_z - height / 2) < TOL, f"Top cap Z: expected {height/2}, got {top_z}"
        assert abs(bot_z + height / 2) < TOL, f"Bottom cap Z: expected {-height/2}, got {bot_z}"
    
        # Circular edges: 2 (one per cap)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00001411/gpt_generated.stl')
