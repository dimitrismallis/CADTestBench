import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a workplane on XY and sketch a circle of radius 10mm ---
        # --- Step 2: Extrude the circle by 20mm to form a cylinder ---
        radius = 10.0
        height = 20.0
    
        result = (
            cq.Workplane("XY")
            .circle(radius)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        diameter = 2 * radius
        assert abs(bb.xlen - diameter) < TOL, f"X length: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y length: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL,   f"Z length: expected {height}, got {bb.zlen}"
    
        # Check bounding box extents (centered on XY, base at Z=0, top at Z=height)
        assert abs(bb.xmin - (-radius)) < TOL, f"xmin: expected {-radius}, got {bb.xmin}"
        assert abs(bb.xmax -  radius)   < TOL, f"xmax: expected {radius}, got {bb.xmax}"
        assert abs(bb.ymin - (-radius)) < TOL, f"ymin: expected {-radius}, got {bb.ymin}"
        assert abs(bb.ymax -  radius)   < TOL, f"ymax: expected {radius}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)       < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height)    < TOL, f"zmax: expected {height}, got {bb.zmax}"
    
        # Check volume: V = π * r² * h
        expected_vol = math.pi * radius**2 * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Check face count: 1 cylindrical face + 2 flat circular caps = 3 faces
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Check that there is exactly 1 cylindrical face
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 1, f"Cylindrical faces: expected 1, got {cyl_face_count}"
    
        # Check that there are exactly 2 planar faces (top and bottom caps)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar faces: expected 2, got {planar_face_count}"
    
        # Check circular edges: 2 circular edges (top and bottom circles)
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 2, f"Circular edges: expected 2, got {circ_edge_count}"
    
        # Check center of mass is at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL,                  f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL,                  f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL,     f"CoM Z: expected {height/2}, got {com.z}"
    
        # Check a point inside the cylinder is truly inside
        inside_point = (0, 0, height / 2)
        assert result.val().isInside(inside_point), \
            f"Point {inside_point} should be inside the cylinder"
    
        # Check a point outside the cylinder is not inside
        outside_point = (radius + 1, 0, height / 2)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the cylinder"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00000007/gpt_generated.stl')
