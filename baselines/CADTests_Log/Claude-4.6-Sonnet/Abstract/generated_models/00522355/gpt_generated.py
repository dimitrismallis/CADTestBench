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
        outer_radius   = 30.0   # outer radius of the large cylinder
        inner_radius   = 25.0   # inner radius (hollow interior)
        height         = 60.0   # total height of the cylinder
        cap_thickness  = 5.0    # thickness of the bottom cap
        tiny_hole_r    = 3.0    # radius of the tiny hole in the center of the cap
    
        # --- Step 1: Create the outer solid cylinder ---
        # Centered=False in Z so the bottom sits at Z=0
        result = cq.Workplane("XY").cylinder(height, outer_radius)
        # cylinder() centers in Z by default, so it spans Z = -height/2 to +height/2
        # We'll work with it centered at origin (Z from -30 to +30)
    
        # --- Step 2: Subtract the inner cylinder to make the tube hollow ---
        # The inner cutout goes from the top down to cap_thickness above the bottom
        # Bottom of outer cylinder is at Z = -height/2 = -30
        # Cap top surface is at Z = -height/2 + cap_thickness = -25
        # Inner hollow starts at Z = -25 and goes to the top Z = +30
        inner_height = height - cap_thickness  # 55 mm tall inner void
    
        # Place the inner cylinder: its center is at Z = (-height/2 + cap_thickness) + inner_height/2
        inner_center_z = (-height / 2 + cap_thickness) + inner_height / 2
        # = -30 + 5 + 27.5 = 2.5
    
        inner_cyl = cq.Workplane("XY").workplane(offset=inner_center_z).cylinder(inner_height, inner_radius)
        result = result.cut(inner_cyl)
    
        # --- Step 3: Cut a tiny hole through the center of the bottom cap ---
        # The bottom cap spans Z = -30 to Z = -25 (thickness = 5 mm)
        # We cut a small cylinder of radius tiny_hole_r through the entire cap
        tiny_hole = cq.Workplane("XY").workplane(offset=-height / 2).cylinder(cap_thickness, tiny_hole_r)
        result = result.cut(tiny_hole)
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # 1. Bounding box checks
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # 2. Volume check
        # Outer cylinder volume
        vol_outer = math.pi * outer_radius**2 * height
        # Inner hollow volume (above cap)
        vol_inner = math.pi * inner_radius**2 * inner_height
        # Tiny hole volume (through cap)
        vol_tiny  = math.pi * tiny_hole_r**2 * cap_thickness
        expected_vol = vol_outer - vol_inner - vol_tiny
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: outer wall, inner wall, tiny hole wall = 3 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 3, \
            f"Cylindrical faces: expected 3 (outer wall, inner wall, tiny hole), got {cyl_faces}"
    
        # 4. Check the bottom is closed (a point just above the bottom center should be inside)
        bottom_center_inside = solid.isInside((0, 0, -height/2 + cap_thickness/2))
        assert bottom_center_inside, "Bottom cap center should be inside the solid"
    
        # 5. Check the interior hollow is empty (a point in the hollow should be outside)
        hollow_point = solid.isInside((0, 0, 0))  # center of the hollow interior
        assert not hollow_point, "Interior of hollow cylinder should be outside the solid"
    
        # 6. Check the tiny hole is open (a point in the tiny hole should be outside)
        tiny_hole_point = solid.isInside((0, 0, -height/2 + cap_thickness/2))
        # The tiny hole is at center, so (0,0,-27.5) should be outside (inside the hole)
        tiny_hole_center = solid.isInside((0, 0, -height/2 + cap_thickness/4))
        # Actually the tiny hole removes material at center, so (0,0,-28) should be outside
        assert not solid.isInside((0, 0, -height/2 + 1.0)), \
            "Center of bottom cap (within tiny hole) should be outside the solid"
    
        # 7. Check wall material exists (a point in the wall should be inside)
        wall_point = (outer_radius * 0.9, 0, 0)  # in the wall, mid-height
        assert solid.isInside(wall_point), \
            f"Point in cylinder wall {wall_point} should be inside the solid"
    
        # 8. Planar faces: top annular ring, bottom annular ring, inner top ring, cap annular bottom
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 3, \
            f"Planar faces: expected at least 3, got {planar_faces}"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00522355/gpt_generated.stl')
