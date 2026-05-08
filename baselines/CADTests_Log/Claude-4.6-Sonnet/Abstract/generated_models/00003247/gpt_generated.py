import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Create a long rectangular prism (100 x 20 x 20 mm) ---
        length = 100.0
        width  = 20.0
        height = 20.0
    
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # 2. Bounding box centered at origin
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # 3. Volume
        expected_vol = length * width * height  # 100 * 20 * 20 = 40000 mm³
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # 4. Face count — a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # 5. All faces are planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, \
            f"Planar face count: expected 6, got {planar_face_count}"
    
        # 6. Edge count — a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # 7. Vertex count — a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # 8. Edges parallel to each axis (4 per axis)
        edges_along_x = result.edges("|X").size()
        edges_along_y = result.edges("|Y").size()
        edges_along_z = result.edges("|Z").size()
        assert edges_along_x == 4, f"Edges along X: expected 4, got {edges_along_x}"
        assert edges_along_y == 4, f"Edges along Y: expected 4, got {edges_along_y}"
        assert edges_along_z == 4, f"Edges along Z: expected 4, got {edges_along_z}"
    
        # 9. Top and bottom faces at correct Z positions
        top_z    = result.faces(">Z").val().Center().z
        bottom_z = result.faces("<Z").val().Center().z
        assert abs(top_z    -  height / 2) < TOL, f"Top face Z:    expected  {height/2}, got {top_z}"
        assert abs(bottom_z - -height / 2) < TOL, f"Bottom face Z: expected -{height/2}, got {bottom_z}"
    
        # 10. The prism is solid (no internal voids) — point at center should be inside
        center_point = (0, 0, 0)
        assert result.val().isInside(center_point), "Center point should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00003247/gpt_generated.stl')
