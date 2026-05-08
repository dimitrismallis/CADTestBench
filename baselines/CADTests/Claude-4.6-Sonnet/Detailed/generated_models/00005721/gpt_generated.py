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
        length = 1.5        # horizontal extent (X)
        width  = 0.73113    # vertical extent (Y)
        depth  = 0.00472    # extrusion depth (Z)
    
        # --- Step 1: Define triangle vertices ---
        half_l = length / 2.0   # 0.75
        half_w = width  / 2.0   # ~0.365565
    
        # Obtuse scalene triangle with apex pointing up.
        #
        # Strategy: place apex slightly right of center so the APEX angle is obtuse.
        # For apex at (ax, hw), the apex angle is obtuse when:
        #   base² > right² + left²
        #   1.5²  > (0.75-ax)² + (2hw)²  +  (0.75+ax)² + (2hw)²
        #   2.25  > 1.125 + 2*ax² + 8*hw²
        # With hw ≈ 0.3656: 8*hw² ≈ 1.069
        #   2.25 > 2.194 + 2*ax²  →  ax² < 0.028  →  ax < 0.167
        #
        # Use apex_x = 0.10 (well within the obtuse range, clearly scalene):
        #   base  ≈ 1.500
        #   right ≈ sqrt(0.4225 + 0.5345) ≈ 0.978
        #   left  ≈ sqrt(0.7225 + 0.5345) ≈ 1.121
        # All sides differ by > 0.10 (scalene), apex angle > 90° (obtuse).
        apex_x = 0.10
    
        p1 = (-half_l, -half_w)   # bottom-left
        p2 = ( half_l, -half_w)   # bottom-right
        p3 = ( apex_x,  half_w)   # apex (pointing up)
    
        # Compute side lengths for verification
        def dist(a, b):
            return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)
    
        s_base  = dist(p1, p2)  # base: p1-p2 (opposite apex p3)
        s_right = dist(p2, p3)  # right side: p2-p3 (opposite p1)
        s_left  = dist(p3, p1)  # left side:  p3-p1 (opposite p2)
    
        # Angles using law of cosines
        def angle_at_vertex(opp, adj1, adj2):
            cos_a = (adj1**2 + adj2**2 - opp**2) / (2.0 * adj1 * adj2)
            cos_a = max(-1.0, min(1.0, cos_a))
            return math.degrees(math.acos(cos_a))
    
        angle_p1 = angle_at_vertex(s_right, s_base,  s_left)
        angle_p2 = angle_at_vertex(s_left,  s_base,  s_right)
        angle_p3 = angle_at_vertex(s_base,  s_right, s_left)
    
        print(f"Vertices: p1={p1}, p2={p2}, p3=({apex_x}, {half_w:.6f})")
        print(f"Side lengths: base={s_base:.5f}, right={s_right:.5f}, left={s_left:.5f}")
        print(f"Angles: p1={angle_p1:.2f}°, p2={angle_p2:.2f}°, p3={angle_p3:.2f}°")
        print(f"Sum of angles: {angle_p1+angle_p2+angle_p3:.2f}°")
    
        # --- Step 2: Build the 2D triangle profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .lineTo(p3[0], p3[1])
            .close()
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
        print(f"Bounding box: xlen={bb.xlen:.5f}, ylen={bb.ylen:.5f}, zlen={bb.zlen:.5f}")
        print(f"  xmin={bb.xmin:.5f}, xmax={bb.xmax:.5f}")
        print(f"  ymin={bb.ymin:.5f}, ymax={bb.ymax:.5f}")
        print(f"  zmin={bb.zmin:.5f}, zmax={bb.zmax:.5f}")
    
        # Bounding box checks
        assert abs(bb.xlen - length) < TOL, \
            f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, \
            f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, \
            f"Z depth: expected {depth}, got {bb.zlen}"
    
        # Centering: bounding box should be centered near origin in X and Y
        assert abs(bb.xmin + bb.xmax) < TOL, \
            f"X not centered: xmin={bb.xmin}, xmax={bb.xmax}"
        assert abs(bb.ymin + bb.ymax) < TOL, \
            f"Y not centered: ymin={bb.ymin}, ymax={bb.ymax}"
    
        # Z should go from 0 to depth
        assert abs(bb.zmin) < TOL, \
            f"Z min should be ~0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, \
            f"Z max should be ~{depth}, got {bb.zmax}"
    
        # Volume: triangle area * depth = 0.5 * base * height * depth
        triangle_area = 0.5 * length * width
        expected_vol  = triangle_area * depth
        actual_vol    = result.val().Volume()
        print(f"Volume: expected={expected_vol:.8f}, actual={actual_vol:.8f}")
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume mismatch: expected {expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Face count: triangular prism has 5 faces (2 triangular + 3 rectangular)
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count == 5, \
            f"Expected 5 faces for triangular prism, got {face_count}"
    
        # Edge count: triangular prism has 9 edges
        edge_count = result.edges().size()
        print(f"Edge count: {edge_count}")
        assert edge_count == 9, \
            f"Expected 9 edges for triangular prism, got {edge_count}"
    
        # Vertex count: triangular prism has 6 vertices
        vertex_count = result.vertices().size()
        print(f"Vertex count: {vertex_count}")
        assert vertex_count == 6, \
            f"Expected 6 vertices for triangular prism, got {vertex_count}"
    
        # Scalene: all three side lengths must differ by more than 0.10
        SCALENE_TOL = 0.10
        diff_base_right = abs(s_base  - s_right)
        diff_right_left = abs(s_right - s_left)
        diff_base_left  = abs(s_base  - s_left)
        print(f"Side differences: |base-right|={diff_base_right:.5f}, "
              f"|right-left|={diff_right_left:.5f}, |base-left|={diff_base_left:.5f}")
        assert diff_base_right > SCALENE_TOL, \
            f"Triangle not scalene: base={s_base:.5f} ≈ right={s_right:.5f} (diff={diff_base_right:.5f})"
        assert diff_right_left > SCALENE_TOL, \
            f"Triangle not scalene: right={s_right:.5f} ≈ left={s_left:.5f} (diff={diff_right_left:.5f})"
        assert diff_base_left  > SCALENE_TOL, \
            f"Triangle not scalene: base={s_base:.5f} ≈ left={s_left:.5f} (diff={diff_base_left:.5f})"
    
        # Obtuse: the apex angle (p3) must be > 90° by design (ax=0.10 < 0.167 threshold)
        # Also verify at least one angle is obtuse
        angles = [angle_p1, angle_p2, angle_p3]
        obtuse_angles = [a for a in angles if a > 90.0]
        assert len(obtuse_angles) >= 1, \
            f"Triangle not obtuse: angles={[f'{a:.2f}' for a in angles]}"
        assert all(a < 180.0 for a in obtuse_angles), \
            f"An angle >= 180°: {[f'{a:.2f}' for a in obtuse_angles]}"
    
        # Apex faces upward: apex vertex (p3) has maximum Y coordinate
        assert p3[1] > p1[1] and p3[1] > p2[1], \
            f"Apex not pointing up: p3={p3}, p1={p1}, p2={p2}"
    
        # Verify the apex angle specifically is obtuse (by law of cosines on actual sides)
        cos_apex = (s_right**2 + s_left**2 - s_base**2) / (2.0 * s_right * s_left)
        assert cos_apex < 0.0, \
            f"Apex angle not obtuse: cos(apex)={cos_apex:.5f} (should be < 0)"
    
        print(f"\nAll assertions passed!")
        print(f"Obtuse angle at apex: {angle_p3:.2f}°")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00005721/gpt_generated.stl')
