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
        height = 0.09494
        outer_diameter = 1.5
        outer_radius = outer_diameter / 2.0   # 0.75
        hole_diameter = 0.93038
        hole_radius = hole_diameter / 2.0     # 0.46519
    
        # --- Step 1: Create outer cylinder ---
        result = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Create central through-hole ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - outer_diameter) < TOL, f"X bounding box: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, f"Y bounding box: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z bounding box (height): expected {height}, got {bb.zlen}"
    
        # Volume check: annular cylinder volume = pi * (R^2 - r^2) * h
        expected_volume = math.pi * (outer_radius**2 - hole_radius**2) * height
        actual_volume = result.val().Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Face count: 3 faces expected (outer cylinder, inner cylinder, top ring, bottom ring)
        # Actually: outer cylindrical face, inner cylindrical face, top annular face, bottom annular face = 4 faces
        face_count = result.faces().size()
        assert face_count == 4, f"Face count: expected 4, got {face_count}"
    
        # Check cylindrical faces (outer and inner)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Check planar faces (top and bottom annular rings)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 2, f"Planar face count: expected 2, got {planar_face_count}"
    
        # Check center of mass is at origin (symmetric object)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        # Check hole exists: a point at center should be outside the solid
        center_point = (0, 0, 0)
        assert not result.val().isInside(center_point), \
            "Center point should be outside the solid (inside the hole)"
    
        # Check material exists at mid-radius between hole and outer wall
        mid_radius = (outer_radius + hole_radius) / 2.0
        mid_point = (mid_radius, 0, 0)
        assert result.val().isInside(mid_point), \
            f"Mid-radius point {mid_point} should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00003801/gpt_generated.stl')
