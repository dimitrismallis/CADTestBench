import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a 1.5 x 1.5 square profile on the XY plane ---
        result = cq.Workplane("XY").rect(1.5, 1.5)
    
        # --- Step 2: Extrude the square to a height of 0.75 units ---
        result = result.extrude(0.75)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 1.5) < TOL, f"X length: expected 1.5, got {bb.xlen}"
        assert abs(bb.ylen - 1.5) < TOL, f"Y length: expected 1.5, got {bb.ylen}"
        assert abs(bb.zlen - 0.75) < TOL, f"Z height: expected 0.75, got {bb.zlen}"
    
        # Check volume: 1.5 * 1.5 * 0.75 = 1.6875
        expected_vol = 1.5 * 1.5 * 0.75
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Check face count: a box has 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check that there are 2 horizontal (Z-normal) faces: top and bottom
        z_faces = result.faces("|Z").size()
        assert z_faces == 2, f"Z-parallel faces: expected 2, got {z_faces}"
    
        # Check that there are 4 vertical (side) faces
        side_faces = result.faces("|X").size() + result.faces("|Y").size()
        assert side_faces == 4, f"Side faces: expected 4, got {side_faces}"
    
        # Check edge count: a box has 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a box has 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Check center of mass is at origin (centered box)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - 0.375) < TOL, f"Center Z: expected 0.375, got {center.z}"
    
        # Check top face is at z = 0.75
        top_z = result.faces(">Z").val().BoundingBox().zmax
        assert abs(top_z - 0.75) < TOL, f"Top face Z: expected 0.75, got {top_z}"
    
        # Check bottom face is at z = 0
        bot_z = result.faces("<Z").val().BoundingBox().zmin
        assert abs(bot_z - 0.0) < TOL, f"Bottom face Z: expected 0.0, got {bot_z}"
    
        return result
    
    final_result = create_cad()
    print("All assertions passed. Model created successfully.")
    print(f"Bounding box: {final_result.val().BoundingBox().xlen} x {final_result.val().BoundingBox().ylen} x {final_result.val().BoundingBox().zlen}")
    print(f"Volume: {final_result.val().Volume()}")
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00008597/gpt_generated.stl')
