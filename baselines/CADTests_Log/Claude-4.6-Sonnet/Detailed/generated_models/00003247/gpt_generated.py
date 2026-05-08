import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create rectangular prism (box) ---
        # Length=0.3 (X), Width=0.7 (Y), Height=0.3 (Z)
        result = cq.Workplane("XY").box(0.3, 0.7, 0.3)
    
        # --- Final object verification ---
        TOL = 1e-6
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 0.3) < TOL, f"X length: expected 0.3, got {bb.xlen}"
        assert abs(bb.ylen - 0.7) < TOL, f"Y length: expected 0.7, got {bb.ylen}"
        assert abs(bb.zlen - 0.3) < TOL, f"Z length: expected 0.3, got {bb.zlen}"
    
        # Check bounding box extents (centered at origin)
        assert abs(bb.xmin - (-0.15)) < TOL, f"xmin: expected -0.15, got {bb.xmin}"
        assert abs(bb.xmax - ( 0.15)) < TOL, f"xmax: expected  0.15, got {bb.xmax}"
        assert abs(bb.ymin - (-0.35)) < TOL, f"ymin: expected -0.35, got {bb.ymin}"
        assert abs(bb.ymax - ( 0.35)) < TOL, f"ymax: expected  0.35, got {bb.ymax}"
        assert abs(bb.zmin - (-0.15)) < TOL, f"zmin: expected -0.15, got {bb.zmin}"
        assert abs(bb.zmax - ( 0.15)) < TOL, f"zmax: expected  0.15, got {bb.zmax}"
    
        # Check volume: 0.3 * 0.7 * 0.3 = 0.063
        expected_volume = 0.3 * 0.7 * 0.3
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) < TOL, \
            f"Volume: expected {expected_volume}, got {actual_volume}"
    
        # Check face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check all faces are planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # Check edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Check center of mass is at origin
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check faces parallel to each axis (2 faces per axis)
        faces_parallel_z = result.faces("|Z").size()
        assert faces_parallel_z == 2, f"Faces parallel to Z: expected 2, got {faces_parallel_z}"
    
        faces_parallel_x = result.faces("|X").size()
        assert faces_parallel_x == 2, f"Faces parallel to X: expected 2, got {faces_parallel_x}"
    
        faces_parallel_y = result.faces("|Y").size()
        assert faces_parallel_y == 2, f"Faces parallel to Y: expected 2, got {faces_parallel_y}"
    
        # Check a point inside the solid
        assert result.val().isInside((0, 0, 0)), "Origin should be inside the solid"
        assert not result.val().isInside((1, 1, 1)), "Point (1,1,1) should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00003247/gpt_generated.stl')
