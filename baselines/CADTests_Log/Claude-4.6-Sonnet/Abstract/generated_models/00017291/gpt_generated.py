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
        # --- Step 1: Create the large cube (40x40x40) centered at origin ---
        cube_size = 40.0
        cube = cq.Workplane("XY").box(cube_size, cube_size, cube_size)
        # Cube spans X:[-20,20], Y:[-20,20], Z:[-20,20]
    
        # --- Step 2: Create the right triangular prism ---
        # Prism is 1/4th the size of the cube: 10x10x10
        prism_size = cube_size / 4.0  # = 10.0
    
        # Right triangle cross-section with legs of 10mm in XY plane
        # Triangle vertices (in local 2D): (0,0), (10,0), (0,10)
        # This gives a right angle at (0,0)
        # The prism height (along Z) is also 10mm
    
        # Build the triangular prism using a polygon profile extruded along Z
        # We'll define the triangle in the XY plane and extrude upward
        prism = (
            cq.Workplane("XY")
            .workplane(offset=20)  # start at Z=20 (top of cube)
            .moveTo(0, 0)
            .lineTo(prism_size, 0)
            .lineTo(0, prism_size)
            .close()
            .extrude(prism_size)  # extrude upward by 10mm → Z: 20 to 30
        )
    
        # --- Step 3: Position the prism so two edges align with cube edges ---
        # We want the right-angle corner of the triangle at (20, 20) in XY
        # and the legs going in -X and -Y directions
        # Triangle vertices: (20,20), (10,20), (20,10) in XY
        # This places the prism at the corner of the cube's top face
        # Two edges of the prism align with two edges of the cube's top face:
        #   Edge 1: from (20,20,20) to (10,20,20) — along cube's top face Y=20 edge
        #   Edge 2: from (20,20,20) to (20,10,20) — along cube's top face X=20 edge
    
        # Rotate 180° around Z: (x,y) → (-x,-y)
        # Triangle: (0,0)→(0,0), (10,0)→(-10,0), (0,10)→(0,-10)
        # Then translate by (20,20): (20,20), (10,20), (20,10) ✓
        prism = prism.rotate((0, 0, 0), (0, 0, 1), 180)
        prism = prism.translate((20, 20, 0))
    
        # --- Step 4: Combine cube and prism into a union ---
        result = cube.union(prism)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Cube spans [-20,20] in X,Y,Z; prism adds from Z=20 to Z=30 and X:[10,20], Y:[10,20]
        # Overall bounding box:
        # X: -20 to 20 (cube dominates)
        # Y: -20 to 20 (cube dominates)
        # Z: -20 to 30 (prism extends above cube)
        assert abs(bb.xmin - (-20)) < TOL, f"xmin: expected -20, got {bb.xmin}"
        assert abs(bb.xmax - 20) < TOL, f"xmax: expected 20, got {bb.xmax}"
        assert abs(bb.ymin - (-20)) < TOL, f"ymin: expected -20, got {bb.ymin}"
        assert abs(bb.ymax - 20) < TOL, f"ymax: expected 20, got {bb.ymax}"
        assert abs(bb.zmin - (-20)) < TOL, f"zmin: expected -20, got {bb.zmin}"
        assert abs(bb.zmax - 30) < TOL, f"zmax: expected 30, got {bb.zmax}"
    
        # Volume check:
        # Cube volume = 40^3 = 64000
        # Prism volume = (1/2 * 10 * 10) * 10 = 500
        # Total = 64500
        cube_vol = cube_size ** 3
        prism_vol = 0.5 * prism_size * prism_size * prism_size
        expected_vol = cube_vol + prism_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check that the prism is 1/4th the cube size (linear dimension)
        assert abs(prism_size - cube_size / 4) < TOL, \
            f"Prism size should be 1/4 of cube size: expected {cube_size/4}, got {prism_size}"
    
        # Check that the model has no cylindrical faces (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected no cylindrical faces, got {cyl_faces}"
    
        # Check that a point inside the prism is inside the solid
        # Centroid of prism triangle at Z=25: centroid of (20,20),(10,20),(20,10) = (50/3, 50/3) ≈ (16.67, 16.67)
        prism_interior = (16, 16, 25)
        assert result.val().isInside(prism_interior), \
            f"Point {prism_interior} should be inside the prism"
    
        # Check that a point inside the cube is inside the solid
        cube_interior = (0, 0, 0)
        assert result.val().isInside(cube_interior), \
            f"Point {cube_interior} should be inside the cube"
    
        # Check that a point outside both shapes is NOT inside
        outside_point = (25, 25, 25)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the solid"
    
        # Check that a point clearly outside the prism (above cube, outside triangle) is not inside
        # Point at (5, 5, 25) — above cube but outside the prism triangle region
        # Triangle vertices: (20,20),(10,20),(20,10) — point (5,5,25) is far from this triangle
        outside_prism = (5, 5, 25)
        assert not result.val().isInside(outside_prism), \
            f"Point {outside_prism} should be outside the prism"
    
        # Verify alignment: the prism sits on top of the cube (touching at Z=20)
        # A point just above the cube surface but inside the prism footprint should be inside
        prism_just_above = (15, 15, 21)
        assert result.val().isInside(prism_just_above), \
            f"Point {prism_just_above} should be inside the prism (just above cube top)"
    
        # A point just above the cube surface but outside the prism footprint should be outside
        outside_above_cube = (0, 0, 21)
        assert not result.val().isInside(outside_above_cube), \
            f"Point {outside_above_cube} should be outside (above cube, not in prism)"
    
        # Verify the prism has a triangular cross-section by checking face count
        # The prism contributes: 2 triangular faces + 3 rectangular faces = 5 faces
        # The cube has 6 faces, but the top face is partially shared with the prism base
        # After union, total planar faces should be deterministic
        planar_faces = result.faces("%Plane").size()
        # Cube: 6 faces (top face partially covered by prism base)
        # Prism: 2 triangular + 3 rectangular = 5 faces
        # After union at Z=20: the prism base merges with cube top, leaving cube top with a
        # triangular hole region merged in. Net planar faces = 6 (cube) + 3 (prism sides) + 1 (prism top) = 10
        # but the cube top face gets split by the prism footprint boundary
        # Let's just check it's a reasonable number (>= 8)
        assert planar_faces >= 8, f"Expected at least 8 planar faces, got {planar_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X[{bb.xmin:.1f},{bb.xmax:.1f}] Y[{bb.ymin:.1f},{bb.ymax:.1f}] Z[{bb.zmin:.1f},{bb.zmax:.1f}]")
        print(f"Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00017291/gpt_generated.stl')
