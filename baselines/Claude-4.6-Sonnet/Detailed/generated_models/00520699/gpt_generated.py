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
        cyl_diameter = 0.15
        cyl_radius   = cyl_diameter / 2.0   # 0.075
        cyl_height   = 0.0375
    
        rect_length  = 0.691425   # extends along Y from circle edge
        rect_width   = 0.093715   # along X, centered
        rect_height  = 0.02625    # along Z, less than cylinder
    
        # Small overlap to ensure proper boolean union
        overlap = 0.001
    
        # --- Step 1: Create the base cylinder (bulb) ---
        # Centered at origin in XY, bottom at Z=0
        cylinder = (
            cq.Workplane("XY")
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Step 2: Create the rectangle stem ---
        # The rectangle extends from slightly inside the circle (overlap) outward
        # so the union produces a single merged solid.
        # Start at y = -overlap (slightly into cylinder), extend to y = cyl_radius + rect_length
        # Total Y length of stem box = overlap + cyl_radius + rect_length
        stem_total_length = overlap + cyl_radius + rect_length
    
        stem = (
            cq.Workplane("XY")
            .box(rect_width, stem_total_length, rect_height, centered=(True, False, False))
            .translate((0, -overlap, 0))
        )
    
        # --- Step 3: Union cylinder and stem ---
        result = cylinder.union(stem)
    
        # --- Step 4: Rotate the assembly for proper thermometer orientation ---
        # Rotate -90 degrees around X axis so the stem points upward in Z
        result = result.rotate((0, 0, 0), (1, 0, 0), -90)
    
        # --- Final object verification ---
        TOL = 0.001
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After rotation by -90° around X:
        # Original axes: X stays X, Y→Z (negated), Z→Y
        # (x,y,z) → (x, z, -y)
        #
        # Original X range: cylinder dominates → [-0.075, 0.075], xlen = 0.15
        # Original Y range: stem goes from -overlap to cyl_radius+rect_length
        #                   cylinder goes from -cyl_radius to +cyl_radius
        #                   Combined: [-0.075, 0.075 + 0.691425] = [-0.075, 0.766425]
        #                   ylen = 0.075 + 0.766425 = 0.841425
        # Original Z range: [0, cyl_height] = [0, 0.0375], zlen = 0.0375
        #
        # After -90° around X: new_Z = -old_Y, new_Y = old_Z
        # New X: [-0.075, 0.075] → xlen = 0.15
        # New Y: [0, 0.0375]     → ylen = 0.0375
        # New Z: [-0.766425, 0.075] → zlen = 0.841425
    
        # Check bounding box X (dominated by cylinder diameter)
        assert abs(bb.xlen - cyl_diameter) < TOL, \
            f"X extent: expected {cyl_diameter}, got {bb.xlen}"
    
        # Check bounding box Y (was Z: cylinder height 0.0375)
        assert abs(bb.ylen - cyl_height) < TOL, \
            f"Y extent: expected {cyl_height}, got {bb.ylen}"
    
        # Check bounding box Z (was Y span: cyl_radius + rect_length + cyl_radius)
        expected_zlen = cyl_radius + rect_length + cyl_radius
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # Check we have exactly 1 merged solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Volume check: cylinder + stem minus overlap region
        cyl_vol  = math.pi * cyl_radius**2 * cyl_height
        # Stem volume uses the actual rect_length (not the extended version with overlap)
        # The overlap portion is inside the cylinder, so net addition is just rect_length portion
        # For a rough check, use cylinder + rect_length * rect_width * rect_height
        stem_vol_approx = rect_width * rect_length * rect_height
        expected_vol_approx = cyl_vol + stem_vol_approx
        actual_vol = solid.Volume()
        # Allow 10% tolerance for overlap region
        assert abs(actual_vol - expected_vol_approx) / expected_vol_approx < 0.10, \
            f"Volume: expected ~{expected_vol_approx:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical face exists (the bulb)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, \
            f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected ~{expected_vol_approx:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Solids: {result.solids().size()}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520699/gpt_generated.stl')
