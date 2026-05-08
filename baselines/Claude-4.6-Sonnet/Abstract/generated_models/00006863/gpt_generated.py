import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define rectangle dimensions and extrusion height ---
        length = 80.0   # X dimension
        width  = 50.0   # Y dimension
        height = 20.0   # Z extrusion height
    
        # --- Step 2: Create rectangle sketch on XY plane and extrude ---
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
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Bounding box extents (centered on origin in X and Y, base at Z=0)
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
        assert abs(bb.zmin - 0)      < TOL, f"zmin: expected 0,      got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, f"zmax: expected {height}, got {bb.zmax}"
    
        # Volume check: a solid rectangular box
        expected_volume = length * width * height  # 80 * 50 * 20 = 80000
        actual_volume   = result.val().Volume()
        assert abs(actual_volume - expected_volume) < TOL, \
            f"Volume: expected {expected_volume}, got {actual_volume}"
    
        # Face count: a rectangular box has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # All faces should be planar
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar face count: expected 6, got {planar_face_count}"
    
        # Top and bottom faces (parallel to XY plane)
        top_bottom_count = result.faces("|Z").size()
        assert top_bottom_count == 2, f"Top/bottom face count: expected 2, got {top_bottom_count}"
    
        # Side faces parallel to XZ plane (front/back)
        xz_parallel_count = result.faces("|Y").size()
        assert xz_parallel_count == 2, f"XZ-parallel face count: expected 2, got {xz_parallel_count}"
    
        # Side faces parallel to YZ plane (left/right)
        yz_parallel_count = result.faces("|X").size()
        assert yz_parallel_count == 2, f"YZ-parallel face count: expected 2, got {yz_parallel_count}"
    
        # Edge count: a rectangular box has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: a rectangular box has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Center of mass should be at the geometric center
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - 0)           < TOL, f"CoM X: expected 0,           got {com.x}"
        assert abs(com.y - 0)           < TOL, f"CoM Y: expected 0,           got {com.y}"
        assert abs(com.z - height / 2)  < TOL, f"CoM Z: expected {height/2},  got {com.z}"
    
        # Solid count: exactly one solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00006863/gpt_generated.stl')
