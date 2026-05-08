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
        stem_x = 0.036      # stem cross-section length (X)
        stem_y = 0.0135     # stem cross-section width (Y)
        stem_h = 0.9        # stem height (Z)
    
        bar_x = 0.24        # crossbar length (X)
        bar_y = 0.0135      # crossbar width (Y)
        bar_z = 0.036       # crossbar extrusion height (Z)
    
        # Crossbar bottom is 0.15m below the top of the stem
        # top of stem = 0.9, so crossbar bottom at Z = 0.9 - 0.15 = 0.75
        bar_z_bottom = stem_h - 0.15  # = 0.75
    
        # --- Step 1: Create the vertical stem ---
        # Box centered at origin in XY, extending from Z=0 to Z=stem_h
        stem = (
            cq.Workplane("XY")
            .box(stem_x, stem_y, stem_h, centered=(True, True, False))
        )
    
        # --- Step 2: Create the horizontal crossbar ---
        # Crossbar: 0.24 (X) x 0.0135 (Y) x 0.036 (Z)
        # Centered in X (same center as stem), same Y center as stem
        # Bottom face at Z = bar_z_bottom = 0.75
        crossbar = (
            cq.Workplane("XY")
            .box(bar_x, bar_y, bar_z, centered=(True, True, False))
            .translate((0, 0, bar_z_bottom))
        )
    
        # --- Step 3: Union stem and crossbar ---
        result = stem.union(crossbar)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: crossbar dominates = 0.24m
        assert abs(bb.xlen - bar_x) < TOL, f"X extent: expected {bar_x}, got {bb.xlen}"
    
        # Y extent: both stem and crossbar have same Y = 0.0135m
        assert abs(bb.ylen - stem_y) < TOL, f"Y extent: expected {stem_y}, got {bb.ylen}"
    
        # Z extent: stem dominates = 0.9m
        assert abs(bb.zlen - stem_h) < TOL, f"Z extent: expected {stem_h}, got {bb.zlen}"
    
        # Z starts at 0
        assert abs(bb.zmin) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - stem_h) < TOL, f"Z max: expected {stem_h}, got {bb.zmax}"
    
        # X centered at 0
        assert abs(bb.xmin + bar_x/2) < TOL, f"X min: expected {-bar_x/2}, got {bb.xmin}"
        assert abs(bb.xmax - bar_x/2) < TOL, f"X max: expected {bar_x/2}, got {bb.xmax}"
    
        # Volume calculation:
        # Stem volume = stem_x * stem_y * stem_h
        stem_vol = stem_x * stem_y * stem_h
        # Crossbar volume = bar_x * bar_y * bar_z
        bar_vol = bar_x * bar_y * bar_z
        # Overlap: where stem and crossbar intersect
        # Overlap region: stem_x (X) x stem_y (Y) x bar_z (Z) — stem is narrower in X
        overlap_vol = stem_x * stem_y * bar_z
        expected_vol = stem_vol + bar_vol - overlap_vol
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check crossbar bottom is at Z=0.75
        # The crossbar top should be at Z = 0.75 + 0.036 = 0.786
        # Verify by checking a point inside the crossbar but outside the stem
        # Point at (bar_x/2 * 0.9, 0, bar_z_bottom + bar_z/2) should be inside
        test_point = (bar_x * 0.4, 0, bar_z_bottom + bar_z / 2)
        assert result.val().isInside(test_point), \
            f"Point {test_point} should be inside the crossbar"
    
        # Point outside the crossbar (below bar_z_bottom, far from stem) should be outside
        test_outside = (bar_x * 0.4, 0, bar_z_bottom - 0.01)
        assert not result.val().isInside(test_outside), \
            f"Point {test_outside} should be outside the object"
    
        # Stem point near bottom should be inside
        test_stem_bottom = (0, 0, 0.1)
        assert result.val().isInside(test_stem_bottom), \
            f"Point {test_stem_bottom} should be inside the stem"
    
        # Check cylindrical faces count = 0 (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.4f}, Y={bb.ylen:.4f}, Z={bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998300/gpt_generated.stl')
