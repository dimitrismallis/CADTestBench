import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 80.0
        width  = 50.0
        height = 10.0
        fillet_r = 8.0
    
        # --- Step 1: Create a 2D sketch of a rectangle with filleted corners ---
        sketch = (
            cq.Sketch()
            .rect(length, width)
            .vertices()
            .fillet(fillet_r)
        )
    
        # --- Step 2: Extrude the sketch to create a 3D solid ---
        result = (
            cq.Workplane("XY")
            .placeSketch(sketch)
            .extrude(height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 1. Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # 2. Volume check
        # Volume = (rectangle area - 4 corner squares + 4 quarter-circle areas) * height
        rect_area    = length * width
        corner_sq    = fillet_r * fillet_r          # each removed square corner
        quarter_circ = math.pi * fillet_r**2 / 4.0  # each added quarter circle
        profile_area = rect_area - 4 * corner_sq + 4 * quarter_circ
        expected_vol = profile_area * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count check
        # A filleted rectangular prism has:
        #   - 1 top face (planar)
        #   - 1 bottom face (planar)
        #   - 4 flat side faces (planar, between fillets)
        #   - 4 curved fillet faces (cylindrical, at corners)
        # Total = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # 4. Planar faces: top + bottom + 4 sides = 6
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, f"Planar face count: expected 6, got {planar_count}"
    
        # 5. Cylindrical (fillet) faces: 4 corners
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count == 4, f"Cylindrical face count: expected 4, got {cyl_count}"
    
        # 6. Top and bottom faces exist at correct Z positions
        top_z = result.faces(">Z").val().Center().z
        bot_z = result.faces("<Z").val().Center().z
        assert abs(top_z - height) < TOL, f"Top face Z: expected {height}, got {top_z}"
        assert abs(bot_z - 0.0)    < TOL, f"Bottom face Z: expected 0.0, got {bot_z}"
    
        # 7. Symmetry: center of mass should be at (0, 0, height/2)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL,              f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL,              f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"CoM Z: expected {height/2}, got {com.z}"
    
        # 8. Vertical edges (|Z): each of the 4 cylindrical fillet faces contributes
        #    2 vertical straight edges (tangent lines to adjacent flat faces),
        #    giving 4 × 2 = 8 vertical edges total.
        vertical_edges = result.edges("|Z").size()
        assert vertical_edges == 8, \
            f"Vertical edges (|Z): expected 8 (2 per filleted corner), got {vertical_edges}"
    
        # 9. Circular edges: top and bottom profiles each have
        #    4 arc segments (from fillets) + 4 straight segments = 8 edges per face,
        #    so 8 top + 8 bottom = 16 circular/arc edges total.
        circular_edges = result.edges("%Circle").size()
        assert circular_edges == 8, \
            f"Circular edges: expected 8 (4 arcs top + 4 arcs bottom), got {circular_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681463/gpt_generated.stl')
