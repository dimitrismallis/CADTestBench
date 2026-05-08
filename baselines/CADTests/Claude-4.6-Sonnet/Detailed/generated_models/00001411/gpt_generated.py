import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define parameters ---
        height = 1.5
        radius = 0.014425
        diameter = 2 * radius  # 0.02885
    
        # --- Step 2: Create the cylinder centered at origin ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - diameter) < TOL, f"X length (diameter): expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y length (diameter): expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length (height): expected {height}, got {bb.zlen}"
    
        # Check bounding box center is at origin
        assert abs(bb.xmin + radius) < TOL, f"xmin: expected {-radius}, got {bb.xmin}"
        assert abs(bb.xmax - radius) < TOL, f"xmax: expected {radius}, got {bb.xmax}"
        assert abs(bb.ymin + radius) < TOL, f"ymin: expected {-radius}, got {bb.ymin}"
        assert abs(bb.ymax - radius) < TOL, f"ymax: expected {radius}, got {bb.ymax}"
        assert abs(bb.zmin + height/2) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - height/2) < TOL, f"zmax: expected {height/2}, got {bb.zmax}"
    
        # Check volume: V = π * r² * h
        expected_volume = math.pi * radius**2 * height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 1e-4, \
            f"Volume: expected {expected_volume:.8f}, got {actual_volume:.8f}"
    
        # Check face count: cylinder has 3 faces (top, bottom, lateral)
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Check cylindrical face exists (lateral surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check top and bottom circular edges
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 2, f"Circular edges: expected 2, got {circular_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00001411/gpt_generated.stl')
