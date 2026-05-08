import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        width  = 20.0   # Y dimension
        length = 40.0   # X dimension (twice the width)
        height = 10.0   # Z dimension (extrusion depth)
    
        # --- Step 1: Create a rectangle on the XY plane with length = 2 * width ---
        # --- Step 2: Extrude it upward to form a rectangular prism ---
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
    
        # Length == 2 * width
        assert abs(bb.xlen - 2 * bb.ylen) < TOL, (
            f"Length should be 2x width: xlen={bb.xlen}, ylen={bb.ylen}"
        )
    
        # Volume check: length * width * height
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, (
            f"Volume: expected {expected_vol}, got {actual_vol}"
        )
    
        # Face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Extrude goes from Z=0 to Z=height (rect is centered in XY, extrude goes up)
        # Top face center at Z = height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - height) < TOL, (
            f"Top face Z center: expected {height}, got {top_face_z}"
        )
    
        # Bottom face center at Z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, (
            f"Bottom face Z center: expected 0.0, got {bot_face_z}"
        )
    
        # Edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass: X=0, Y=0 (rect centered), Z=height/2 (extrude goes up)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00031181/gpt_generated.stl')
