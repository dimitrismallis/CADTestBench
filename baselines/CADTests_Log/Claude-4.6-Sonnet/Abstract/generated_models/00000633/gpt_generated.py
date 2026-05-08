import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length   = 80.0   # X dimension
        width    = 50.0   # Y dimension
        height   =  5.0   # Z dimension (thickness)
        hole_dia = 20.0   # diameter of the central circular hole
        hole_r   = hole_dia / 2.0
    
        # --- Step 1: Create the base rectangular plate ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Cut a circular through-hole in the center ---
        result = result.faces(">Z").workplane().hole(hole_dia)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box must match the plate dimensions exactly
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2b. Volume = box volume minus cylinder volume
        box_vol  = length * width * height
        hole_vol = math.pi * hole_r**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, (
            f"Volume: expected ~{expected_vol:.3f}, got {actual_vol:.3f}"
        )
    
        # 2c. There must be exactly one cylindrical face (the hole wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # 2d. There must be exactly 2 circular edges (top and bottom rim of the hole)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # 2e. The hole is centered: a point at the center of the plate (inside the hole)
        #     should NOT be inside the solid
        center_point = (0.0, 0.0, 0.0)
        assert not result.val().isInside(center_point), (
            "Center of plate should be inside the hole (not inside the solid)"
        )
    
        # 2f. A point near the corner (well within the plate, away from the hole)
        #     should be inside the solid
        corner_point = (length/2 - 5, width/2 - 5, 0.0)
        assert result.val().isInside(corner_point), (
            f"Corner region {corner_point} should be inside the solid plate"
        )
    
        # 2g. Planar faces: 2 large flat faces (top/bottom) + 4 side faces = 6 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # 2h. Center of mass should be at the geometric center (0, 0, 0) by symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00000633/gpt_generated.stl')
