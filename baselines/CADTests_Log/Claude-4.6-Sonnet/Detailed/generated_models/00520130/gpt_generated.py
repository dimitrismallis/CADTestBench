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
        # --- Step 1: Create main rectangle box 1.05 x 0.375 x 0.9 ---
        # Centered at origin, extruded along +Z
        main_box = cq.Workplane("XY").box(1.05, 0.375, 0.9)
    
        # --- Step 2: Create left protrusion ---
        # 0.6 (Y) x 0.15 (X) x 0.9 (Z), attached to left face (x = -0.525)
        # Center of left protrusion: x = -(0.525 + 0.075) = -0.6, y = 0, z = 0
        left_protrusion = cq.Workplane("XY").box(0.15, 0.6, 0.9).translate((-0.6, 0, 0))
    
        # --- Step 3: Create right protrusion ---
        # 0.6 (Y) x 0.15 (X) x 0.9 (Z), attached to right face (x = +0.525)
        # Center of right protrusion: x = +(0.525 + 0.075) = +0.6, y = 0, z = 0
        right_protrusion = cq.Workplane("XY").box(0.15, 0.6, 0.9).translate((0.6, 0, 0))
    
        # --- Step 4: Union all three parts ---
        result = main_box.union(left_protrusion).union(right_protrusion)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        # Total X extent: main 1.05 + left 0.15 + right 0.15 = 1.35
        expected_xlen = 1.05 + 0.15 + 0.15
        assert abs(bb.xlen - expected_xlen) < TOL, f"X length: expected {expected_xlen}, got {bb.xlen}"
        # Y extent: max of main (0.375) and protrusions (0.6) = 0.6
        expected_ylen = 0.6
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
        # Z extent: 0.9
        expected_zlen = 0.9
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Bounding box center should be at origin (symmetric)
        cx = (bb.xmin + bb.xmax) / 2
        cy = (bb.ymin + bb.ymax) / 2
        cz = (bb.zmin + bb.zmax) / 2
        assert abs(cx) < TOL, f"Center X: expected 0, got {cx}"
        assert abs(cy) < TOL, f"Center Y: expected 0, got {cy}"
        assert abs(cz) < TOL, f"Center Z: expected 0, got {cz}"
    
        # Volume check
        # Main box: 1.05 * 0.375 * 0.9 = 0.354375
        # Left protrusion: 0.15 * 0.6 * 0.9 = 0.081
        # Right protrusion: 0.15 * 0.6 * 0.9 = 0.081
        # No overlap since protrusions are outside main box
        vol_main = 1.05 * 0.375 * 0.9
        vol_left = 0.15 * 0.6 * 0.9
        vol_right = 0.15 * 0.6 * 0.9
        expected_vol = vol_main + vol_left + vol_right
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check symmetry: left and right protrusions exist
        # The shape should have faces at x = -0.675 (left outer) and x = +0.675 (right outer)
        assert abs(bb.xmin - (-0.675)) < TOL, f"xmin: expected -0.675, got {bb.xmin}"
        assert abs(bb.xmax - 0.675) < TOL, f"xmax: expected 0.675, got {bb.xmax}"
    
        # Check that the shape is not a simple box (has the grooved/stepped profile)
        # A simple box would have 6 faces; this shape should have more
        face_count = result.faces().size()
        assert face_count > 6, f"Face count should be > 6 for grooved shape, got {face_count}"
    
        # Check that points inside the protrusions are inside the solid
        solid = result.val()
        assert solid.isInside((-0.6, 0, 0)), "Left protrusion center should be inside solid"
        assert solid.isInside((0.6, 0, 0)), "Right protrusion center should be inside solid"
        # Check that a point in the groove (between protrusion and main body in Y) is outside
        # The groove region: x = -0.6, y = 0.4 (outside protrusion Y range of ±0.3, outside main Y range of ±0.1875)
        assert not solid.isInside((-0.6, 0.4, 0)), "Point outside protrusion Y range should be outside solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00520130/gpt_generated.stl')
