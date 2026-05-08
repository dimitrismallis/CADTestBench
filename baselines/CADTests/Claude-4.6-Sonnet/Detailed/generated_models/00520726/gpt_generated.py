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
        block_l = 0.5
        block_w = 0.5
        block_h = 0.633333
    
        cyl_h = 0.116667
        cyl_d = 0.316667
        cyl_r = cyl_d / 2.0
    
        cav_l = 0.411666
        cav_w = 0.411666
        cav_depth = 0.533333
        cav_recess = 0.05  # floor of cavity is 0.05 above bottom surface
    
        # --- Step 1: Create rectangular block with bottom at Z=0 ---
        # centered=False means block goes from (0,0,0) to (block_l, block_w, block_h)
        # We'll use centered=(True,True,False) so it's centered in X,Y but starts at Z=0
        result = cq.Workplane("XY").box(block_l, block_w, block_h, centered=(True, True, False))
    
        # --- Step 2: Add cylinder on top, centered on top face ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(cyl_r)
            .extrude(cyl_h)
        )
    
        # --- Step 3: Hollow out cavity from the bottom ---
        # The cavity floor is at z = cav_recess = 0.05 (above bottom surface)
        # The cavity extends upward: depth = 0.533333
        # So cavity top is at z = 0.05 + 0.533333 = 0.583333
        # We cut from the bottom face upward
        # The cavity is centered in X,Y
        # We create the cavity as a box cut from the bottom
        # The cavity box: cav_l x cav_w x cav_depth, positioned so its bottom is at z=cav_recess
    
        # Create a cutting solid: a box centered in X,Y, from z=cav_recess to z=cav_recess+cav_depth
        cavity = (
            cq.Workplane("XY")
            .workplane(offset=cav_recess)
            .box(cav_l, cav_w, cav_depth, centered=(True, True, False))
        )
    
        result = result.cut(cavity)
    
        # --- Step 4: The model is already aligned with base at Z=0 (centered=(True,True,False)) ---
        # No additional translation needed since we built with bottom at Z=0
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X: centered, so -0.25 to +0.25
        assert abs(bb.xlen - block_l) < TOL, f"X length: expected {block_l}, got {bb.xlen}"
        assert abs(bb.ylen - block_w) < TOL, f"Y length: expected {block_w}, got {bb.ylen}"
        # Z: from 0 to block_h + cyl_h
        expected_zlen = block_h + cyl_h
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
        assert abs(bb.zmin) < TOL, f"Z min (base at ground): expected 0, got {bb.zmin}"
        assert abs(bb.zmax - expected_zlen) < TOL, f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # X and Y centered
        assert abs(bb.xmin + block_l/2) < TOL, f"X min: expected {-block_l/2}, got {bb.xmin}"
        assert abs(bb.xmax - block_l/2) < TOL, f"X max: expected {block_l/2}, got {bb.xmax}"
        assert abs(bb.ymin + block_w/2) < TOL, f"Y min: expected {-block_w/2}, got {bb.ymin}"
        assert abs(bb.ymax - block_w/2) < TOL, f"Y max: expected {block_w/2}, got {bb.ymax}"
    
        # Volume check
        block_vol = block_l * block_w * block_h
        cyl_vol = math.pi * cyl_r**2 * cyl_h
        cav_vol = cav_l * cav_w * cav_depth
        expected_vol = block_vol + cyl_vol - cav_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cavity exists: a point inside the cavity should NOT be inside the solid
        # Cavity center in X,Y is (0,0), at z = cav_recess + cav_depth/2
        cav_center_z = cav_recess + cav_depth / 2.0
        cavity_interior_point = cq.Vector(0, 0, cav_center_z)
        assert not solid.isInside(cavity_interior_point), \
            f"Cavity interior point {cavity_interior_point} should be outside solid (cavity should exist)"
    
        # Check cavity floor: point just above the floor (z = cav_recess + small epsilon) should be outside
        just_above_floor = cq.Vector(0, 0, cav_recess + 0.001)
        assert not solid.isInside(just_above_floor), \
            f"Point just above cavity floor should be outside solid"
    
        # Check cavity recess: point below cavity floor (z = cav_recess/2) should be inside solid
        below_cavity_floor = cq.Vector(0, 0, cav_recess / 2.0)
        assert solid.isInside(below_cavity_floor), \
            f"Point below cavity floor (z={cav_recess/2}) should be inside solid"
    
        # Check cylinder exists: point inside cylinder above block top should be inside solid
        cyl_interior = cq.Vector(0, 0, block_h + cyl_h / 2.0)
        assert solid.isInside(cyl_interior), \
            f"Point inside cylinder should be inside solid"
    
        # Check cylindrical face exists (the cylinder side)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520726/gpt_generated.stl')
