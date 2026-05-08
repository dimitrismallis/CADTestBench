import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define parameters ---
        length = 0.66788   # X dimension
        width  = 0.75      # Y dimension
        height = 0.32847   # Z extrusion height
    
        # --- Step 2: Create rectangle centered at origin in XY, extrude upward ---
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Centered in XY: xmin == -length/2, xmax == length/2, etc.
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
    
        # Extrusion starts at z=0 and goes to z=height
        assert abs(bb.zmin - 0.0)    < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"zmax: expected {height}, got {bb.zmax}"
    
        # Volume check: should equal length * width * height (solid box, no holes)
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a box has 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: a box has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a box has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0)          < TOL, f"CoM x: expected 0.0, got {com.x}"
        assert abs(com.y - 0.0)          < TOL, f"CoM y: expected 0.0, got {com.y}"
        assert abs(com.z - height / 2.0) < TOL, f"CoM z: expected {height/2.0}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00006863/gpt_generated.stl')
