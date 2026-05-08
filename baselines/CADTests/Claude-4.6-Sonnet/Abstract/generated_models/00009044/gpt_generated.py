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
        cyl_diameter = 150.0   # large diameter
        cyl_height   = 20.0    # short height
        hole_diameter = 15.0   # small central cutout
    
        cyl_radius  = cyl_diameter / 2.0
        hole_radius = hole_diameter / 2.0
    
        # --- Step 1: Create the short, large-diameter cylinder ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Add a small circular cutout at the center ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"Y extent: expected {cyl_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"Z extent: expected {cyl_height}, got {bb.zlen}"
    
        # 2. Volume check: large cylinder minus small hole cylinder
        vol_large = math.pi * cyl_radius**2 * cyl_height
        vol_hole  = math.pi * hole_radius**2 * cyl_height
        expected_vol = vol_large - vol_hole
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Cylindrical faces: outer wall + inner hole wall = 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2 (outer + inner), got {cyl_faces}"
    
        # 4. Planar faces: top and bottom flat rings = 2 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar faces: expected 2 (top + bottom), got {planar_faces}"
    
        # 5. Verify the hole exists at center by checking a point inside the hole
        #    A point at (0, 0, 0) should be OUTSIDE the solid (it's in the hole)
        center_point = (0.0, 0.0, 0.0)
        solid = result.val()
        assert not solid.isInside(center_point), \
            "Center point (0,0,0) should be inside the hole (outside the solid)"
    
        # 6. Verify a point on the large cylinder body IS inside the solid
        body_point = (cyl_radius * 0.5, 0.0, 0.0)
        assert solid.isInside(body_point), \
            f"Body point {body_point} should be inside the solid"
    
        # 7. Verify the center of mass is at the origin (symmetric shape)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009044/gpt_generated.stl')
