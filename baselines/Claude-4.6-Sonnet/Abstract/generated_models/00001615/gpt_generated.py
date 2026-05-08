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
        cyl_diameter = 40.0
        cyl_radius   = cyl_diameter / 2.0   # 20 mm
        cyl_height   = 80.0
    
        cut_diameter_fraction = 1/4   # 1/4 of diameter
        cut_height_fraction   = 1/4   # 1/4 of height
    
        cut_x = cyl_diameter * cut_diameter_fraction   # 10 mm in X
        cut_y = cyl_diameter                            # full diameter in Y (ensures clean cut through)
        cut_z = cyl_height   * cut_height_fraction      # 20 mm in Z
    
        # --- Step 1: Create the base cylinder ---
        # Cylinder centered at origin, axis along Z, so it spans Z = -40 to +40
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Cut a box from the top of the cylinder ---
        # The cut box is placed at the top of the cylinder.
        # It removes a portion that is 1/4 the diameter (10 mm) in X
        # and 1/4 the height (20 mm) in Z from the top.
        # Position the cut box so its top face aligns with the cylinder top (Z = +40)
        # and it sits on the +X side of the cylinder.
        # Box center in X: cyl_radius - cut_x/2 = 20 - 5 = 15 mm (so it spans x=10..20)
        # Box center in Z: cyl_height/2 - cut_z/2 = 40 - 10 = 30 mm (so it spans z=20..40)
        cut_box = (
            cq.Workplane("XY")
            .box(cut_x, cut_y, cut_z, centered=True)
            .translate((cyl_radius - cut_x / 2, 0, cyl_height / 2 - cut_z / 2))
        )
    
        result = result.cut(cut_box)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box: X should still span -20 to +20 (cylinder radius)
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X bounding box: expected {cyl_diameter}, got {bb.xlen}"
    
        # Y bounding box: should still be full diameter (40 mm)
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y bounding box: expected {cyl_diameter}, got {bb.ylen}"
    
        # Z bounding box: should still be full height (80 mm) since cut is from top
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"Z bounding box: expected {cyl_height}, got {bb.zlen}"
    
        # Volume check:
        # Original cylinder volume
        vol_cylinder = math.pi * cyl_radius**2 * cyl_height
        # The cut box volume (but only the part inside the cylinder is removed)
        # The cut box spans x=10..20, y=-20..20, z=20..40
        # The intersection with the cylinder: x in [10,20], y in [-20,20], z in [20,40]
        # This is a rectangular strip at the edge of the cylinder.
        # Compute intersection area in XY: integrate over x from 10 to 20
        # For each x in [10,20], y ranges from -sqrt(400-x^2) to +sqrt(400-x^2)
        # but also clipped to [-20, 20] (which is the full range, so no clipping needed)
        # Area = integral from x=10 to x=20 of 2*sqrt(400 - x^2) dx
        # = [x*sqrt(400-x^2) + 400*arcsin(x/20)] from 10 to 20
        # At x=20: 0 + 400*arcsin(1) = 400*(pi/2) = 200*pi
        # At x=10: 10*sqrt(300) + 400*arcsin(0.5) = 10*sqrt(300) + 400*(pi/6)
        val_at_20 = 400 * math.asin(1.0)
        val_at_10 = 10 * math.sqrt(300) + 400 * math.asin(0.5)
        cut_area_xy = val_at_20 - val_at_10
        vol_cut = cut_area_xy * cut_z
        expected_vol = vol_cylinder - vol_cut
    
        assert abs(solid.Volume() - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {solid.Volume():.2f}"
    
        # The result should have at least one cylindrical face (the main cylinder body)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # The result should have at least one planar face (top, bottom, and cut faces)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 3, \
            f"Expected at least 3 planar faces (bottom, top remainder, cut face), got {planar_faces}"
    
        # Center of mass should be slightly below Z=0 (cut removed material from top)
        com = cq.Shape.centerOfMass(solid)
        assert com.z < 0, \
            f"Center of mass Z should be below 0 (cut from top), got {com.z}"
    
        print(f"Cylinder volume:  {vol_cylinder:.2f} mm³")
        print(f"Cut volume:       {vol_cut:.2f} mm³")
        print(f"Expected volume:  {expected_vol:.2f} mm³")
        print(f"Actual volume:    {solid.Volume():.2f} mm³")
        print(f"Bounding box:     X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Planar faces:     {planar_faces}")
        print(f"Cylindrical faces:{cyl_faces}")
        print(f"Center of mass:   ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00001615/gpt_generated.stl')
