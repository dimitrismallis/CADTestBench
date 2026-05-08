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
        base_length = 0.307377   # X dimension
        base_width  = 0.307377   # Z dimension (on XZ plane)
        base_height = 0.012295   # Y extrusion (base thickness)
    
        pillar_length = 0.307377  # X dimension (same as base)
        pillar_width  = 0.184426  # Z dimension (approx half of base_width per prompt)
        pillar_height = 0.737705  # Y extrusion (main body)
    
        total_height = base_height + pillar_height  # 0.75
    
        # --- Step 1: Create the square base on the X-Z plane ---
        # XZ plane normal is +Y, so extrusion goes in +Y direction.
        result = (
            cq.Workplane("XZ")
            .rect(base_length, base_width)
            .extrude(base_height)
        )
    
        # Translate so the base bottom sits at Y=0 (ymin=0) if needed
        bb_check = result.val().BoundingBox()
        if bb_check.ymin < 0:
            result = result.translate((0, -bb_check.ymin, 0))
    
        # --- Step 2: On the top face (max Y), sketch the smaller rectangle and extrude ---
        result = (
            result
            .faces(">Y")
            .workplane()
            .rect(pillar_length, pillar_width)
            .extrude(pillar_height)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X extent: base_length = 0.307377
        assert abs(bb.xlen - base_length) < TOL, \
            f"X extent: expected {base_length}, got {bb.xlen}"
    
        # Z extent: base_width = 0.307377 (the base is wider in Z than the pillar)
        assert abs(bb.zlen - base_width) < TOL, \
            f"Z extent: expected {base_width}, got {bb.zlen}"
    
        # Y extent: base_height + pillar_height = 0.012295 + 0.737705 = 0.75
        assert abs(bb.ylen - total_height) < TOL, \
            f"Y extent: expected {total_height}, got {bb.ylen}"
    
        # Volume check:
        # Base volume: base_length * base_width * base_height
        base_vol = base_length * base_width * base_height
        # Pillar volume: pillar_length * pillar_width * pillar_height
        pillar_vol = pillar_length * pillar_width * pillar_height
        expected_vol = base_vol + pillar_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: compound shape should have more than 6 faces
        face_count = result.faces().size()
        assert face_count > 6, \
            f"Face count: expected > 6 (compound shape), got {face_count}"
    
        # Check the base bottom is at Y=0
        assert abs(bb.ymin) < TOL, \
            f"Base bottom Y: expected ~0, got {bb.ymin}"
    
        # Check the top is at total_height
        assert abs(bb.ymax - total_height) < TOL, \
            f"Top Y: expected {total_height}, got {bb.ymax}"
    
        # Check center of mass is roughly centered in X and Z
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.z) < TOL, \
            f"Center of mass Z: expected ~0, got {com.z}"
    
        # Verify pillar is narrower in Z than the base (pillar_width < base_width)
        assert pillar_width < base_width, \
            f"Pillar Z width {pillar_width} should be less than base Z width {base_width}"
    
        # Verify pillar width matches specified value
        assert abs(pillar_width - 0.184426) < TOL, \
            f"Pillar width: expected 0.184426, got {pillar_width}"
    
        # Verify pillar height is significantly larger than base height
        assert pillar_height > base_height * 10, \
            f"Pillar height {pillar_height} should be much larger than base height {base_height}"
    
        # Verify the center of mass Y is above the midpoint of the base
        assert com.y > base_height, \
            f"Center of mass Y {com.y} should be above base height {base_height}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print(f"Y range: [{bb.ymin:.6f}, {bb.ymax:.6f}]")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00522404/gpt_generated.stl')
