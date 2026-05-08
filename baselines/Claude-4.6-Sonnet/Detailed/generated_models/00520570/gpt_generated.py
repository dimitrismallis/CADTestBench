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
        # --- Parameters (convert meters to mm) ---
        base_width  = 0.767871 * 1000   # 767.871 mm  (bottom, narrower)
        top_width   = 1.04978  * 1000   # 1049.78 mm  (top, wider)
        height      = 0.576632 * 1000   # 576.632 mm
        length      = 0.012814 * 1000   # 12.814 mm   (extrusion depth)
    
        # --- Step 1: Define trapezoid vertices (centered at origin) ---
        # Half-widths
        hb = base_width / 2    # 383.9355
        ht = top_width  / 2    # 524.89
        hh = height     / 2    # 288.316
    
        # Vertices of the isosceles trapezoid, centered at (0,0):
        # Bottom edge at y = -hh, top edge at y = +hh
        v1 = (-hb, -hh)   # bottom-left
        v2 = ( hb, -hh)   # bottom-right
        v3 = ( ht,  hh)   # top-right
        v4 = (-ht,  hh)   # top-left
    
        # --- Step 2: Create the 2D profile and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(v1[0], v1[1])
            .lineTo(v2[0], v2[1])
            .lineTo(v3[0], v3[1])
            .lineTo(v4[0], v4[1])
            .close()
            .extrude(length)
        )
    
        # The extrude goes from Z=0 to Z=length by default.
        # Center it along Z by translating by -length/2
        result = result.translate((0, 0, -length / 2))
    
        # --- Final object verification ---
        TOL = 0.1  # mm tolerance
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        expected_xlen = top_width   # widest dimension is the top width
        expected_ylen = height
        expected_zlen = length
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.3f}, got {bb.xlen:.3f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.3f}, got {bb.ylen:.3f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.3f}, got {bb.zlen:.3f}"
    
        # Centering checks
        assert abs(bb.xmin + bb.xmax) < TOL, \
            f"X not centered: xmin={bb.xmin:.3f}, xmax={bb.xmax:.3f}"
        assert abs(bb.ymin + bb.ymax) < TOL, \
            f"Y not centered: ymin={bb.ymin:.3f}, ymax={bb.ymax:.3f}"
        assert abs(bb.zmin + bb.zmax) < TOL, \
            f"Z not centered: zmin={bb.zmin:.3f}, zmax={bb.zmax:.3f}"
    
        # Volume check: trapezoid area = 0.5 * (base + top) * height
        trap_area = 0.5 * (base_width + top_width) * height
        expected_vol = trap_area * length
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: trapezoid prism has 6 faces (2 trapezoid faces + 4 side rectangles)
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # Check planar faces only (all faces should be planar for a prism)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 6, \
            f"Planar face count: expected 6, got {planar_count}"
    
        # Check top and bottom faces (parallel to XY plane)
        z_parallel = result.faces("|Z").size()
        assert z_parallel == 2, \
            f"Faces parallel to Z (front/back): expected 2, got {z_parallel}"
    
        print("All assertions passed!")
        print(f"  Bounding box: X={bb.xlen:.3f}, Y={bb.ylen:.3f}, Z={bb.zlen:.3f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"  Centered at: ({(bb.xmin+bb.xmax)/2:.3f}, {(bb.ymin+bb.ymax)/2:.3f}, {(bb.zmin+bb.zmax)/2:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520570/gpt_generated.stl')
