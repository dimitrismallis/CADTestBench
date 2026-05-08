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
        large_diameter = 0.059646
        large_radius   = large_diameter / 2          # 0.029823
        large_height   = 0.750036
    
        small_diameter = large_diameter / 2          # 0.029823
        small_radius   = small_diameter / 2          # 0.0149115
        small_height   = large_height * 5            # 3.75018
    
        # --- Step 1: Create the large cylinder centered at origin ---
        # Large cylinder: Z from -large_height/2 to +large_height/2
        large_cyl = cq.Workplane("XY").cylinder(large_height, large_radius)
    
        # --- Step 2: Create the small cylinder below the large cylinder ---
        # Bottom of large cylinder is at Z = -large_height/2
        # Small cylinder center Z = -large_height/2 - small_height/2
        small_cyl_center_z = -large_height / 2 - small_height / 2
    
        small_cyl = (
            cq.Workplane("XY")
            .workplane(offset=small_cyl_center_z)
            .cylinder(small_height, small_radius)
        )
    
        # --- Step 3: Union the two cylinders ---
        result = large_cyl.union(small_cyl)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X and Y extents should be dominated by the large cylinder (wider)
        expected_xlen = large_diameter
        expected_ylen = large_diameter
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BBox X: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BBox Y: expected {expected_ylen}, got {bb.ylen}"
    
        # Total Z extent: large_height + small_height
        expected_zlen = large_height + small_height   # 0.750036 + 3.75018 = 4.500216
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents
        expected_zmax = large_height / 2             # +0.375018
        expected_zmin = -(large_height / 2 + small_height)  # -4.125198
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"BBox Zmax: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"BBox Zmin: expected {expected_zmin}, got {bb.zmin}"
    
        # Volume check: sum of two cylinders (no overlap)
        vol_large = math.pi * large_radius**2 * large_height
        vol_small = math.pi * small_radius**2 * small_height
        expected_vol = vol_large + vol_small
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Face counts - inspect what we actually have
        total_faces = result.faces().size()
        cyl_faces   = result.faces("%Cylinder").size()
        planar_faces = result.faces("%Plane").size()
    
        # The union of two coaxial cylinders (large on top, small below) produces:
        # - 1 curved face for the large cylinder body
        # - 1 curved face for the small cylinder body  (may be split by OCCT = 2)
        # - 1 top planar face (top of large cylinder)
        # - 1 annular planar face at junction (bottom of large, minus small hole)
        # - 1 bottom planar face (bottom of small cylinder)
        # Total planar = 3, cylindrical = 2 or 3
        assert planar_faces == 3, \
            f"Planar faces: expected 3, got {planar_faces}"
        assert cyl_faces >= 2, \
            f"Cylindrical faces: expected at least 2, got {cyl_faces}"
        assert total_faces == planar_faces + cyl_faces, \
            f"Total faces mismatch: {total_faces} != {planar_faces} + {cyl_faces}"
    
        # Top face at Z = +large_height/2
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - expected_zmax) < TOL, \
            f"Top face Z center: expected {expected_zmax}, got {top_face_z}"
    
        # Bottom face at Z = expected_zmin
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - expected_zmin) < TOL, \
            f"Bottom face Z center: expected {expected_zmin}, got {bot_face_z}"
    
        # Center of mass should be on Z-axis (x=0, y=0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
    
        # Check a point inside the small cylinder shaft is inside the solid
        mid_small_z = -large_height / 2 - small_height / 2
        assert result.val().isInside((0, 0, mid_small_z)), \
            "Point at center of small cylinder should be inside the solid"
    
        # Check a point outside the small cylinder (but within large cylinder radius) is outside
        outside_pt = (large_radius * 0.9, 0, mid_small_z)
        assert not result.val().isInside(outside_pt), \
            f"Point at {outside_pt} should be outside the solid (beyond small cylinder radius)"
    
        # Check a point inside the large cylinder is inside
        assert result.val().isInside((0, 0, 0)), \
            "Point at origin should be inside the large cylinder"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521217/gpt_generated.stl')
