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
        cube_size = 0.747683
        tri_base = 0.498375   # base and height of right triangle
        tri_extrusion = cube_size  # extrusion length equals cube's length
    
        half_cube = cube_size / 2.0  # 0.373842 (approx)
    
        # --- Step 1: Large cube centered at origin ---
        cube = cq.Workplane("XY").box(cube_size, cube_size, cube_size)
    
        # --- Step 2: Right triangular prism ---
        # The right triangle has legs of length tri_base (0.498375) in X and Y.
        # We place the right-angle vertex at the cube corner (+X, +Y side),
        # so two long edges of the prism align with two edges of the cube.
        # The prism is extruded along Z with the same height as the cube.
        #
        # Triangle vertices in XY plane (right angle at cube corner):
        #   P0 = (half_cube, half_cube)           <- right-angle vertex, at cube corner
        #   P1 = (half_cube + tri_base, half_cube) <- along +X
        #   P2 = (half_cube, half_cube + tri_base) <- along +Y
        #
        # The prism is extruded from Z = -half_cube to Z = +half_cube (same as cube).
    
        prism = (
            cq.Workplane("XY")
            .workplane(offset=-half_cube)  # start at bottom of cube's Z range
            .moveTo(half_cube, half_cube)
            .lineTo(half_cube + tri_base, half_cube)
            .lineTo(half_cube, half_cube + tri_base)
            .close()
            .extrude(tri_extrusion)
        )
    
        # --- Step 3: Combine both shapes (union — they touch at an edge) ---
        result = cube.union(prism)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X: cube goes from -half_cube to +half_cube, prism extends to half_cube + tri_base
        expected_xmin = -half_cube
        expected_xmax = half_cube + tri_base
        expected_xlen = cube_size + tri_base
    
        # Y: same as X
        expected_ymin = -half_cube
        expected_ymax = half_cube + tri_base
        expected_ylen = cube_size + tri_base
    
        # Z: cube spans full cube_size
        expected_zlen = cube_size
    
        assert abs(bb.xmin - expected_xmin) < TOL, f"xmin: expected {expected_xmin:.4f}, got {bb.xmin:.4f}"
        assert abs(bb.xmax - expected_xmax) < TOL, f"xmax: expected {expected_xmax:.4f}, got {bb.xmax:.4f}"
        assert abs(bb.xlen - expected_xlen) < TOL, f"xlen: expected {expected_xlen:.4f}, got {bb.xlen:.4f}"
    
        assert abs(bb.ymin - expected_ymin) < TOL, f"ymin: expected {expected_ymin:.4f}, got {bb.ymin:.4f}"
        assert abs(bb.ymax - expected_ymax) < TOL, f"ymax: expected {expected_ymax:.4f}, got {bb.ymax:.4f}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"ylen: expected {expected_ylen:.4f}, got {bb.ylen:.4f}"
    
        assert abs(bb.zlen - expected_zlen) < TOL, f"zlen: expected {expected_zlen:.4f}, got {bb.zlen:.4f}"
    
        # Volume check
        cube_vol = cube_size ** 3
        prism_vol = 0.5 * tri_base * tri_base * tri_extrusion  # right triangle area * extrusion
        expected_vol = cube_vol + prism_vol  # they touch at an edge (zero overlap)
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that the prism point is inside the combined shape
        # Point inside the prism (away from cube)
        prism_interior = (half_cube + tri_base * 0.2, half_cube + tri_base * 0.2, 0.0)
        assert result.val().isInside(prism_interior), \
            f"Point {prism_interior} should be inside the combined shape (prism region)"
    
        # Point inside the cube
        cube_interior = (0.0, 0.0, 0.0)
        assert result.val().isInside(cube_interior), \
            f"Point {cube_interior} should be inside the combined shape (cube region)"
    
        # Point outside both shapes
        outside_point = (half_cube + tri_base + 0.1, 0.0, 0.0)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the combined shape"
    
        # Check cylindrical faces (holes) — there should be none
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        print(f"Cube size: {cube_size}")
        print(f"Tri base/height: {tri_base}, extrusion: {tri_extrusion}")
        print(f"Bounding box: X=[{bb.xmin:.4f}, {bb.xmax:.4f}], Y=[{bb.ymin:.4f}, {bb.ymax:.4f}], Z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00017291/gpt_generated.stl')
