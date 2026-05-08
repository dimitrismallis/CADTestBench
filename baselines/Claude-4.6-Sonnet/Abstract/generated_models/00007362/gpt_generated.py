import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        LENGTH = 200.0   # very long (X)
        WIDTH  = 80.0    # wide (Y)
        HEIGHT = 20.0    # short (Z)
    
        # --- Step 1: Create the rectangular prism (box) ---
        result = cq.Workplane("XY").box(LENGTH, WIDTH, HEIGHT)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - LENGTH) < TOL, f"X length: expected {LENGTH}, got {bb.xlen}"
        assert abs(bb.ylen - WIDTH)  < TOL, f"Y width:  expected {WIDTH},  got {bb.ylen}"
        assert abs(bb.zlen - HEIGHT) < TOL, f"Z height: expected {HEIGHT}, got {bb.zlen}"
    
        # 2. Proportions: length >> width >> height
        assert bb.xlen > 2 * bb.ylen, f"Should be much longer than wide: xlen={bb.xlen}, ylen={bb.ylen}"
        assert bb.ylen > 2 * bb.zlen, f"Should be wider than tall: ylen={bb.ylen}, zlen={bb.zlen}"
    
        # 3. Volume
        expected_vol = LENGTH * WIDTH * HEIGHT
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # 4. Face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # 5. All faces are planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # 6. Edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # 7. Vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # 8. Center of mass at origin (box is centered by default)
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # 9. Top and bottom faces exist at correct Z positions
        top_face_z    = result.faces(">Z").val().Center().z
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z    -  HEIGHT / 2) < TOL, f"Top face Z: expected {HEIGHT/2}, got {top_face_z}"
        assert abs(bottom_face_z - -HEIGHT / 2) < TOL, f"Bottom face Z: expected {-HEIGHT/2}, got {bottom_face_z}"
    
        # 10. Edges parallel to Z (vertical edges): 4 expected
        z_edges = result.edges("|Z").size()
        assert z_edges == 4, f"Edges parallel to Z: expected 4, got {z_edges}"
    
        # 11. Edges parallel to X (long edges): 4 expected
        x_edges = result.edges("|X").size()
        assert x_edges == 4, f"Edges parallel to X: expected 4, got {x_edges}"
    
        # 12. Edges parallel to Y (width edges): 4 expected
        y_edges = result.edges("|Y").size()
        assert y_edges == 4, f"Edges parallel to Y: expected 4, got {y_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00007362/gpt_generated.stl')
