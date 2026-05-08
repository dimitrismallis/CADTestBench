import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    import numpy as np
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        R = 20.0        # large circle radius
        r = 8.0         # small circle radius
        d = 40.0        # center-to-center distance (≈ diameter of large circle)
        extrude_h = 5.0 # extrusion height
    
        # Centers
        C1 = (0.0, 0.0)   # large circle center
        C2 = (d, 0.0)     # small circle center
    
        # --- Step 1: Compute external tangent geometry ---
        # For external tangents between two circles of radii R and r (R > r),
        # separated by distance d:
        # The angle alpha = arcsin((R - r) / d)
        # This is the angle the tangent line makes with the line of centers.
        alpha = math.asin((R - r) / d)
    
        # Tangent points on large circle (top and bottom):
        # The radius to the tangent point is perpendicular to the tangent line.
        # Tangent line direction: (cos(alpha), sin(alpha)) for top tangent
        # Radius direction (perpendicular to tangent, pointing from center to tangent point):
        # rotated 90° from tangent direction = (-sin(alpha), cos(alpha)) for top
        # Top tangent point on large circle:
        T1_top = (C1[0] + R * (-math.sin(alpha)), C1[1] + R * math.cos(alpha))
        # Top tangent point on small circle:
        T2_top = (C2[0] + r * (-math.sin(alpha)), C2[1] + r * math.cos(alpha))
    
        # Bottom tangent points (mirror in x-axis):
        T1_bot = (T1_top[0], -T1_top[1])
        T2_bot = (T2_top[0], -T2_top[1])
    
        # --- Step 2: Compute arc angles for each circle ---
        # Large circle: arc goes from T1_bot (bottom tangent point) 
        # counterclockwise to T1_top (top tangent point) — the LEFT arc (around left side)
        # Small circle: arc goes from T2_top (top tangent point)
        # counterclockwise to T2_bot (bottom tangent point) — the RIGHT arc (around right side)
    
        # Angle of T1_top on large circle (from center C1):
        angle_T1_top = math.atan2(T1_top[1] - C1[1], T1_top[0] - C1[0])
        angle_T1_bot = math.atan2(T1_bot[1] - C1[1], T1_bot[0] - C1[0])
    
        # Angle of T2_top on small circle (from center C2):
        angle_T2_top = math.atan2(T2_top[1] - C2[1], T2_top[0] - C2[0])
        angle_T2_bot = math.atan2(T2_bot[1] - C2[1], T2_bot[0] - C2[0])
    
        # Convert to degrees
        a1_top_deg = math.degrees(angle_T1_top)  # ~(90 + alpha_deg)
        a1_bot_deg = math.degrees(angle_T1_bot)  # ~-(90 + alpha_deg)
        a2_top_deg = math.degrees(angle_T2_top)
        a2_bot_deg = math.degrees(angle_T2_bot)
    
        # --- Step 3: Build the closed wire profile ---
        # Profile path (counterclockwise):
        # 1. Start at T1_bot (bottom tangent on large circle)
        # 2. Arc CCW around large circle from T1_bot to T1_top (left side arc)
        # 3. Line from T1_top to T2_top (top tangent line)
        # 4. Arc CCW around small circle from T2_top to T2_bot (right side arc)
        # 5. Line from T2_bot to T1_bot (bottom tangent line, closes shape)
    
        # For CadQuery arcs, we need a midpoint on the arc.
        # Large circle left arc midpoint (at angle 180°):
        mid_large = (C1[0] + R * math.cos(math.pi), C1[1] + R * math.sin(math.pi))
        # = (-R, 0) = (-20, 0)
    
        # Small circle right arc midpoint (at angle 0°):
        mid_small = (C2[0] + r * math.cos(0), C2[1] + r * math.sin(0))
        # = (d + r, 0) = (48, 0)
    
        # Build the wire using CadQuery's 2D drawing tools
        result = (
            cq.Workplane("XY")
            .moveTo(T1_bot[0], T1_bot[1])
            .threePointArc(mid_large, T1_top)
            .lineTo(T2_top[0], T2_top[1])
            .threePointArc(mid_small, T2_bot)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box X: from -R to d+r = -20 to 48, so xlen = 68
        expected_xlen = d + r + R  # 40 + 8 + 20 = 68
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Bounding box Y: from -(R*cos(alpha)) to +(R*cos(alpha))
        expected_half_y = R * math.cos(alpha)
        expected_ylen = 2 * expected_half_y
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
    
        # Bounding box Z: extrusion height
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h}, got {bb.zlen}"
    
        # Volume check: approximate area of the profile * height
        # Area = rectangle-like shape + two semicircle caps
        # More precisely: area = d * 2*R*cos(alpha) + pi*R^2 + pi*r^2 - (R-r)*d*sin(alpha)... 
        # Use a simpler bound: volume should be between (d * 2*r * extrude_h) and (d * 2*R * extrude_h + pi*R^2*extrude_h)
        vol = result.val().Volume()
        vol_min = d * 2 * r * extrude_h  # conservative lower bound
        vol_max = (d * 2 * R + math.pi * R**2 + math.pi * r**2) * extrude_h  # upper bound
        assert vol > vol_min, f"Volume too small: {vol:.1f} < {vol_min:.1f}"
        assert vol < vol_max, f"Volume too large: {vol:.1f} > {vol_max:.1f}"
    
        # Should have exactly 1 solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Should have 2 flat (planar) faces on top and bottom (Z faces)
        z_faces = result.faces("|Z").size()
        assert z_faces == 2, f"Expected 2 Z-parallel faces (top/bottom), got {z_faces}"
    
        # Should have 4 lateral faces: 2 cylindrical (arcs) + 2 planar (tangent lines)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Expected 2 cylindrical faces, got {cyl_faces}"
    
        plane_faces = result.faces("%Plane").size()
        # 2 top/bottom + 2 tangent line sides = 4 planar faces
        assert plane_faces == 4, f"Expected 4 planar faces, got {plane_faces}"
    
        # Center of mass should be roughly between the two circle centers
        com = cq.Shape.centerOfMass(result.val())
        assert 0 < com.x < d, f"Center of mass X should be between 0 and {d}, got {com.x:.3f}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y:.3f}"
        assert abs(com.z - extrude_h / 2) < TOL, \
            f"Center of mass Z should be ~{extrude_h/2}, got {com.z:.3f}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {vol:.2f}")
        print(f"Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
        print(f"Tangent angle alpha: {math.degrees(alpha):.2f}°")
        print(f"T1_top: {T1_top}, T1_bot: {T1_bot}")
        print(f"T2_top: {T2_top}, T2_bot: {T2_bot}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00037276/gpt_generated.stl')
