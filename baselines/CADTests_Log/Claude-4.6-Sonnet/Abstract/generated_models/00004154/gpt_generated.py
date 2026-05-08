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
        width   = 80.0   # X dimension
        height  = 50.0   # Y dimension
        radius  = 8.0    # corner fillet radius
        depth   = 15.0   # extrusion height
    
        # --- Step 1: Create a rounded rectangle profile using rect + fillet via Sketch ---
        # Use the Sketch API to build a rectangle with filleted corners,
        # then place it on the XY workplane and extrude.
        sketch = (
            cq.Sketch()
            .rect(width, height)
            .vertices()
            .fillet(radius)
        )
    
        # --- Step 2: Extrude the rounded rectangle profile ---
        result = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - width)  < TOL, f"X length: expected {width}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Y length: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - depth)  < TOL, f"Z length: expected {depth}, got {bb.zlen}"
    
        # 2b. Z extents: bottom at z=0, top at z=depth (extrude goes up from XY plane)
        assert abs(bb.zmin - 0.0)   < TOL, f"Z min: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, f"Z max: expected {depth}, got {bb.zmax}"
    
        # 2c. Volume check:
        # Rounded rectangle area = width*height - (4 - pi)*radius^2
        # (subtract 4 corner squares, add back the 4 quarter-circles)
        rounded_rect_area = width * height - (4 - math.pi) * radius ** 2
        expected_vol = rounded_rect_area * depth
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 2d. Face count:
        # A rounded-rectangle extrusion has:
        #   - 1 top face (flat)
        #   - 1 bottom face (flat)
        #   - 4 flat side faces (along the straight edges)
        #   - 4 curved side faces (one per rounded corner)
        # Total = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # 2e. Cylindrical (curved) faces — one per rounded corner = 4
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 4, f"Cylindrical faces: expected 4, got {cyl_face_count}"
    
        # 2f. Planar faces — top + bottom + 4 sides = 6
        plane_face_count = result.faces("%Plane").size()
        assert plane_face_count == 6, f"Planar faces: expected 6, got {plane_face_count}"
    
        # 2g. Top and bottom faces exist at correct Z positions
        top_face_z    = result.faces(">Z").val().Center().z
        bottom_face_z = result.faces("<Z").val().Center().z
        assert abs(top_face_z    - depth) < TOL, f"Top face Z center: expected {depth}, got {top_face_z}"
        assert abs(bottom_face_z - 0.0)   < TOL, f"Bottom face Z center: expected 0.0, got {bottom_face_z}"
    
        # 2h. Center of mass should be at (0, 0, depth/2) by symmetry
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL,                  f"CoM X: expected 0.0, got {com.x}"
        assert abs(com.y) < TOL,                  f"CoM Y: expected 0.0, got {com.y}"
        assert abs(com.z - depth / 2) < TOL,      f"CoM Z: expected {depth/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00004154/gpt_generated.stl')
