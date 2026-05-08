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
        cyl_radius = 15.0       # cylinder radius
        cyl_height = 30.0       # cylinder height (along Z axis)
    
        block_length = 40.0     # longer than diameter (2*15=30), extends along Z
        block_width  = 8.0      # narrow dimension (along X, tangent to cylinder top)
        block_height = 4.0      # very short extrusion outward (along Y)
        overlap      = 1.0      # overlap into cylinder to ensure solid union
    
        # --- Step 1: Create the base cylinder ---
        # Cylinder axis along Z, centered at origin
        # Radius=15, height=30 → short and wide
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Create the rectangular block on top of the cylinder ---
        # The top of the cylinder's curved surface is at y = +cyl_radius
        # Sink the block 'overlap' mm into the cylinder so union merges cleanly
        # Block center Y = cyl_radius - overlap + (block_height + overlap)/2
        #                = cyl_radius + (block_height - overlap)/2
        block_center_y = cyl_radius + (block_height - overlap) / 2.0
    
        block = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, block_center_y, 0))
            .box(block_width, block_height + overlap, block_length)
        )
    
        # --- Step 3: Union the block with the cylinder ---
        result = result.union(block)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for curved geometry
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks:
        # X: cylinder diameter = 2*15 = 30, block width = 8 < 30, so xlen ~ 30
        expected_xlen = 2 * cyl_radius
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected ~{expected_xlen}, got {bb.xlen:.3f}"
    
        # Y: cylinder goes from -15 to +15, block top is at cyl_radius + block_height = 19
        # So ylen = 15 + 19 = 34
        expected_ylen = cyl_radius + cyl_radius + block_height
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected ~{expected_ylen}, got {bb.ylen:.3f}"
    
        # Z: block is longer (40) than cylinder height (30), so zlen ~ 40
        expected_zlen = block_length
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z extent: expected ~{expected_zlen}, got {bb.zlen:.3f}"
    
        # Volume check:
        # Cylinder volume = pi * r^2 * h
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        # Block effective volume (above cylinder surface) = block_width * block_height * block_length
        # The overlap region is inside the cylinder already, so net addition ~ block_width * block_height * block_length
        # But the overlap region subtracts from the block volume that's "new":
        # Total ~ cyl_vol + block_width * block_height * block_length
        # (overlap portion was already inside cylinder)
        # Approximate: allow 10% tolerance
        expected_vol_approx = cyl_vol + block_width * block_height * block_length
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol_approx) / expected_vol_approx < 0.10, \
            f"Volume: expected ~{expected_vol_approx:.1f}, got {actual_vol:.1f}"
    
        # Check that the block extends beyond the cylinder in Z direction
        assert bb.zlen > 2 * cyl_radius, \
            f"Block should be longer than cylinder diameter: zlen={bb.zlen:.3f}, diameter={2*cyl_radius}"
    
        # Check cylindrical face exists (the cylinder body)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # Check the block is on top (positive Y side) by verifying ymax
        assert abs(bb.ymax - (cyl_radius + block_height)) < TOL, \
            f"ymax: expected {cyl_radius + block_height}, got {bb.ymax:.3f}"
    
        # Check center of mass is slightly above Y=0 (block pulls it upward)
        com = cq.Shape.centerOfMass(solid)
        assert com.y > 0, f"Center of mass Y should be positive (block on top), got {com.y:.3f}"
    
        # Check the whistle has a single connected solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        print(f"Whistle model verified successfully!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"  Volume: {actual_vol:.2f} mm³")
        print(f"  Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00689273/gpt_generated.stl')
