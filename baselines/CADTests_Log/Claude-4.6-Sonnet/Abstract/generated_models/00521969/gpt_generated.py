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
        side = 40.0          # square side length (mm)
        corner_r = 8.0       # corner fillet radius (mm)
        height = 20.0        # extrusion height (mm)
    
        # --- Step 1: Create a rounded square sketch ---
        # Use the Sketch API: draw a rectangle, then fillet all 4 vertices
        sketch = (
            cq.Sketch()
            .rect(side, side)
            .vertices()
            .fillet(corner_r)
        )
    
        # --- Step 2: Extrude the rounded square profile ---
        result = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2.1 Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side) < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2.2 Bounding box extents (centered on XY, base at Z=0)
        assert abs(bb.xmin - (-side / 2)) < TOL, f"xmin: expected {-side/2}, got {bb.xmin}"
        assert abs(bb.xmax - (side / 2)) < TOL,  f"xmax: expected {side/2}, got {bb.xmax}"
        assert abs(bb.ymin - (-side / 2)) < TOL, f"ymin: expected {-side/2}, got {bb.ymin}"
        assert abs(bb.ymax - (side / 2)) < TOL,  f"ymax: expected {side/2}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0) < TOL,         f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL,       f"zmax: expected {height}, got {bb.zmax}"
    
        # 2.3 Volume check
        # Rounded square area = side^2 - (4 - pi) * r^2
        # (subtract 4 square corners, add 4 quarter-circle sectors = 1 full circle)
        rounded_sq_area = side**2 - (4 - math.pi) * corner_r**2
        expected_vol = rounded_sq_area * height
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 2.4 Face count check
        # A rounded-square extrusion has:
        #   - 1 top face (flat)
        #   - 1 bottom face (flat)
        #   - 4 flat side faces (one per straight edge of the square)
        #   - 4 curved side faces (one per rounded corner)
        # Total = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # 2.5 Cylindrical (curved) faces = 4 (one per rounded corner)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 4, f"Cylindrical faces: expected 4, got {cyl_face_count}"
    
        # 2.6 Planar faces = 6 (top + bottom + 4 sides)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 6, f"Planar faces: expected 6, got {planar_face_count}"
    
        # 2.7 Top and bottom faces exist at correct Z
        top_face_z = result.faces(">Z").val().Center().z
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z - height) < TOL, f"Top face Z center: expected {height}, got {top_face_z}"
        assert abs(bot_face_z - 0.0) < TOL,   f"Bottom face Z center: expected 0.0, got {bot_face_z}"
    
        # 2.8 Center of mass should be at (0, 0, height/2) by symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL,                  f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL,                  f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL,     f"CoM Z: expected {height/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521969/gpt_generated.stl')
