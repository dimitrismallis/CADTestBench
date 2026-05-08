import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        diameter = 200.0   # very large diameter
        radius   = diameter / 2.0  # 100 mm
        height   = 20.0    # short height
    
        # --- Step 1: Create the short cylinder ---
        result = cq.Workplane("XY").cylinder(height, radius)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - diameter) < TOL, f"X extent: expected {diameter}, got {bb.xlen}"
        assert abs(bb.ylen - diameter) < TOL, f"Y extent: expected {diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height)   < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Center of mass should be at origin (cylinder is centered)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center Z: expected 0, got {com.z}"
    
        # Volume check: π * r² * h
        expected_vol = math.pi * radius**2 * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: 1 curved lateral face + 2 flat circular caps = 3 faces
        face_count = result.faces().size()
        assert face_count == 3, f"Face count: expected 3, got {face_count}"
    
        # Exactly 1 cylindrical face (the lateral surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Exactly 2 planar faces (top and bottom caps)
        plane_faces = result.faces("%Plane").size()
        assert plane_faces == 2, f"Planar faces: expected 2, got {plane_faces}"
    
        # Top face at z = +height/2, bottom face at z = -height/2
        top_z    = result.faces(">Z").val().Center().z
        bottom_z = result.faces("<Z").val().Center().z
        assert abs(top_z    -  height/2) < TOL, f"Top face Z: expected {height/2}, got {top_z}"
        assert abs(bottom_z - -height/2) < TOL, f"Bottom face Z: expected {-height/2}, got {bottom_z}"
    
        # Edge count: 2 circular rim edges + 1 seam edge on the lateral surface = 3
        edge_count = result.edges().size()
        assert edge_count == 3, f"Edge count: expected 3, got {edge_count}"
    
        # 2 circular edges (top and bottom rims)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges == 2, f"Circular edges: expected 2, got {circ_edges}"
    
        # A point at the center of the cylinder should be inside the solid
        assert result.val().isInside((0, 0, 0)), "Center point should be inside the cylinder"
    
        # A point outside the radius should NOT be inside
        assert not result.val().isInside((radius + 1, 0, 0)), \
            "Point outside radius should not be inside the cylinder"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670106/gpt_generated.stl')
