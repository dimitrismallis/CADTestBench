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
        cyl1_diameter = 0.38527
        cyl1_radius   = cyl1_diameter / 2.0   # 0.192635
        cyl1_height   = 0.256849
    
        cyl2_diameter = 0.256849
        cyl2_radius   = cyl2_diameter / 2.0   # 0.1284245
        cyl2_height   = 0.493151
    
        # --- Step 1: First cylinder centered at origin ---
        # Spans Z from -cyl1_height/2 to +cyl1_height/2
        cyl1 = cq.Workplane("XY").cylinder(cyl1_height, cyl1_radius)
    
        # --- Step 2: Second cylinder connected to center of first cylinder's base ---
        # Base of first cylinder is at Z = -cyl1_height/2
        # Second cylinder extends downward from there
        # Center of second cylinder is at Z = -cyl1_height/2 - cyl2_height/2
        cyl2_center_z = -cyl1_height / 2.0 - cyl2_height / 2.0
    
        cyl2 = cq.Workplane(cq.Plane(origin=(0, 0, cyl2_center_z), normal=(0, 0, 1))).cylinder(cyl2_height, cyl2_radius)
    
        # --- Step 3: Union the two cylinders ---
        result = cyl1.union(cyl2)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: should be the wider cylinder (cyl1) diameter
        assert abs(bb.xlen - cyl1_diameter) < TOL, \
            f"X extent: expected {cyl1_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - cyl1_diameter) < TOL, \
            f"Y extent: expected {cyl1_diameter}, got {bb.ylen}"
    
        # Total height: cyl1_height + cyl2_height
        total_height = cyl1_height + cyl2_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z extent (total height): expected {total_height}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmax - cyl1_height / 2.0) < TOL, \
            f"Z max: expected {cyl1_height/2.0}, got {bb.zmax}"
        assert abs(bb.zmin - (-cyl1_height / 2.0 - cyl2_height)) < TOL, \
            f"Z min: expected {-cyl1_height/2.0 - cyl2_height}, got {bb.zmin}"
    
        # Volume check: sum of both cylinders (they share only a circle at the interface, no overlap volume)
        vol_cyl1 = math.pi * cyl1_radius**2 * cyl1_height
        vol_cyl2 = math.pi * cyl2_radius**2 * cyl2_height
        expected_vol = vol_cyl1 + vol_cyl2
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Cylindrical faces: should have 2 cylindrical faces (one per cylinder)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Center of mass should be on the Z axis (X=0, Y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # The top face (max Z) should be at cyl1_height/2
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - cyl1_height / 2.0) < TOL, \
            f"Top face Z center: expected {cyl1_height/2.0}, got {top_face_z}"
    
        # The bottom face (min Z) should be at -(cyl1_height/2 + cyl2_height)
        bot_face_z = result.faces("<Z").val().Center().z
        expected_bot_z = -(cyl1_height / 2.0 + cyl2_height)
        assert abs(bot_face_z - expected_bot_z) < TOL, \
            f"Bottom face Z center: expected {expected_bot_z}, got {bot_face_z}"
    
        # Check that a point inside cyl1 (but outside cyl2 radius) is inside the solid
        point_in_cyl1 = (cyl1_radius * 0.8, 0, 0)
        assert result.val().isInside(point_in_cyl1), \
            f"Point {point_in_cyl1} should be inside cyl1"
    
        # Check that a point inside cyl2 (at its mid-height) is inside the solid
        cyl2_mid_z = -(cyl1_height / 2.0 + cyl2_height / 2.0)
        point_in_cyl2 = (cyl2_radius * 0.5, 0, cyl2_mid_z)
        assert result.val().isInside(point_in_cyl2), \
            f"Point {point_in_cyl2} should be inside cyl2"
    
        # Check that a point outside cyl1 radius at cyl1 height is NOT inside
        point_outside = (cyl1_radius * 1.5, 0, 0)
        assert not result.val().isInside(point_outside), \
            f"Point {point_outside} should be outside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00005161/gpt_generated.stl')
