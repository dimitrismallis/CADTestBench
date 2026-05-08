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
        length = 0.74999   # X dimension
        width  = 0.73843   # Y dimension
        height = 0.11078   # Z extrusion height
        fillet_r = 0.038   # corner fillet radius
    
        # --- Step 1: Create 2D rounded rectangle profile ---
        # Draw a rectangle and apply 2D fillet to all 4 corners
        profile = (
            cq.Workplane("XY")
            .rect(length, width)
        )
    
        # --- Step 2: Extrude to height ---
        result = profile.extrude(height)
    
        # --- Step 3: Fillet the vertical edges (4 corners) ---
        # The vertical edges are parallel to Z
        result = result.edges("|Z").fillet(fillet_r)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        # After filleting vertical edges, the bounding box in X and Y remains the same
        # (fillet removes material from corners but doesn't change the overall extents)
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box volume minus 4 corner fillets
        # Each vertical fillet removes a quarter-cylinder from each corner
        # Volume of 4 quarter-cylinders = 1 full cylinder of radius r and height h
        box_vol = length * width * height
        fillet_removed = math.pi * fillet_r**2 * height  # 4 * (1/4 * pi * r^2 * h)
        expected_vol = box_vol - fillet_removed
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 
        # Top face: 1 (planar, octagonal-ish with 4 straight + 4 arc edges)
        # Bottom face: 1
        # 4 flat side faces (between fillets)
        # 4 curved fillet faces (cylindrical)
        # Total: 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check cylindrical faces (4 fillet faces)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 4, f"Cylindrical faces: expected 4, got {cyl_faces}"
    
        # Check planar faces (top + bottom + 4 sides = 6)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # Check the object is centered at origin in X and Y
        center = result.val().Center()
        assert abs(center.x) < TOL, f"Center X: expected 0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected 0, got {center.y}"
        assert abs(center.z - height/2) < TOL, f"Center Z: expected {height/2}, got {center.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521969/gpt_generated.stl')
