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
        base_size = 0.75       # base square side length
        base_height = 0.25     # base extrusion height
        small_size = 0.15      # small square side length (≈ 1/5 of 0.75)
        cut_depth = 0.5        # negative extrusion depth
    
        # --- Step 1: Create base box 0.75 x 0.75 x 0.25 ---
        # centered=(True, True, False): centered in XY, starts at Z=0
        # Spans X: [-0.375, 0.375], Y: [-0.375, 0.375], Z: [0, 0.25]
        result = cq.Workplane("XY").box(base_size, base_size, base_height,
                                         centered=(True, True, False))
    
        # --- Step 2: Create the cutter box for the top-right corner ---
        # Small square top-right corner aligns with base top-right corner at (0.375, 0.375)
        # Small square spans: X in [0.225, 0.375], Y in [0.225, 0.375]
        # Center of small square in XY: (0.3, 0.3)
        # Cutter is centered at Z=base_height/2=0.125 with height=cut_depth=0.5
        # So cutter spans Z: [-0.125, 0.375] — completely through the base [0, 0.25]
        small_cx = (base_size / 2) - (small_size / 2)   # 0.375 - 0.075 = 0.3
        small_cy = (base_size / 2) - (small_size / 2)   # 0.375 - 0.075 = 0.3
    
        cutter = (cq.Workplane("XY")
                  .transformed(offset=cq.Vector(small_cx, small_cy, base_height / 2))
                  .box(small_size, small_size, cut_depth, centered=True))
    
        # --- Step 3: Subtract the cutter from the base ---
        result = result.cut(cutter)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Bounding box: cut is at top-right corner but overall extents unchanged
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - base_size) < TOL, f"BB xlen: expected {base_size}, got {bb.xlen}"
        assert abs(bb.ylen - base_size) < TOL, f"BB ylen: expected {base_size}, got {bb.ylen}"
        assert abs(bb.zlen - base_height) < TOL, f"BB zlen: expected {base_height}, got {bb.zlen}"
    
        # Bounding box Z position: 0 to 0.25
        assert abs(bb.zmin - 0.0) < TOL, f"BB zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - base_height) < TOL, f"BB zmax: expected {base_height}, got {bb.zmax}"
    
        # Volume check:
        # The cutter spans completely through the base (Z: -0.125 to 0.375 vs base Z: 0 to 0.25)
        # Removed volume = small_size * small_size * base_height = 0.15 * 0.15 * 0.25
        base_vol = base_size * base_size * base_height          # 0.140625
        cut_vol = small_size * small_size * base_height         # 0.005625
        expected_vol = base_vol - cut_vol                       # 0.135000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Point inside the cut region should NOT be inside the solid
        shape = result.val()
        inside_cut = shape.isInside((0.35, 0.35, 0.1))
        assert not inside_cut, "Point inside cut region should NOT be inside the solid"
    
        # Point in the main body should be inside
        inside_body = shape.isInside((0.0, 0.0, 0.1))
        assert inside_body, "Point in main body should be inside the solid"
    
        # Point in the cut corner should be outside
        inside_corner = shape.isInside((0.36, 0.36, 0.1))
        assert not inside_corner, "Point in cut corner should be outside the solid"
    
        # No cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Planar faces count:
        # The cutter goes completely through the base (no cut floor inside solid).
        # Faces: bottom (L-shaped)=1, side -X=1, side -Y=1, side +X (trimmed)=1,
        #        side +Y (trimmed)=1, top (L-shaped)=1, cut wall (facing -X)=1, cut wall (facing -Y)=1
        # Total = 8 planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 8, f"Expected 8 planar faces, got {planar_faces}"
    
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520976/gpt_generated.stl')
