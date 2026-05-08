import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Define dimensions ---
        length = 200.0   # very long (X direction)
        width  = 10.0    # very narrow (Y direction)
        height = 80.0    # tall (Z direction)
    
        # --- Step 2: Create the rectangular prism (box) ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check that it is centered at the origin
        center = result.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z: expected 0, got {center.z}"
    
        # Check volume
        expected_vol = length * width * height  # 200 * 10 * 80 = 160000
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) < TOL, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # Check face count: a rectangular prism has exactly 6 planar faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check that all faces are planar
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # Check edge count: a rectangular prism has exactly 12 edges
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Check vertex count: a rectangular prism has exactly 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Verify proportions: length >> height >> width
        assert bb.xlen > bb.zlen, "Length should be greater than height"
        assert bb.zlen > bb.ylen, "Height should be greater than width"
        assert bb.xlen / bb.ylen >= 10, \
            f"Length/width ratio should be >= 10, got {bb.xlen / bb.ylen:.1f}"
    
        # Check top and bottom faces exist at correct Z positions
        top_z    = result.faces(">Z").val().Center().z
        bottom_z = result.faces("<Z").val().Center().z
        assert abs(top_z    - ( height / 2)) < TOL, f"Top face Z:    expected  {height/2}, got {top_z}"
        assert abs(bottom_z - (-height / 2)) < TOL, f"Bottom face Z: expected -{height/2}, got {bottom_z}"
    
        # Verify a point at the center is inside the solid
        assert result.val().isInside((0, 0, 0)), "Center point should be inside the solid"
    
        # Verify a point outside the solid is not inside
        assert not result.val().isInside((0, 0, height)), \
            "Point above solid should not be inside"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00008315/gpt_generated.stl')
