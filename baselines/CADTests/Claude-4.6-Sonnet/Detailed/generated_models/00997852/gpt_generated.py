import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Step 1: Base rectangle (tier 1) ---
        # Dimensions: length=1.5 (X), width=0.153061 (Y), height=0.918367 (Z)
        # Centered at origin
        base_length = 1.5
        base_width  = 0.153061
        base_height = 0.918367
    
        result = cq.Workplane("XY").box(base_length, base_width, base_height)
    
        # --- Step 2: Upper tier (tier 2) ---
        # On top of base, sketch a smaller rectangle centered at same XY center
        # Dimensions: length=1.43878 (X), width=0.841837 (Y), extruded upward by 0.229592
        tier2_length = 1.43878
        tier2_width  = 0.841837
        tier2_extrude = 0.229592
    
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(tier2_length, tier2_width)
            .extrude(tier2_extrude)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box:
        # X: max of base_length and tier2_length = 1.5
        expected_xlen = max(base_length, tier2_length)  # 1.5
        # Y: max of base_width and tier2_width = 0.841837
        expected_ylen = max(base_width, tier2_width)    # 0.841837
        # Z: base_height + tier2_extrude = 0.918367 + 0.229592 = 1.147959
        expected_zlen = base_height + tier2_extrude     # 1.147959
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Base volume + tier2 volume
        vol_base  = base_length * base_width * base_height
        vol_tier2 = tier2_length * tier2_width * tier2_extrude
        expected_vol = vol_base + vol_tier2
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check that there are planar faces (tiered shape)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 10, \
            f"Expected at least 10 planar faces for tiered shape, got {planar_faces}"
    
        # Check the top face is at the correct Z
        top_z = result.faces(">Z").val().Center().z
        expected_top_z = -base_height/2 + base_height + tier2_extrude
        assert abs(top_z - expected_top_z) < TOL, \
            f"Top face Z center: expected {expected_top_z}, got {top_z}"
    
        # Check the bottom face is at the correct Z
        bot_z = result.faces("<Z").val().Center().z
        expected_bot_z = -base_height / 2
        assert abs(bot_z - expected_bot_z) < TOL, \
            f"Bottom face Z center: expected {expected_bot_z}, got {bot_z}"
    
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997852/gpt_generated.stl')
