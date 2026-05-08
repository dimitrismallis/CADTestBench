import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        d_large = 0.485133
        d_small = 0.157385
        total_length = 0.993343
        extrude_width = 0.243343
    
        r_large = d_large / 2.0   # 0.2425665
        r_small = d_small / 2.0   # 0.0786925
    
        # Center separation = total_length - r_large - r_small
        center_sep = total_length - r_large - r_small
    
        # Large circle center at origin, small circle center at (center_sep, 0)
        cx1, cy1 = 0.0, 0.0
        cx2, cy2 = center_sep, 0.0
    
        # --- External tangent geometry ---
        d = center_sep
        sin_alpha = (r_large - r_small) / d
        cos_alpha = math.sqrt(1.0 - sin_alpha**2)
        alpha = math.asin(sin_alpha)
    
        # Tangent points on large circle:
        # The tangent point on large circle is at angle (pi/2 + alpha) from +x
        t1_upper_x = cx1 + r_large * (-sin_alpha)
        t1_upper_y = cy1 + r_large * cos_alpha
        t1_lower_x = cx1 + r_large * (-sin_alpha)
        t1_lower_y = cy1 - r_large * cos_alpha
    
        # Tangent points on small circle:
        t2_upper_x = cx2 + r_small * (-sin_alpha)
        t2_upper_y = cy2 + r_small * cos_alpha
        t2_lower_x = cx2 + r_small * (-sin_alpha)
        t2_lower_y = cy2 - r_small * cos_alpha
    
        # Arc midpoints:
        arc1_mid_x = cx1 - r_large   # leftmost point of large circle
        arc1_mid_y = cy1
    
        arc2_mid_x = cx2 + r_small   # rightmost point of small circle
        arc2_mid_y = cy2
    
        # --- Build the closed 2D profile ---
        profile = (
            cq.Workplane("XY")
            .moveTo(t1_lower_x, t1_lower_y)
            .threePointArc((arc1_mid_x, arc1_mid_y), (t1_upper_x, t1_upper_y))
            .lineTo(t2_upper_x, t2_upper_y)
            .threePointArc((arc2_mid_x, arc2_mid_y), (t2_lower_x, t2_lower_y))
            .close()
        )
    
        # Extrude the profile
        result = profile.extrude(extrude_width)
    
        # --- Final object verification ---
        TOL = 0.005
    
        bb = result.val().BoundingBox()
    
        print(f"BBox: xlen={bb.xlen:.6f}, ylen={bb.ylen:.6f}, zlen={bb.zlen:.6f}")
    
        # X extent = total_length
        assert abs(bb.xlen - total_length) < TOL, \
            f"X length: expected {total_length}, got {bb.xlen}"
    
        # Y extent = 2 * r_large * cos_alpha (tangent point height)
        expected_ylen = 2.0 * r_large * cos_alpha
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: extrude width
        assert abs(bb.zlen - extrude_width) < TOL, \
            f"Z length: expected {extrude_width}, got {bb.zlen}"
    
        # Z bounds: starts at 0, ends at extrude_width
        assert abs(bb.zmin) < TOL, f"Z min should be ~0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_width) < TOL, \
            f"Z max should be ~{extrude_width}, got {bb.zmax}"
    
        # --- Correct volume calculation using numerical integration ---
        # Compute profile area using Green's theorem by sampling the boundary
        # The boundary consists of:
        # 1. Large arc: from angle -(pi/2+alpha) to +(pi/2+alpha) going CCW through pi
        #    i.e., from angle (3pi/2 - alpha) to (pi/2 + alpha) going CCW
        #    Parametrize: theta from -(pi/2+alpha) to (pi/2+alpha) going through pi
        #    = from -(pi/2+alpha) decreasing (going CCW means increasing angle in standard math)
        #    Actually CCW means angle increases. The arc goes from lower to upper passing through leftmost.
        #    Lower point angle: -(pi/2 + alpha) = -pi/2 - alpha
        #    Upper point angle: pi/2 + alpha
        #    Going CCW (increasing angle) from -pi/2-alpha to pi/2+alpha would go through 0 (right side)
        #    But we want to go through pi (left side), so we go CW or equivalently:
        #    from -pi/2-alpha going in decreasing direction to -(pi) then to pi/2+alpha
        #    OR: from pi/2+alpha to -pi/2-alpha going CCW (increasing) through pi
        #    Let's parametrize: theta from (pi/2+alpha) to (3pi/2-alpha) = -(pi/2+alpha)+2pi
        #    going CCW (increasing theta), passing through pi
    
        N = 10000
    
        # Use Green's theorem: Area = 0.5 * integral(x dy - y dx)
    
        # Segment 1: Large arc from t1_lower to t1_upper going CCW through leftmost point
        # Angles: start = -(pi/2 + alpha), end = pi/2 + alpha, going through pi
        # CCW through pi means: start at -(pi/2+alpha), go to -pi, then to pi, then to pi/2+alpha
        # In terms of increasing angle: from -(pi/2+alpha) we need to go to pi/2+alpha
        # passing through pi. Since -(pi/2+alpha) < 0 < pi/2+alpha, going through pi means
        # going in the negative direction (CW in standard) or equivalently:
        # theta from -(pi/2+alpha) going to -(pi) = -pi, then wrapping to +pi, then to pi/2+alpha
        # Simpler: theta from (pi/2+alpha) down to -(pi/2+alpha) going through pi
        # i.e., theta decreases from pi/2+alpha to -(pi/2+alpha) but passing through pi
        # = theta from pi/2+alpha increases to pi, then continues to 3pi/2-alpha = 2pi-(pi/2+alpha)
        # Let's use: theta from (pi/2+alpha) to (2pi - (pi/2+alpha)) = (3pi/2 - alpha)
        # going in increasing direction (CCW)
    
        theta1_start = math.pi/2 + alpha   # upper tangent point angle
        theta1_end = 2*math.pi - (math.pi/2 + alpha)  # = 3pi/2 - alpha (lower tangent point, going CCW)
    
        thetas1 = np.linspace(theta1_start, theta1_end, N)
        x1 = cx1 + r_large * np.cos(thetas1)
        y1 = cy1 + r_large * np.sin(thetas1)
    
        # Segment 2: Line from t1_upper to t2_upper (already handled by arc endpoint)
        # Wait, I need to reconsider the direction.
        # The profile goes: t1_lower -> (arc CCW through left) -> t1_upper -> line -> t2_upper
        #                   -> (arc CCW through right) -> t2_lower -> line -> t1_lower
    
        # Let me redo with correct parametrization:
        # Large arc: t1_lower to t1_upper going CCW through leftmost (-r_large, 0)
        # t1_lower angle = -(pi/2 + alpha)
        # t1_upper angle = pi/2 + alpha  
        # Going CCW through pi: angles go from -(pi/2+alpha) decreasing to -pi, 
        # then from pi decreasing to pi/2+alpha... that's CW.
        # 
        # Actually "CCW" in standard math = increasing angle.
        # From -(pi/2+alpha) increasing to pi/2+alpha goes through 0 (right side) - WRONG
        # From -(pi/2+alpha) decreasing to -(pi) then to pi/2+alpha... 
        # 
        # The correct path: start at -(pi/2+alpha), go to -pi (= pi), then to pi/2+alpha
        # This means: theta from -(pi/2+alpha) to -(pi) [decreasing, i.e., going CW]
        # then from pi to pi/2+alpha [decreasing, still CW]
        # So the large arc is traversed CLOCKWISE.
        # 
        # For Green's theorem with CCW boundary = positive area:
        # The overall boundary should be CCW for positive area.
        # Let me just compute numerically.
    
        def compute_area_numerical(cx1, cy1, r_large, cx2, cy2, r_small, 
                                    t1_upper_x, t1_upper_y, t1_lower_x, t1_lower_y,
                                    t2_upper_x, t2_upper_y, t2_lower_x, t2_lower_y,
                                    alpha, N=50000):
            """Compute area using Green's theorem: A = 0.5 * sum(x_i*(y_{i+1}-y_{i-1}))"""
    
            # Build boundary points going around the profile
            # Order: t1_lower -> large arc (through left) -> t1_upper -> line -> t2_upper 
            #        -> small arc (through right) -> t2_lower -> line -> t1_lower
    
            # Large arc: from t1_lower to t1_upper going through leftmost point
            # t1_lower is at angle -(pi/2+alpha) on large circle
            # t1_upper is at angle +(pi/2+alpha) on large circle
            # Going through leftmost (angle=pi): 
            #   from -(pi/2+alpha) we go to -pi (same as pi), then to pi/2+alpha
            #   This is going in the NEGATIVE direction (clockwise)
            #   OR equivalently: from -(pi/2+alpha) to -(pi) to -(3pi/2-alpha) = -(pi/2+alpha)-pi
            #   Hmm, let me just use: from angle_start to angle_end going through pi
    
            angle_t1_lower = -(math.pi/2 + alpha)  # negative
            angle_t1_upper = math.pi/2 + alpha      # positive
    
            # Going from t1_lower to t1_upper through pi (leftmost):
            # We go from angle_t1_lower in the negative direction to -pi,
            # then continue (wrapping) to pi, then to angle_t1_upper
            # Total angular span = pi - angle_t1_upper + (pi - abs(angle_t1_lower))
            #                    = pi - (pi/2+alpha) + pi - (pi/2+alpha) = pi - 2*alpha... 
            # Wait: from -(pi/2+alpha) going CW (decreasing angle):
            # -(pi/2+alpha) -> -(pi/2+alpha) - delta -> ... -> -pi
            # then wrapping: -pi = pi, continuing: pi -> pi - delta -> ... -> pi/2+alpha
            # Total span = (pi - (pi/2+alpha)) + (pi - (pi/2+alpha)) = pi - 2*alpha... 
            # No: from -(pi/2+alpha) to -pi is a span of pi - (pi/2+alpha) = pi/2 - alpha
            # from pi to pi/2+alpha is a span of pi - (pi/2+alpha) = pi/2 - alpha
            # Total = pi - 2*alpha... that's less than pi. But the arc should be more than pi!
    
            # I'm confusing myself. Let me think differently.
            # The large arc subtends the angle from t1_lower to t1_upper going through the LEFT side.
            # The angle at center between t1_lower and t1_upper:
            # t1_lower is at angle -(pi/2+alpha), t1_upper is at angle (pi/2+alpha)
            # The SHORT arc (going through right, angle=0) spans: (pi/2+alpha) - (-(pi/2+alpha)) = pi+2*alpha
            # The LONG arc (going through left, angle=pi) spans: 2*pi - (pi+2*alpha) = pi - 2*alpha
            # 
            # Wait, that means the arc through the LEFT is SHORTER (pi-2*alpha < pi)?
            # Let me verify with alpha=21.58 deg:
            # Short arc (through right): pi + 2*21.58*pi/180 = pi + 0.753 = 3.895 rad = 223 deg
            # Long arc (through left): 2*pi - 3.895 = 2.388 rad = 137 deg
            # 
            # Hmm, so the arc through the LEFT is actually the SHORTER one (137 deg)?
            # That seems wrong for a bike chain link shape...
    
            # Let me reconsider: t1_upper_x = -r_large*sin_alpha (negative x)
            # t1_upper_y = r_large*cos_alpha (positive y)
            # This point is in the second quadrant (x<0, y>0)
            # angle = pi - arcsin(cos_alpha)... let me just compute:
            # angle = atan2(r_large*cos_alpha, -r_large*sin_alpha) = atan2(cos_alpha, -sin_alpha)
            # = pi - atan2(cos_alpha, sin_alpha) = pi - (pi/2 - alpha) = pi/2 + alpha ✓
    
            # So t1_upper is at angle pi/2+alpha (second quadrant for alpha < pi/2)
            # t1_lower is at angle -(pi/2+alpha) = -pi/2-alpha (third quadrant)
    
            # Going from t1_lower (angle=-pi/2-alpha) to t1_upper (angle=pi/2+alpha):
            # CCW (increasing angle): span = (pi/2+alpha) - (-pi/2-alpha) = pi + 2*alpha (goes through 0, right side)
            # CW (decreasing angle): span = 2*pi - (pi+2*alpha) = pi - 2*alpha (goes through pi, left side)
    
            # So the arc through the LEFT (leftmost point) is the SHORTER arc (pi-2*alpha)!
            # And the arc through the RIGHT is the LONGER arc (pi+2*alpha).
    
            # For a bike chain link, the large circle is on the LEFT and the small on the RIGHT.
            # The profile wraps around the LEFT side of the large circle (shorter arc)
            # and the RIGHT side of the small circle.
    
            # Large arc (left side, CW from t1_lower to t1_upper through leftmost):
            # Going CW = decreasing angle
            # from -pi/2-alpha, decreasing to -pi (= pi), then to pi/2+alpha
            # Parametrize: theta from -pi/2-alpha to -(pi) [decreasing] then pi to pi/2+alpha
            # Equivalently: theta from pi/2+alpha to -pi/2-alpha going through pi (increasing from pi/2+alpha to pi, then... no)
    
            # Simplest parametrization for CW arc from t1_lower to t1_upper through pi:
            # theta = -pi/2-alpha + t*(-(pi-2*alpha)) for t in [0,1]... 
            # At t=0: theta = -pi/2-alpha (t1_lower) ✓
            # At t=1: theta = -pi/2-alpha - (pi-2*alpha) = -pi/2-alpha-pi+2*alpha = -3pi/2+alpha
            # = -3pi/2+alpha, which should equal pi/2+alpha - 2pi = pi/2+alpha (mod 2pi)? 
            # -3pi/2+alpha + 2pi = pi/2+alpha ✓
    
            # So: theta goes from -pi/2-alpha to -pi/2-alpha-(pi-2*alpha) = -3pi/2+alpha
            # (going in negative/CW direction)
    
            arc1_start = -math.pi/2 - alpha
            arc1_end = -3*math.pi/2 + alpha  # = -(3pi/2 - alpha)
    
            thetas1 = np.linspace(arc1_start, arc1_end, N//4)
            x_arc1 = cx1 + r_large * np.cos(thetas1)
            y_arc1 = cy1 + r_large * np.sin(thetas1)
    
            # Line from t1_upper to t2_upper
            x_line1 = np.linspace(t1_upper_x, t2_upper_x, N//4)
            y_line1 = np.linspace(t1_upper_y, t2_upper_y, N//4)
    
            # Small arc: from t2_upper to t2_lower going through rightmost point (CCW)
            # t2_upper angle on small circle: atan2(r_small*cos_alpha, -r_small*sin_alpha) = pi/2+alpha
            # t2_lower angle: -(pi/2+alpha)
            # Going through rightmost (angle=0): CCW from pi/2+alpha decreasing to 0 to -(pi/2+alpha)
            # That's CW (decreasing). Span = pi+2*alpha (going CW through 0)
            # OR CCW (increasing) from pi/2+alpha to 2pi-(pi/2+alpha) = 3pi/2-alpha, span = pi-2*alpha
    
            # For the profile to be consistent (going around the outside), 
            # the small arc should go CW from t2_upper to t2_lower through rightmost:
            arc2_start = math.pi/2 + alpha   # t2_upper angle
            arc2_end = -(math.pi/2 + alpha)  # t2_lower angle (going CW, decreasing)
            # But going CW from pi/2+alpha to -(pi/2+alpha) through 0:
            # span = pi+2*alpha (CW)
            # Parametrize: theta from pi/2+alpha to -(pi/2+alpha) decreasing
    
            thetas2 = np.linspace(arc2_start, arc2_end, N//4)
            x_arc2 = cx2 + r_small * np.cos(thetas2)
            y_arc2 = cy2 + r_small * np.sin(thetas2)
    
            # Line from t2_lower to t1_lower
            x_line2 = np.linspace(t2_lower_x, t1_lower_x, N//4)
            y_line2 = np.linspace(t2_lower_y, t1_lower_y, N//4)
    
            # Concatenate all boundary points
            x_all = np.concatenate([x_arc1, x_line1, x_arc2, x_line2])
            y_all = np.concatenate([y_arc1, y_line1, y_arc2, y_line2])
    
            # Shoelace formula
            n = len(x_all)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += x_all[i] * y_all[j] - x_all[j] * y_all[i]
            area = abs(area) / 2.0
            return area
    
        area_profile = compute_area_numerical(
            cx1, cy1, r_large, cx2, cy2, r_small,
            t1_upper_x, t1_upper_y, t1_lower_x, t1_lower_y,
            t2_upper_x, t2_upper_y, t2_lower_x, t2_lower_y,
            alpha
        )
    
        expected_vol = area_profile * extrude_width
        actual_vol = result.val().Volume()
    
        print(f"alpha={math.degrees(alpha):.4f} deg")
        print(f"area_profile (numerical)={area_profile:.6f}")
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
    
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 2 flat (top/bottom) + 2 cylindrical (arcs) + 2 planar (tangent sides) = 6
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count == 6, f"Expected 6 faces, got {face_count}"
    
        # Cylindrical faces from the two arcs
        cyl_faces = result.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_faces}")
        assert cyl_faces == 2, f"Expected 2 cylindrical faces, got {cyl_faces}"
    
        # Center of mass checks
        com = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        assert abs(com.z - extrude_width / 2.0) < TOL, \
            f"COM z: expected {extrude_width/2.0:.6f}, got {com.z:.6f}"
        assert abs(com.y) < TOL, f"COM y: expected ~0, got {com.y:.6f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00037276/gpt_generated.stl')
