import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.375    # full diagonal along X
        width  = 0.11438  # full diagonal along Y
        height = 0.75     # extrusion height
    
        # --- Step 1: Define rhombus vertices ---
        # Rhombus with diagonals along X and Y axes
        half_l = length / 2   # 0.1875
        half_w = width  / 2   # 0.05719
    
        # Vertices: right, top, left, bottom
        v_right  = (half_l,  0.0)
        v_top    = (0.0,     half_w)
        v_left   = (-half_l, 0.0)
        v_bottom = (0.0,    -half_w)
    
        # --- Step 2: Build the rhombus wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(*v_right)
            .lineTo(*v_top)
            .lineTo(*v_left)
            .lineTo(*v_bottom)
            .close()
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: rhombus area = (d1 * d2) / 2
        rhombus_area = (length * width) / 2.0
        expected_vol = rhombus_area * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a rhombus prism has 6 faces (2 rhombus faces + 4 side faces)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: 4 (bottom) + 4 (top) + 4 (vertical) = 12
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: 4 (bottom) + 4 (top) = 8
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # Check that a point inside the rhombus body is inside the solid
        inside_pt = (0.0, 0.0, height / 2)
        assert result.val().isInside(inside_pt), f"Point {inside_pt} should be inside the solid"
    
        # Check that a corner point outside the rhombus is NOT inside
        outside_pt = (half_l, half_w, height / 2)
        assert not result.val().isInside(outside_pt), f"Point {outside_pt} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00038438/gpt_generated.stl')
