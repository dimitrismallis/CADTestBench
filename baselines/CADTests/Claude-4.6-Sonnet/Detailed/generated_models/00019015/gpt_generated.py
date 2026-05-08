import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        cyl_height = 0.468766
        cyl_diameter = 1.31858
        cyl_radius = cyl_diameter / 2.0  # 0.65929
    
        prism_length = 1.5
        prism_width = 0.1875
        prism_height = 0.075
    
        # --- Step 1: Create the cylinder centered at origin ---
        # cylinder() centers at origin: top at Z = cyl_height/2, bottom at Z = -cyl_height/2
        cylinder = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Create the rectangular prism ---
        # The prism must sit on top of the cylinder.
        # Cylinder top face is at Z = cyl_height / 2
        # Prism bottom should be at Z = cyl_height / 2
        # Prism center Z = cyl_height/2 + prism_height/2
        prism_center_z = cyl_height / 2.0 + prism_height / 2.0
    
        prism = (
            cq.Workplane("XY")
            .box(prism_length, prism_width, prism_height,
                 centered=(True, True, True))
            .translate((0, 0, prism_center_z))
        )
    
        # --- Step 3: Union the cylinder and the prism ---
        result = cylinder.union(prism)
    
        # --- Final object verification ---
        TOL = 0.001
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: max of cylinder diameter and prism length
        expected_xlen = max(cyl_diameter, prism_length)  # 1.5
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: max of cylinder diameter and prism width
        expected_ylen = max(cyl_diameter, prism_width)  # 1.31858
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent: cylinder height + prism height (prism sits on top)
        expected_zlen = cyl_height + prism_height  # 0.468766 + 0.075 = 0.543766
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Z min should be at -cyl_height/2 (bottom of cylinder)
        expected_zmin = -cyl_height / 2.0
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
    
        # Z max should be at cyl_height/2 + prism_height (top of prism)
        expected_zmax = cyl_height / 2.0 + prism_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
    
        # Volume check: cylinder volume + prism volume (they may overlap slightly at the top face, but overlap is negligible)
        cyl_vol = math.pi * (cyl_radius ** 2) * cyl_height
        prism_vol = prism_length * prism_width * prism_height
        # The prism sits exactly on top, so overlap is zero (they share a face, not volume)
        expected_vol = cyl_vol + prism_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the center of the model is roughly above the cylinder center in XY
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X should be ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y should be ~0, got {center.y}"
    
        # Check cylindrical face exists (the cylinder's curved surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check there is exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00019015/gpt_generated.stl')
