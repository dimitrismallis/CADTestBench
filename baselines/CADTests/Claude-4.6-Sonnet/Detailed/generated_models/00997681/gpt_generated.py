import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.058594   # shorter dimension (X)
        width  = 0.75       # longer dimension (Y)
        height = 0.216797   # extrusion height (Z)
        fillet_r = height - 0.1875  # = 0.029297
    
        # --- Step 1: Create the base box ---
        # Box centered at origin in X and Y, starting at Z=0
        result = cq.Workplane("XY").box(length, width, height, centered=(True, True, False))
    
        # Debug: check what edges are available
        print(f"Total edges: {result.edges().size()}")
        print(f"Edges |Z: {result.edges('|Z').size()}")
    
        # The box has 12 edges: 4 parallel to X, 4 parallel to Y, 4 parallel to Z
        # The 4 vertical edges (|Z) are at the 4 corners
        # We want the 2 on the +X side
        # Their centers are at x=+L/2, y=±W/2, z=height/2
    
        # Try selecting edges at >X position among |Z edges
        # Use a custom approach: get all |Z edges and filter by X position
    
        # Alternative: use the Sketch API to build the profile
        # Use cq.Sketch with rect and selective vertex fillet
    
        s = (
            cq.Sketch()
            .rect(length, width)
            .reset()
            .vertices(">X")   # select vertices on the +X side
            .fillet(fillet_r)
        )
    
        result = cq.Workplane("XY").placeSketch(s).extrude(height)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        print(f"BBox: x={bb.xlen}, y={bb.ylen}, z={bb.zlen}")
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check
        rect_area = length * width
        r = fillet_r
        corner_area_removed = 2 * (r * r - math.pi * r * r / 4)
        expected_area = rect_area - corner_area_removed
        expected_vol = expected_area * height
        actual_vol = result.val().Volume()
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # Check cylindrical faces (the two fillets)
        cyl_faces = result.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_faces}")
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Center of mass
        com = cq.Shape.centerOfMass(result.val())
        print(f"CoM: x={com.x}, y={com.y}, z={com.z}")
        assert com.x < 0, f"Center of mass X should be negative, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
        assert abs(com.z - height / 2) < TOL, f"Center of mass Z should be {height/2}, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997681/gpt_generated.stl')
