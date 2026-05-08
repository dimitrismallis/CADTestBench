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
        length = 1.5
        width  = 0.83721
        height = 0.07849
    
        # --- Step 1: Create rectangular prism centered on XY origin, base at Z=0 ---
        # centered=(True, True, False) means centered in X and Y, but starts at Z=0
        result = cq.Workplane("XY").box(length, width, height, centered=(True, True, False))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box dimensions
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Base centered on origin in XY: xmin=-length/2, xmax=+length/2, ymin=-width/2, ymax=+width/2
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2}, got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2}, got {bb.ymax}"
    
        # Base at Z=0, top at Z=height
        assert abs(bb.zmin - 0.0)    < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"zmax: expected {height}, got {bb.zmax}"
    
        # Volume check
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # A rectangular prism has exactly 6 planar faces
        face_count = result.faces("%Plane").size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # 12 edges total
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # 8 vertices total
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0)          < TOL, f"CoM X: expected 0.0, got {com.x}"
        assert abs(com.y - 0.0)          < TOL, f"CoM Y: expected 0.0, got {com.y}"
        assert abs(com.z - height / 2.0) < TOL, f"CoM Z: expected {height/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009863/gpt_generated.stl')
