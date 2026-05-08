import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        R = 10.0   # Major radius
        r = 1.5    # Minor radius (tube radius)
    
        # --- Step 1: Create torus using shell subtraction approach ---
        # Create outer cylinder and inner cylinder, then intersect with
        # a torus shape built via sweep of a circle along a circular path.
    
        # Build a circular path in the XY plane with radius R
        path = cq.Workplane("XY").circle(R).val()  # Wire
    
        # Build the cross-section profile: a circle of radius r
        # The profile needs to be on a plane perpendicular to the path start tangent
        # At the start of the circle (R, 0, 0), the tangent is (0, 1, 0)
        # So the profile plane has normal (0, 1, 0) and passes through (R, 0, 0)
        profile_plane = cq.Plane(
            origin=(R, 0, 0),
            xDir=(1, 0, 0),
            normal=(0, 1, 0)
        )
        profile = cq.Workplane(profile_plane).circle(r)
    
        # Sweep the profile along the circular path
        result = profile.sweep(path, isFrenet=True)
    
        # --- Final object verification ---
        TOL = 0.15
    
        solid = result.val()
    
        # Bounding box: torus in XY plane
        # X extent: 2*(R+r), Y extent: 2*(R+r), Z extent: 2*r
        bb = solid.BoundingBox()
        expected_diameter = 2 * (R + r)   # 23mm
        expected_thickness = 2 * r        # 3mm
    
        assert abs(bb.xlen - expected_diameter) < TOL, \
            f"X extent: expected {expected_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - expected_diameter) < TOL, \
            f"Y extent: expected {expected_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - expected_thickness) < TOL, \
            f"Z extent (thickness): expected {expected_thickness}, got {bb.zlen}"
    
        # Center of mass should be at origin
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0, got {com.z}"
    
        # Volume of torus = 2 * pi^2 * R * r^2
        expected_vol = 2 * math.pi**2 * R * r**2
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Point on tube centerline should be inside
        assert solid.isInside((R, 0, 0)), \
            f"Point ({R}, 0, 0) should be inside the ring solid"
    
        # Center hole should be outside
        assert not solid.isInside((0, 0, 0)), \
            "Center point (0,0,0) should NOT be inside the ring"
    
        # Point far outside should not be inside
        assert not solid.isInside((R + r + 2, 0, 0)), \
            f"Point outside ring should not be inside solid"
    
        # Inner hole point should be outside
        assert not solid.isInside((R - r - 0.5, 0, 0)), \
            f"Point in the hole of the ring should not be inside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00005358/gpt_generated.stl')
