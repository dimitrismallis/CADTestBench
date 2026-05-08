import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a rectangular prism centered at the origin ---
        length = 0.19091
        width  = 0.01705
        height = 0.75
    
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Center at origin
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Volume check
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Bounding box min/max symmetry (centered at origin)
        assert abs(bb.xmin + bb.xmax) < TOL, f"X not centered: xmin={bb.xmin}, xmax={bb.xmax}"
        assert abs(bb.ymin + bb.ymax) < TOL, f"Y not centered: ymin={bb.ymin}, ymax={bb.ymax}"
        assert abs(bb.zmin + bb.zmax) < TOL, f"Z not centered: zmin={bb.zmin}, zmax={bb.zmax}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00007258/gpt_generated.stl')
