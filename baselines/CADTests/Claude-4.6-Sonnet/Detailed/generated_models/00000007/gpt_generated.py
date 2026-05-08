import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create workplane and draw circle with radius 0.75 ---
        # --- Step 2: Extrude the circle 0.20923 units high ---
        result = (
            cq.Workplane("XY")
            .circle(0.75)
            .extrude(0.20923)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        diameter = 0.75 * 2  # 1.5
        assert abs(bb.xlen - diameter) < TOL, f"X length: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y length: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - 0.20923) < TOL, f"Z length: expected 0.20923, got {bb.zlen}"
    
        # Z extents: centered=True by default for extrude, but extrude goes from 0 to height
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - 0.20923) < TOL, f"Z max: expected 0.20923, got {bb.zmax}"
    
        # Volume check: V = pi * r^2 * h
        expected_volume = math.pi * (0.75 ** 2) * 0.20923
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.001, \
            f"Volume: expected {expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Face count: cylinder has 3 faces (top circle, bottom circle, curved side)
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Check cylindrical face exists (the curved side)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check top and bottom planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, f"Planar faces: expected 2, got {planar_faces}"
    
        # Check circular edges (top and bottom circles)
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 2, f"Circular edges: expected 2, got {circular_edges}"
    
        # Center of mass should be at (0, 0, h/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - 0.20923 / 2) < TOL, f"Center of mass Z: expected {0.20923/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00000007/gpt_generated.stl')
