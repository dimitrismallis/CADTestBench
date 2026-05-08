import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 100.0   # long dimension (X)
        width  = 20.0    # narrow dimension (Y)
        height = 80.0    # tall dimension (Z)
    
        # --- Step 1: Create the rectangular prism centered at origin ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check bounding box extents (centered at origin)
        assert abs(bb.xmin - (-length / 2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length / 2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width  / 2)) < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width  / 2)) < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
        assert abs(bb.zmin - (-height / 2)) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( height / 2)) < TOL, f"zmax: expected { height/2}, got {bb.zmax}"
    
        # Check volume
        expected_vol = length * width * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Check face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check all faces are planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Check edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Check center of mass is at origin
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Confirm "long" > "tall" > "narrow" proportions
        assert bb.xlen > bb.zlen, f"Should be longer than tall: xlen={bb.xlen}, zlen={bb.zlen}"
        assert bb.zlen > bb.ylen, f"Should be taller than narrow: zlen={bb.zlen}, ylen={bb.ylen}"
    
        # Check top and bottom faces exist at correct Z positions
        top_face_z    = result.faces(">Z").val().Center().z
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z    -  height / 2) < TOL, f"Top face Z:    expected { height/2}, got {top_face_z}"
        assert abs(bottom_face_z - -height / 2) < TOL, f"Bottom face Z: expected {-height/2}, got {bottom_face_z}"
    
        # Verify a point inside the solid is truly inside
        assert result.val().isInside((0, 0, 0)), "Origin should be inside the solid"
        # Verify a point outside the solid is truly outside
        assert not result.val().isInside((60, 0, 0)), "Point (60,0,0) should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00007258/gpt_generated.stl')
