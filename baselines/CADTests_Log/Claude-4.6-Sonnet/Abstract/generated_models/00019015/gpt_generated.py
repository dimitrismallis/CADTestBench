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
        cyl_height   = 20.0    # short cylinder
        cyl_radius   = 40.0    # large diameter (80mm)
        cyl_diameter = cyl_radius * 2  # 80mm
    
        prism_length = 90.0    # slightly longer than cylinder diameter (80mm)
        prism_width  = 10.0    # narrow
        prism_height = 8.0     # short
    
        # --- Step 1: Create the cylinder centered at origin, sitting on XY plane ---
        # centered=(True, True, False) → centered in X and Y, but starts at Z=0
        cylinder = (
            cq.Workplane("XY")
            .cylinder(cyl_height, cyl_radius, centered=(True, True, False))
        )
    
        # --- Step 2: Create the rectangular prism ---
        # It sits on top of the cylinder (Z = cyl_height)
        # centered in X and Y, bottom face at Z = cyl_height
        prism = (
            cq.Workplane("XY")
            .workplane(offset=cyl_height)
            .box(prism_length, prism_width, prism_height, centered=(True, True, False))
        )
    
        # --- Step 3: Union the two shapes ---
        result = cylinder.union(prism)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: prism is longer (90mm), centered → -45 to +45
        assert abs(bb.xlen - prism_length) < TOL, \
            f"BBox X length: expected {prism_length}, got {bb.xlen}"
    
        # Bounding box Y: cylinder is wider (80mm diameter), centered → -40 to +40
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"BBox Y length: expected {cyl_diameter}, got {bb.ylen}"
    
        # Bounding box Z: cylinder (20) + prism (8) = 28mm total
        total_height = cyl_height + prism_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"BBox Z length: expected {total_height}, got {bb.zlen}"
    
        # Z starts at 0 (cylinder base on XY plane)
        assert abs(bb.zmin - 0.0) < TOL, \
            f"BBox zmin: expected 0.0, got {bb.zmin}"
    
        # Z ends at cyl_height + prism_height = 28
        assert abs(bb.zmax - total_height) < TOL, \
            f"BBox zmax: expected {total_height}, got {bb.zmax}"
    
        # Volume check: cylinder volume + prism volume (they share no overlap since prism sits on top)
        cyl_vol   = math.pi * cyl_radius**2 * cyl_height
        prism_vol = prism_length * prism_width * prism_height
        expected_vol = cyl_vol + prism_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical face exists (the curved side of the cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # The prism sits on top: check a point inside the prism is inside the solid
        prism_center_point = (0, 0, cyl_height + prism_height / 2)
        assert result.val().isInside(prism_center_point), \
            f"Point {prism_center_point} should be inside the prism portion"
    
        # Check a point inside the cylinder is inside the solid
        cyl_center_point = (0, 0, cyl_height / 2)
        assert result.val().isInside(cyl_center_point), \
            f"Point {cyl_center_point} should be inside the cylinder portion"
    
        # Check a point outside the solid is NOT inside
        outside_point = (0, 0, total_height + 10)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00019015/gpt_generated.stl')
