import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.75
        width  = 0.40
        height = 0.2375
        hole_diameter = 0.11875
        hole_radius   = hole_diameter / 2.0  # 0.059375
    
        # --- Step 1: Create rectangular base (centered at origin in X, Y, and Z) ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Add circular through-hole at center of top face ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Check bounding box dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y width:  expected {width},  got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Check bounding box extents (box is centered at origin in all axes by default)
        assert abs(bb.xmin - (-length/2)) < TOL, f"xmin: expected {-length/2}, got {bb.xmin}"
        assert abs(bb.xmax - ( length/2)) < TOL, f"xmax: expected { length/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-width/2))  < TOL, f"ymin: expected {-width/2},  got {bb.ymin}"
        assert abs(bb.ymax - ( width/2))  < TOL, f"ymax: expected { width/2},  got {bb.ymax}"
        assert abs(bb.zmin - (-height/2)) < TOL, f"zmin: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - ( height/2)) < TOL, f"zmax: expected { height/2}, got {bb.zmax}"
    
        # Check volume: box minus cylinder
        box_vol      = length * width * height
        hole_vol     = math.pi * hole_radius**2 * height
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there is exactly one cylindrical face (the hole wall)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 1, \
            f"Cylindrical faces: expected 1, got {cyl_face_count}"
    
        # Check circular edges: top and bottom circles of the hole = 2
        circ_edge_count = result.edges("%Circle").size()
        assert circ_edge_count == 2, \
            f"Circular edges: expected 2, got {circ_edge_count}"
    
        # Check that the hole center is at (0, 0) in XY (i.e., center of rectangle)
        cyl_face = result.faces("%Cylinder").val()
        cyl_center = cyl_face.Center()
        assert abs(cyl_center.x) < TOL, f"Hole center X: expected 0, got {cyl_center.x}"
        assert abs(cyl_center.y) < TOL, f"Hole center Y: expected 0, got {cyl_center.y}"
    
        # Check that a point at the center of the hole is NOT inside the solid
        center_point = (0.0, 0.0, 0.0)  # center of hole at mid-height
        solid = result.val()
        assert not solid.isInside(center_point), \
            "Center of hole should NOT be inside the solid"
    
        # Check that a point near the edge of the rectangle IS inside the solid
        corner_point = (length/2 - 0.05, width/2 - 0.05, 0.0)
        assert solid.isInside(corner_point), \
            "Corner region should be inside the solid"
    
        # Check face count:
        # 4 rectangular side faces + 2 annular faces (top/bottom with hole) + 1 cylindrical = 7
        total_faces = result.faces().size()
        assert total_faces == 7, f"Total faces: expected 7, got {total_faces}"
    
        return result
    
    final_result = create_cad()
    print("All assertions passed!")
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670334/gpt_generated.stl')
