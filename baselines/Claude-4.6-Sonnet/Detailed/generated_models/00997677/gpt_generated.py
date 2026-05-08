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
        base_len    = 1.5
        base_wid    = 0.75
        base_thk    = 0.034954
    
        col_len     = 0.35911
        col_wid     = 0.581568
        col_height  = 0.699153
        margin      = 0.055864
    
        # --- Step 1: Base plate (centered at origin) ---
        # Z: -base_thk/2 to +base_thk/2
        base = cq.Workplane("XY").box(base_len, base_wid, base_thk)
    
        # --- Step 2: Column positions ---
        # Columns placed symmetrically at each end in X direction
        # margin from edge of base in X: 0.055864
        # Column center X = ±(base_len/2 - margin - col_len/2)
        col_cx = base_len / 2 - margin - col_len / 2
        # col_cx = 0.75 - 0.055864 - 0.179555 = 0.514581
        # Columns centered in Y (col_wid=0.581568 < base_wid=0.75, fits)
        col_cy = 0.0
    
        # --- Step 3: Columns extruded downward from bottom face of base ---
        # Bottom face at Z = -base_thk/2
        # Columns go downward: Z from -base_thk/2 to -base_thk/2 - col_height
    
        col1 = (
            cq.Workplane("XY")
            .center(col_cx, col_cy)
            .box(col_len, col_wid, col_height, centered=(True, True, False))
            .translate((0, 0, -base_thk / 2 - col_height))
        )
    
        col2 = (
            cq.Workplane("XY")
            .center(-col_cx, col_cy)
            .box(col_len, col_wid, col_height, centered=(True, True, False))
            .translate((0, 0, -base_thk / 2 - col_height))
        )
    
        # --- Step 4: Union base + columns ---
        assembly = base.union(col1).union(col2)
    
        # --- Step 5: Translate so top of base is at Z=0 ---
        # Base top at +base_thk/2, shift by -base_thk/2
        # After: base Z from -base_thk to 0, columns Z from -base_thk - col_height to -base_thk
        # Column top (base of columns) = -base_thk = bottom of base ✓ (inverted table)
        shift_z = -base_thk / 2
        result = assembly.translate((0, 0, shift_z))
    
        # After translation:
        # Base: Z from -base_thk to 0
        # Columns: Z from -(base_thk + col_height) to -base_thk
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box
        # X is determined by the base plate (wider than columns)
        expected_xlen = base_len        # 1.5 (base plate dominates)
        expected_ylen = base_wid        # 0.75 (base plate dominates)
        expected_zlen = base_thk + col_height  # 0.034954 + 0.699153 = 0.734107
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Z extents: top of base at 0, bottom of columns at -(base_thk + col_height)
        expected_zmax = 0.0
        expected_zmin = -(base_thk + col_height)
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin:.6f}, got {bb.zmin:.6f}"
    
        # X extents: base plate dominates at ±base_len/2
        assert abs(bb.xmax - base_len / 2) < TOL, \
            f"X max: expected {base_len/2}, got {bb.xmax}"
        assert abs(bb.xmin - (-base_len / 2)) < TOL, \
            f"X min: expected {-base_len/2}, got {bb.xmin}"
    
        # Y extents: base plate dominates at ±base_wid/2
        assert abs(bb.ymax - base_wid / 2) < TOL, \
            f"Y max: expected {base_wid/2}, got {bb.ymax}"
        assert abs(bb.ymin - (-base_wid / 2)) < TOL, \
            f"Y min: expected {-base_wid/2}, got {bb.ymin}"
    
        # Volume: base + 2 columns
        vol_base = base_len * base_wid * base_thk
        vol_col  = col_len * col_wid * col_height
        expected_vol = vol_base + 2 * vol_col
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Center of mass should be at X=0, Y=0 (symmetric about both axes)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, \
            f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, \
            f"Center of mass Y: expected 0, got {com.y}"
    
        # Column positions: verify columns are within base X bounds
        assert col_cx + col_len / 2 <= base_len / 2 + TOL, \
            f"Column exceeds base in X: col edge={col_cx + col_len/2}, base edge={base_len/2}"
        # Verify margin from edge
        actual_margin = base_len / 2 - (col_cx + col_len / 2)
        assert abs(actual_margin - margin) < TOL, \
            f"Column margin: expected {margin}, got {actual_margin}"
    
        # Planar faces check
        n_planar = result.faces("%Plane").size()
        assert n_planar > 0, f"Expected planar faces, got {n_planar}"
    
        print(f"Bounding box: X={bb.xlen:.6f}, Y={bb.ylen:.6f}, Z={bb.zlen:.6f}")
        print(f"Volume: expected={expected_vol:.6f}, actual={actual_vol:.6f}")
        print(f"Z range: [{bb.zmin:.6f}, {bb.zmax:.6f}]")
        print(f"Column center X: ±{col_cx:.6f}")
        print(f"Column margin from base edge: {actual_margin:.6f}")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997677/gpt_generated.stl')
