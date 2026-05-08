import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a 0.25 x 0.25 square profile on XY plane ---
        # --- Step 2: Extrude it 0.5 units in +Z ---
        result = (
            cq.Workplane("XY")
            .rect(0.25, 0.25)
            .extrude(0.5)
        )
    
        # --- Final object verification ---
        TOL = 1e-6
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 0.25) < TOL, f"X length: expected 0.25, got {bb.xlen}"
        assert abs(bb.ylen - 0.25) < TOL, f"Y length: expected 0.25, got {bb.ylen}"
        assert abs(bb.zlen - 0.50) < TOL, f"Z length: expected 0.50, got {bb.zlen}"
    
        # Volume check: 0.25 * 0.25 * 0.5 = 0.03125
        expected_vol = 0.25 * 0.25 * 0.5
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Face count: a box has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Edge count: a box has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a box has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # All faces should be planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # Top face at z = 0.5, bottom face at z = 0.0
        top_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_bb.zmax - 0.5) < TOL, f"Top face Z: expected 0.5, got {top_bb.zmax}"
    
        bot_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_bb.zmin - 0.0) < TOL, f"Bottom face Z: expected 0.0, got {bot_bb.zmin}"
    
        # Center of mass should be at (0, 0, 0.25)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0.0) < TOL, f"CoM X: expected 0.0, got {com.x}"
        assert abs(com.y - 0.0) < TOL, f"CoM Y: expected 0.0, got {com.y}"
        assert abs(com.z - 0.25) < TOL, f"CoM Z: expected 0.25, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520974/gpt_generated.stl')
