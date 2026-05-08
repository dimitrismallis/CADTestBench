import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_size = 1.5
        outer_fillet = 0.157235
        height = 0.655147
        inner_size = 1.44759
        inner_fillet = 0.13103
        half_height = height / 2.0
    
        # --- Step 1: Create outer square sketch with rounded corners ---
        outer_sketch = (
            cq.Sketch()
            .rect(outer_size, outer_size)
            .vertices()
            .fillet(outer_fillet)
        )
    
        # --- Step 2: Extrude outer sketch to height ---
        outer_solid = (
            cq.Workplane("XY")
            .placeSketch(outer_sketch)
            .extrude(height)
        )
    
        # --- Step 3: Create inner square sketch with rounded corners ---
        inner_sketch = (
            cq.Sketch()
            .rect(inner_size, inner_size)
            .vertices()
            .fillet(inner_fillet)
        )
    
        # --- Step 4: Create inner solid to cut with (same height, placed at top, cutting downward) ---
        # Build the inner solid separately and use .cut()
        inner_solid = (
            cq.Workplane("XY")
            .placeSketch(inner_sketch)
            .extrude(height)
        )
    
        # --- Step 5: Cut inner solid from outer solid ---
        result = outer_solid.cut(inner_solid)
    
        # --- Step 6: Translate vertically by half the height to center ---
        result = result.translate((0, 0, -half_height))
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - outer_size) < TOL, f"X length: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - outer_size) < TOL, f"Y length: expected {outer_size}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # After centering, the object should span from -half_height to +half_height in Z
        assert abs(bb.zmin - (-half_height)) < TOL, f"Z min: expected {-half_height}, got {bb.zmin}"
        assert abs(bb.zmax - half_height) < TOL, f"Z max: expected {half_height}, got {bb.zmax}"
    
        # Volume check:
        # Since the inner cut goes the full height, the result is a hollow frame (no bottom, no top)
        # Outer area (square with filleted corners): A = side^2 - (4 - pi) * r^2
        outer_area = outer_size**2 - (4 - math.pi) * outer_fillet**2
        # Inner area (square with filleted corners)
        inner_area = inner_size**2 - (4 - math.pi) * inner_fillet**2
        # Volume = (outer_area - inner_area) * height
        expected_vol = (outer_area - inner_area) * height
        actual_vol = solid.Volume()
    
        print(f"Outer area: {outer_area:.6f}")
        print(f"Inner area: {inner_area:.6f}")
        print(f"Expected volume: {expected_vol:.6f}")
        print(f"Actual volume: {actual_vol:.6f}")
        print(f"Bounding box: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
        print(f"Z range: [{bb.zmin:.4f}, {bb.zmax:.4f}]")
    
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The object should be hollow: a point in the center of the cavity should NOT be inside the solid
        cavity_point = (0.0, 0.0, 0.0)
        assert not solid.isInside(cavity_point), \
            f"Cavity point {cavity_point} should be outside (hollow), but is inside the solid"
    
        # A point in the wall should be inside the solid
        wall_mid = (outer_size / 2.0 - (outer_size - inner_size) / 4.0, 0.0, 0.0)
        assert solid.isInside(wall_mid), \
            f"Wall point {wall_mid} should be inside the solid, but is not"
    
        # Check cylindrical faces exist (from the filleted corners)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces > 0, f"Expected cylindrical faces from fillets, got {cyl_faces}"
    
        # Check planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 2, f"Expected at least 2 planar faces, got {planar_faces}"
    
        print(f"Planar faces: {planar_faces}, Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997753/gpt_generated.stl')
