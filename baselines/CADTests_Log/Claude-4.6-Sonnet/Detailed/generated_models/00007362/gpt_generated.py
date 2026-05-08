import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a rectangular prism centered at the origin ---
        length = 0.75
        width  = 0.06429
        height = 0.03929
    
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 1e-5
    
        bb = result.val().BoundingBox()
    
        # Check bounding box dimensions
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check center is at origin
        center = result.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check bounding box min/max are symmetric about origin
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
        assert abs(bb.zmin - (-height / 2)) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( height / 2)) < TOL, f"zmax: expected { height/2}, got {bb.zmax}"
    
        # Check volume
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00007362/gpt_generated.stl')
