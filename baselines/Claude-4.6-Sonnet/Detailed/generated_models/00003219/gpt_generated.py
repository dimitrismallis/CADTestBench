import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        height = 1.23718
        radius = 0.27226
    
        # --- Step 1: Create the cylinder ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        diameter = 2 * radius
        assert abs(bb.xlen - diameter) < TOL, f"X extent: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y extent: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check: V = pi * r^2 * h
        expected_vol = math.pi * radius**2 * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 1 cylindrical face + 2 flat circular caps = 3 faces
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Cylindrical face check
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Flat (planar) face check: top and bottom caps
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Circular edge check: 2 circular edges (top and bottom rims)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # Center of mass should be at origin (cylinder is centered)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00003219/gpt_generated.stl')
