import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        height       = 0.75
        outer_dia    = 0.85714
        inner_dia    = 0.535714
        outer_radius = outer_dia / 2.0    # 0.42857
        inner_radius = inner_dia / 2.0    # 0.267857
    
        # --- Step 1: Create outer cylinder ---
        result = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Cut inner hole through full height ---
        result = result.faces(">Z").workplane().hole(inner_dia)
    
        # --- Final object verification ---
        TOL = 1e-3
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - outer_dia) < TOL, \
            f"X extent: expected {outer_dia}, got {bb.xlen}"
        assert abs(bb.ylen - outer_dia) < TOL, \
            f"Y extent: expected {outer_dia}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check: pi*(R_outer^2 - R_inner^2)*h
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 2 flat annular faces (top & bottom) + 2 cylindrical faces (outer & inner) = 4
        face_count = result.faces().size()
        assert face_count == 4, \
            f"Face count: expected 4, got {face_count}"
    
        # Cylindrical face count: 2 (outer wall + inner wall)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Planar face count: 2 (top annular + bottom annular)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, \
            f"Planar face count: expected 2, got {planar_face_count}"
    
        # Center of mass should be at origin (symmetric cylinder)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0, got {com.z}"
    
        # Check that a point inside the wall is solid (inside the material)
        mid_r = (outer_radius + inner_radius) / 2.0   # midpoint of wall
        assert solid.isInside((mid_r, 0, 0)), \
            f"Point at mid-wall radius {mid_r} should be inside the solid"
    
        # Check that a point inside the hole is NOT solid
        assert not solid.isInside((0, 0, 0)), \
            "Center point (0,0,0) should be inside the hole, not the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00004495/gpt_generated.stl')
