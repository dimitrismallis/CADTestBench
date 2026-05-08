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
        base_length = 80.0   # X dimension
        base_width  = 40.0   # Y dimension
        base_height = 20.0   # Z dimension (each tier)
    
        upper_length = 80.0  # same length as base
        upper_width  = 20.0  # half the width of base
        upper_height = 20.0  # same height as base tier
    
        hole_diameter = 10.0
    
        # --- Step 1: Create base rectangle block ---
        # Centered at origin in XY, so X: [-40,40], Y: [-20,20], Z: [0,20]
        result = (
            cq.Workplane("XY")
            .box(base_length, base_width, base_height,
                 centered=(True, True, False))  # Z starts at 0
        )
    
        # --- Step 2: Create upper rectangle block at one end ---
        # Upper block: same length (80), smaller width (20), same height (20)
        # Placed at +Y end of base: Y: [0, 20], X: [-40,40], Z: [20,40]
        # Center of upper block in XY: (0, 10), center Z: 30
        upper_block = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, upper_width / 2, base_height + upper_height / 2))
            .box(upper_length, upper_width, upper_height)
        )
    
        result = result.union(upper_block)
    
        # --- Step 3: Create circular hole through center of upper block ---
        # Center of upper block footprint: X=0, Y=10 (world coords)
        # Workplane origin after faces(">Z").workplane() is at (0, 0, 40) in world coords
        # (projection of previous origin (0,0,0) onto Z=40 plane)
        # So we need to offset by (0, +10) in workplane to reach world (0, 10)
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(0, 10)          # move workplane origin to world (0, 10, 40)
            .circle(hole_diameter / 2)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base_length) < TOL, \
            f"X length: expected {base_length}, got {bb.xlen}"
        assert abs(bb.ylen - base_width) < TOL, \
            f"Y length: expected {base_width}, got {bb.ylen}"
        assert abs(bb.zlen - (base_height + upper_height)) < TOL, \
            f"Z length: expected {base_height + upper_height}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - (base_height + upper_height)) < TOL, \
            f"Z max: expected {base_height + upper_height}, got {bb.zmax}"
    
        # Volume check
        base_vol  = base_length * base_width * base_height
        upper_vol = upper_length * upper_width * upper_height
        hole_vol  = math.pi * (hole_diameter / 2) ** 2 * (base_height + upper_height)
        expected_vol = base_vol + upper_vol - hole_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical face check (hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check hole passes through: a point at center of hole should be outside solid
        # Hole center in world: X=0, Y=10; check at multiple Z levels
        solid = result.val()
    
        # Mid-height of upper block (Z=30)
        point_in_hole_upper = cq.Vector(0.0, 10.0, 30.0)
        assert not solid.isInside(point_in_hole_upper), \
            f"Point {(0.0, 10.0, 30.0)} should be outside solid (inside hole in upper block)"
    
        # Mid-height of base block (Z=10), hole should pass through here too
        point_in_hole_base = cq.Vector(0.0, 10.0, 10.0)
        assert not solid.isInside(point_in_hole_base), \
            f"Point {(0.0, 10.0, 10.0)} should be outside solid (inside hole in base block)"
    
        # Check a point in the base block (away from hole) is inside solid
        point_in_base = cq.Vector(0, -15, 10)  # in base block, away from hole
        assert solid.isInside(point_in_base), \
            f"Point {(0, -15, 10)} should be inside the base block"
    
        # Check a point in the upper block (away from hole) is inside solid
        point_in_upper = cq.Vector(30, 10, 30)  # in upper block, away from hole center
        assert solid.isInside(point_in_upper), \
            f"Point {(30, 10, 30)} should be inside the upper block"
    
        # Check staircase: a point at the "step" region should be outside solid
        # (the region Y: [-20, 0] at Z: [20, 40] is empty — the step cutout)
        point_in_step = cq.Vector(0, -10, 30)  # in the empty step region
        assert not solid.isInside(point_in_step), \
            f"Point {(0, -10, 30)} should be outside solid (staircase step region)"
    
        # Top face should be at Z=40
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - (base_height + upper_height)) < TOL, \
            f"Top face Z center: expected {base_height + upper_height}, got {top_face_z}"
    
        # Verify hole center line intersects faces (entry and exit of hole)
        hole_faces = solid.facesIntersectedByLine(
            (0, 10, 50), (0, 0, -1)  # shoot ray downward through hole center
        )
        assert len(hole_faces) == 0, \
            f"Ray through hole center should intersect 0 solid faces (open hole), got {len(hole_faces)}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998843/gpt_generated.stl')
