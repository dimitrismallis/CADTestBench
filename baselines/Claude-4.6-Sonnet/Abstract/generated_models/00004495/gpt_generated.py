import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_radius = 20.0   # mm
        inner_radius = 14.0   # mm
        height       = 40.0   # mm
    
        # --- Step 1: Create the outer solid cylinder ---
        outer = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Subtract the inner cylinder to make it hollow ---
        result = outer.faces(">Z").workplane().circle(inner_radius).cutThruAll()
    
        # --- Final object verification ---
        TOL = 0.05
    
        # 1. Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 2 * outer_radius) < TOL, \
            f"X extent: expected {2*outer_radius}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_radius) < TOL, \
            f"Y extent: expected {2*outer_radius}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z extent: expected {height}, got {bb.zlen}"
    
        # 2. Volume check: annular cross-section × height
        expected_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 3. Face count: 2 cylindrical faces (outer + inner) + 2 flat annular faces (top + bottom) = 4
        total_faces = result.faces().size()
        assert total_faces == 4, \
            f"Face count: expected 4, got {total_faces}"
    
        # 4. Cylindrical face count: exactly 2 (outer wall and inner wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical face count: expected 2, got {cyl_faces}"
    
        # 5. Planar face count: exactly 2 (top and bottom annular rings)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 2, \
            f"Planar face count: expected 2, got {planar_faces}"
    
        # 6. Hollow check: a point at the center axis (inside the hole) should NOT be inside the solid
        center_point = (0.0, 0.0, 0.0)
        assert not result.val().isInside(center_point), \
            "Hollow check failed: center point should be outside (in the hole), but isInside returned True"
    
        # 7. Wall check: a point in the wall material should be inside the solid
        mid_radius = (outer_radius + inner_radius) / 2.0
        wall_point = (mid_radius, 0.0, 0.0)
        assert result.val().isInside(wall_point), \
            f"Wall check failed: point at radius {mid_radius} should be inside the solid"
    
        # 8. Symmetry: center of mass should be at (0, 0, 0)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected 0, got {com.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00004495/gpt_generated.stl')
