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
        height = 0.010714
        outer_diameter = 1.5
        outer_radius = outer_diameter / 2  # 0.75
        inner_diameter = outer_diameter - 0.342858  # 1.157142
        inner_radius = inner_diameter / 2  # 0.578571
    
        hole_diameter = 0.105429
        hole_radius = hole_diameter / 2  # 0.0527145
    
        # Hole center radius: outer_radius - (outer_diameter - inner_diameter) / 4
        wall_thickness = outer_diameter - inner_diameter  # 0.342858
        hole_center_radius = outer_radius - wall_thickness / 4  # 0.75 - 0.085714 = 0.664286
    
        # --- Step 1: Create the outer cylinder ---
        ring = cq.Workplane("XY").cylinder(height, outer_radius)
    
        # --- Step 2: Cut the inner cylinder to make the ring (annulus) ---
        ring = ring.cut(
            cq.Workplane("XY").cylinder(height, inner_radius)
        )
    
        # --- Step 3: Create three holes in triangular formation (120° apart) ---
        # Hole centers at angles 0°, 120°, 240°
        angles = [0, 120, 240]
        for angle_deg in angles:
            angle_rad = math.radians(angle_deg)
            cx = hole_center_radius * math.cos(angle_rad)
            cy = hole_center_radius * math.sin(angle_rad)
            hole_cyl = cq.Workplane("XY").center(cx, cy).cylinder(height, hole_radius)
            ring = ring.cut(hole_cyl)
    
        # --- Step 4: Rotate -90 degrees around Z-axis ---
        ring = ring.rotate((0, 0, 0), (0, 0, 1), -90)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = ring.val()
        bb = solid.BoundingBox()
    
        # Bounding box should be approximately outer_diameter x outer_diameter x height
        assert abs(bb.xlen - outer_diameter) < TOL, f"X extent: expected {outer_diameter}, got {bb.xlen}"
        assert abs(bb.ylen - outer_diameter) < TOL, f"Y extent: expected {outer_diameter}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # Ring volume = pi * (outer_r^2 - inner_r^2) * height
        # Minus 3 holes = 3 * pi * hole_r^2 * height
        ring_vol = math.pi * (outer_radius**2 - inner_radius**2) * height
        holes_vol = 3 * math.pi * hole_radius**2 * height
        expected_vol = ring_vol - holes_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Check cylindrical faces:
        # outer cylinder face, inner cylinder face, 3 hole cylinder faces = 5 cylindrical faces
        cyl_faces = ring.faces("%Cylinder").size()
        assert cyl_faces == 5, f"Cylindrical faces: expected 5, got {cyl_faces}"
    
        # Check that the ring has flat top and bottom faces (at least 2 planar faces)
        planar_faces = ring.faces("%Plane").size()
        assert planar_faces >= 2, f"Planar faces: expected at least 2, got {planar_faces}"
    
        # Check center of mass is near origin (symmetric ring)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
        assert abs(com.z) < TOL, f"Center of mass Z: expected ~0, got {com.z}"
    
        # Check that a point inside the ring material is inside the solid.
        # Use angle 60° (midway between holes at 0° and 120°) before rotation,
        # then apply -90° rotation: (x,y) -> (y, -x)
        mid_wall_r = (outer_radius + inner_radius) / 2  # midpoint of wall thickness
        orig_x = mid_wall_r * math.cos(math.radians(60))
        orig_y = mid_wall_r * math.sin(math.radians(60))
        # After -90° rotation around Z: x' = y, y' = -x
        test_x = orig_y
        test_y = -orig_x
        test_point = (test_x, test_y, 0)
        assert solid.isInside(test_point), \
            f"Point {test_point} should be inside the ring material"
    
        # Check that a point at the center (inside the hollow) is NOT inside the solid
        center_point = (0, 0, 0)
        assert not solid.isInside(center_point), \
            f"Center point should be inside the hollow of the ring"
    
        # Check that a point well outside the ring is NOT inside the solid
        outside_point = (outer_radius + 0.1, 0, 0)
        assert not solid.isInside(outside_point), \
            f"Outside point {outside_point} should not be inside the ring"
    
        print("All assertions passed!")
        print(f"  Outer diameter: {outer_diameter}")
        print(f"  Inner diameter: {inner_diameter:.6f}")
        print(f"  Height: {height}")
        print(f"  Hole diameter: {hole_diameter}")
        print(f"  Hole center radius: {hole_center_radius:.6f}")
        print(f"  Volume: {actual_vol:.8f} (expected {expected_vol:.8f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Planar faces: {planar_faces}")
    
        return ring
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521000/gpt_generated.stl')
