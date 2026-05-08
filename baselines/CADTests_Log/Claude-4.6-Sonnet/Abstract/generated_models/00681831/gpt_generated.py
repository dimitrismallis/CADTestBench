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
        R = 20.0          # circle radius
        height = 10.0     # extrusion height
    
        # Trapezoid cutout (isosceles, centered at top of circle)
        # Bottom edge (inner, shorter): width = 6, at y = 10
        # Top edge (outer, wider): width = 14, at y = 20 (at circle boundary)
        trap_bottom_half = 3.0    # half-width of bottom (inner) edge
        trap_top_half = 7.0       # half-width of top (outer) edge
        trap_y_bottom = 10.0      # y-position of bottom edge
        trap_y_top = R            # y-position of top edge (at circle boundary)
    
        # --- Step 1: Build the 2D profile using Sketch API ---
        # Start with a circle, then subtract the trapezoid
        s = (
            cq.Sketch()
            .circle(R)
            .polygon(
                [
                    (-trap_bottom_half, trap_y_bottom),
                    ( trap_bottom_half, trap_y_bottom),
                    ( trap_top_half,    trap_y_top),
                    (-trap_top_half,    trap_y_top),
                ],
                mode="s"
            )
        )
    
        # --- Step 2: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(s).extrude(height)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X extent: should be 2*R = 40 (circle diameter, trapezoid doesn't exceed it in X)
        assert abs(bb.xlen - 2 * R) < TOL, f"X extent: expected {2*R}, got {bb.xlen}"
    
        # Y min: circle extends to -R on the bottom (no cutout there)
        assert abs(bb.ymin - (-R)) < TOL, f"Y min: expected {-R}, got {bb.ymin}"
    
        # Y max: The trapezoid cuts into the top of the circle. The remaining solid's
        # highest Y point is where the trapezoid's slanted side meets the circle arc.
        # Trapezoid side line from (trap_bottom_half, trap_y_bottom) to (trap_top_half, trap_y_top):
        # x = trap_bottom_half + (y - trap_y_bottom) * (trap_top_half - trap_bottom_half) / (trap_y_top - trap_y_bottom)
        # Intersection with circle x^2 + y^2 = R^2:
        # Line: x = 3 + 0.4*(y-10)
        # (3 + 0.4*(y-10))^2 + y^2 = 400
        # Let u = y-10: (3 + 0.4*u)^2 + (u+10)^2 = 400
        # 1.16u^2 + 22.4u - 291 = 0
        a_coef = 1.16
        b_coef = 22.4
        c_coef = -291.0
        discriminant = b_coef**2 - 4*a_coef*c_coef
        u_sol = (-b_coef + math.sqrt(discriminant)) / (2 * a_coef)
        y_max_expected = u_sol + 10.0  # convert back from u = y-10
    
        assert abs(bb.ymax - y_max_expected) < TOL, \
            f"Y max: expected ~{y_max_expected:.4f}, got {bb.ymax}"
    
        # Z extent: should equal extrusion height
        assert abs(bb.zlen - height) < TOL, f"Z extent: expected {height}, got {bb.zlen}"
    
        # Volume check:
        full_circle_area = math.pi * R ** 2
        full_cyl_vol = full_circle_area * height
        actual_vol = result.val().Volume()
    
        # The cutout must reduce volume: actual < full cylinder
        assert actual_vol < full_cyl_vol, \
            f"Volume should be less than full cylinder {full_cyl_vol:.2f}, got {actual_vol:.2f}"
    
        # The cutout trapezoid (clipped to circle) area is at most the full trapezoid area
        trap_parallel_bottom = 2 * trap_bottom_half   # = 6
        trap_parallel_top = 2 * trap_top_half          # = 14
        trap_height_2d = trap_y_top - trap_y_bottom    # = 10
        trap_area = 0.5 * (trap_parallel_bottom + trap_parallel_top) * trap_height_2d  # = 100
        min_expected_vol = (full_circle_area - trap_area) * height
        assert actual_vol > min_expected_vol, \
            f"Volume {actual_vol:.2f} should be > {min_expected_vol:.2f} (full cyl minus full trapezoid)"
    
        # Volume should be > 85% of full cylinder (small cutout)
        assert actual_vol > 0.85 * full_cyl_vol, \
            f"Volume {actual_vol:.2f} should be > 85% of full cylinder {0.85*full_cyl_vol:.2f}"
    
        # Face count analysis:
        # The trapezoid top corners (±7, 20) lie outside the circle (7²+20²=449>400),
        # so the trapezoid is clipped by the circle boundary. The resulting faces are:
        # 1. Bottom flat face (disk with notch)
        # 2. Top flat face (disk with notch)
        # 3. Outer cylindrical wall (one continuous cylindrical face — OCCT merges the two arcs)
        # 4. Left slanted trapezoid wall
        # 5. Right slanted trapezoid wall
        # 6. Bottom horizontal trapezoid wall (inner shorter edge)
        # Total = 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check cylindrical face exists (outer circle wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check planar faces: bottom + top + 3 trapezoid walls = 5 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 5, f"Expected 5 planar faces, got {planar_faces}"
    
        # Check the solid is NOT inside the trapezoid cutout region (midpoint of trapezoid)
        cutout_point = cq.Vector(0, (trap_y_bottom + trap_y_top) / 2, height / 2)
        solid = result.val()
        assert not solid.isInside(cutout_point), \
            f"Point {cutout_point} should be outside (in cutout), but is inside the solid"
    
        # Check a point inside the solid (bottom of circle, away from cutout)
        inside_point = cq.Vector(0, -R / 2, height / 2)
        assert solid.isInside(inside_point), \
            f"Point {inside_point} should be inside the solid, but is not"
    
        # Check symmetry: center of mass X should be ~0 (symmetric about Y axis)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"Center of mass X should be ~0 (symmetric), got {com.x}"
    
        # Center of mass Z should be at height/2
        assert abs(com.z - height / 2) < TOL, \
            f"Center of mass Z should be {height/2}, got {com.z}"
    
        print(f"All assertions passed!")
        print(f"Volume: {actual_vol:.2f} mm³")
        print(f"Bounding box: X={bb.xlen:.2f}, Y={bb.ylen:.2f}, Z={bb.zlen:.2f}")
        print(f"Y max computed: {y_max_expected:.4f}, actual: {bb.ymax:.4f}")
        print(f"Face count: {face_count}, Cylindrical: {cyl_faces}, Planar: {planar_faces}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681831/gpt_generated.stl')
