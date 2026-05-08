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
        base_length = 60.0   # X dimension (larger side)
        base_width  = 20.0   # Y dimension (depth)
        base_height = 40.0   # Z dimension
    
        # Cutout: larger side ~2/3 of base_length = 40
        cut_length  = 40.0   # X dimension of cutout (2/3 of 60)
        cut_depth   = 30.0   # How deep the cutout goes from the top (leaves 10 at bottom)
    
        # --- Step 1: Create the base rectangular block centered at origin ---
        # Block spans X: -30..+30, Y: -10..+10, Z: -20..+20
        base = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # --- Step 2: Create the cutting box ---
        # Cutout is centered in X (X: -20..+20), full Y depth, from top down by cut_depth
        # Top of base is at Z=+20, cutout floor at Z = 20 - 30 = -10
        # Cutter box center: X=0, Y=0, Z = (20 + (-10))/2 = +5
        # Cutter dimensions: 40 x (base_width+2) x 30
        cutter_height = cut_depth          # 30
        cutter_z_center = (base_height / 2.0) - (cut_depth / 2.0)  # 20 - 15 = +5
    
        cutter = (
            cq.Workplane("XY")
            .box(cut_length, base_width + 2.0, cutter_height,
                 centered=(True, True, True))
            .translate((0, 0, cutter_z_center))
        )
    
        # --- Step 3: Subtract the cutter from the base to form the U-shape ---
        result = base.cut(cutter)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box should still be the original base dimensions
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Y width:  expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, \
            f"Z height: expected {base_height}, got {bb.zlen}"
    
        # Volume check:
        # Base volume minus cutout volume (clamped to base_width in Y)
        base_vol     = base_length * base_width * base_height   # 60*20*40 = 48000
        cut_vol      = cut_length  * base_width * cut_depth     # 40*20*30 = 24000
        expected_vol = base_vol - cut_vol                       # 24000
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # No cylindrical faces expected
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # U-shape planar face count = 10:
        # Bottom(1) + left outer(1) + right outer(1) + front(1) + back(1)
        # + top-left ledge(1) + top-right ledge(1)
        # + inner left wall(1) + inner right wall(1) + cutout floor(1)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 10, \
            f"Expected 10 planar faces, got {planar_faces}"
    
        # Bottom face at Z = -base_height/2 = -20
        assert abs(bb.zmin - (-base_height / 2.0)) < TOL, \
            f"Bottom Z: expected {-base_height/2.0}, got {bb.zmin}"
    
        # Top of solid at Z = +base_height/2 = +20
        assert abs(bb.zmax - (base_height / 2.0)) < TOL, \
            f"Top Z: expected {base_height/2.0}, got {bb.zmax}"
    
        solid = result.val()
    
        # Cutout floor at Z = +20 - 30 = -10
        cutout_floor_z = (base_height / 2.0) - cut_depth   # -10
    
        # Point inside the cutout channel should be OUTSIDE the solid
        point_in_cutout = cq.Vector(0, 0, 0)   # Z=0 is within the cutout (between Z=-10 and Z=+20)
        assert not solid.isInside(point_in_cutout), \
            "Point (0,0,0) should be OUTSIDE the solid (inside the cutout channel)"
    
        # Point below the cutout floor should be INSIDE the solid
        point_below_cut = cq.Vector(0, 0, cutout_floor_z - 5)   # (0, 0, -15)
        assert solid.isInside(point_below_cut), \
            f"Point (0,0,{cutout_floor_z-5:.1f}) should be INSIDE the solid (below cutout floor)"
    
        # Point in the right leg should be INSIDE the solid
        # Right leg spans X: +20..+30, so X=25 is in the leg
        point_in_leg = cq.Vector(25, 0, 0)
        assert solid.isInside(point_in_leg), \
            f"Point (25,0,0) should be INSIDE the solid (in the right leg)"
    
        # Symmetry: center of mass at X=0, Y=0
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00682073/gpt_generated.stl')
