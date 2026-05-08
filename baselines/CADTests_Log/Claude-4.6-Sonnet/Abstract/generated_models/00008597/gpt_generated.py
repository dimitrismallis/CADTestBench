import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side   = 20.0   # square side length (mm)
        height = 20.0   # extrusion height (mm)
    
        # --- Step 1: Draw a square on the XY plane ---
        # --- Step 2: Extrude it upward along Z ---
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side)   < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side)   < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Bounding box extents (centered on XY, starting at Z=0)
        assert abs(bb.xmin - (-side/2))   < TOL, f"xmin: expected {-side/2}, got {bb.xmin}"
        assert abs(bb.xmax -  (side/2))   < TOL, f"xmax: expected {side/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-side/2))   < TOL, f"ymin: expected {-side/2}, got {bb.ymin}"
        assert abs(bb.ymax -  (side/2))   < TOL, f"ymax: expected {side/2}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0)         < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height)      < TOL, f"zmax: expected {height}, got {bb.zmax}"
    
        # Volume: side × side × height
        expected_vol = side * side * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count: a box has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar (no curved surfaces)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Edge count: a box has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a box has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Top face at max Z, bottom face at min Z
        top_face_z    = result.faces(">Z").val().Center().z
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z    - height) < TOL, f"Top face Z center: expected {height}, got {top_face_z}"
        assert abs(bottom_face_z - 0.0)   < TOL, f"Bottom face Z center: expected 0.0, got {bottom_face_z}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0)        < TOL, f"CoM X: expected 0.0, got {com.x}"
        assert abs(com.y - 0.0)        < TOL, f"CoM Y: expected 0.0, got {com.y}"
        assert abs(com.z - height/2)   < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # A point inside the solid should be reported as inside
        interior_point = (0.0, 0.0, height / 2)
        assert result.val().isInside(interior_point), \
            f"Interior point {interior_point} should be inside the solid"
    
        # A point outside the solid should NOT be inside
        exterior_point = (side, side, height)
        assert not result.val().isInside(exterior_point), \
            f"Exterior point {exterior_point} should NOT be inside the solid"
    
        return result
    
    final_result = create_cad()
    print("All assertions passed — extruded square created successfully.")
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00008597/gpt_generated.stl')
