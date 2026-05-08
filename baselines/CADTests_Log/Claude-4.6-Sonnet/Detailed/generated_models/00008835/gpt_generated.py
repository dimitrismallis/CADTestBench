import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side = 0.02812
        height = 0.75
    
        # --- Step 1: Create square profile and extrude ---
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-5
    
        bb = result.val().BoundingBox()
    
        # Bounding box dimensions
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side) < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Volume: side * side * height
        expected_vol = side * side * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # A rectangular prism has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # A rectangular prism has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # A rectangular prism has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # Top face at max Z should be at height
        assert abs(bb.zmax - height) < TOL, f"Top Z: expected {height}, got {bb.zmax}"
        # Bottom face at min Z should be at 0
        assert abs(bb.zmin - 0.0) < TOL, f"Bottom Z: expected 0, got {bb.zmin}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00008835/gpt_generated.stl')
