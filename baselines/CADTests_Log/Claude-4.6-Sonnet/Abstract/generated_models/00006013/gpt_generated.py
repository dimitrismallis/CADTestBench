import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 200.0   # large rectangle length (X)
        width  = 120.0   # large rectangle width (Y)
        height = 5.0     # marginal extrusion height (Z)
    
        # --- Step 1: Create a large rectangle sketch on XY plane ---
        # --- Step 2: Extrude it marginally to form a thin flat plate ---
        result = (
            cq.Workplane("XY")
            .rect(length, width)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Bounding box extents (centered on XY, base at Z=0)
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
        assert abs(bb.zmin - 0)             < TOL, f"zmin: expected 0,           got {bb.zmin}"
        assert abs(bb.zmax - height)        < TOL, f"zmax: expected {height},    got {bb.zmax}"
    
        # Volume check: should equal length × width × height exactly (no holes)
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count: a box has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar (no curved surfaces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, \
            f"Planar face count: expected 6, got {planar_face_count}"
    
        # Top face at max Z
        top_faces = result.faces(">Z").size()
        assert top_faces == 1, f"Top face count: expected 1, got {top_faces}"
    
        # Bottom face at min Z
        bot_faces = result.faces("<Z").size()
        assert bot_faces == 1, f"Bottom face count: expected 1, got {bot_faces}"
    
        # Edge count: a rectangular box has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a rectangular box has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0)           < TOL, f"CoM X: expected 0,          got {com.x}"
        assert abs(com.y - 0)           < TOL, f"CoM Y: expected 0,          got {com.y}"
        assert abs(com.z - height / 2)  < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # The solid should contain its own center point
        assert result.val().isInside((0, 0, height / 2)), \
            "Center point should be inside the solid"
    
        # The solid should NOT contain a point outside it
        assert not result.val().isInside((length, width, height)), \
            "Point outside solid should not be inside"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00006013/gpt_generated.stl')
