import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        LENGTH = 120.0   # long dimension (X)
        WIDTH  = 60.0    # wide dimension (Y)
        HEIGHT = 15.0    # short dimension (Z)
    
        # --- Step 1: Create the rectangular prism centered at origin ---
        result = cq.Workplane("XY").box(LENGTH, WIDTH, HEIGHT)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - LENGTH) < TOL, f"X length: expected {LENGTH}, got {bb.xlen}"
        assert abs(bb.ylen - WIDTH)  < TOL, f"Y width:  expected {WIDTH},  got {bb.ylen}"
        assert abs(bb.zlen - HEIGHT) < TOL, f"Z height: expected {HEIGHT}, got {bb.zlen}"
    
        # Bounding box extents (centered at origin)
        assert abs(bb.xmin - (-LENGTH / 2)) < TOL, f"xmin: expected {-LENGTH/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( LENGTH / 2)) < TOL, f"xmax: expected { LENGTH/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-WIDTH  / 2)) < TOL, f"ymin: expected {-WIDTH/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( WIDTH  / 2)) < TOL, f"ymax: expected { WIDTH/2},  got {bb.ymax}"
        assert abs(bb.zmin - (-HEIGHT / 2)) < TOL, f"zmin: expected {-HEIGHT/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( HEIGHT / 2)) < TOL, f"zmax: expected { HEIGHT/2}, got {bb.zmax}"
    
        # Volume check
        expected_vol = LENGTH * WIDTH * HEIGHT
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Proportions: length > width > height (long, wide, short)
        assert LENGTH > WIDTH,  f"Should be longer than wide: {LENGTH} > {WIDTH}"
        assert WIDTH  > HEIGHT, f"Should be wider than tall:  {WIDTH} > {HEIGHT}"
    
        # Center of mass should be at origin
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009863/gpt_generated.stl')
