import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side = 10.0
        extrusion_length = 2 * side  # 20 mm
    
        # --- Step 1: Draw a square on the XY plane ---
        # --- Step 2: Extrude it by twice the side length ---
        result = (
            cq.Workplane("XY")
            .rect(side, side)
            .extrude(extrusion_length)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side) < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - extrusion_length) < TOL, f"Z length (extrusion): expected {extrusion_length}, got {bb.zlen}"
    
        # Volume check: side * side * extrusion_length
        expected_volume = side * side * extrusion_length
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) < TOL, f"Volume: expected {expected_volume}, got {actual_volume}"
    
        # Face count: a box has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Edge count: a box has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a box has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Extrusion goes from Z=0 upward to Z=extrusion_length (20 mm)
        # Top face center at Z = extrusion_length
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - extrusion_length) < TOL, f"Top face Z center: expected {extrusion_length}, got {top_face_z}"
    
        # Bottom face center at Z = 0
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(bottom_face_z - 0.0) < TOL, f"Bottom face Z center: expected 0.0, got {bottom_face_z}"
    
        # All faces are planar (no curved surfaces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # Center of mass should be at (0, 0, extrusion_length/2)
        # since the square is centered in XY and extrusion goes from 0 to extrusion_length
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z - extrusion_length / 2) < TOL, f"Center of mass Z: expected {extrusion_length/2}, got {com.z}"
    
        # Extrusion length (Z) is exactly twice the side length (X and Y)
        assert abs(bb.zlen - 2 * bb.xlen) < TOL, f"Extrusion (Z) should be 2x side (X): zlen={bb.zlen}, xlen={bb.xlen}"
        assert abs(bb.zlen - 2 * bb.ylen) < TOL, f"Extrusion (Z) should be 2x side (Y): zlen={bb.zlen}, ylen={bb.ylen}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520974/gpt_generated.stl')
