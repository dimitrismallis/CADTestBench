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
        TOL = 0.001
    
        # --- Parameters ---
        # Part 1: Base rectangle
        p1_len = 1.40217   # X
        p1_wid = 0.062517  # Y
        p1_h   = 0.75      # Z
    
        # Part 2: Middle rectangle
        p2_len = 1.27174   # X
        p2_wid = 0.103421  # Y
        p2_h   = 0.75      # Z
    
        # Part 3: Trapezoid
        trap_base  = 1.33696  # X (bottom edge, wider)
        trap_angle = 72.0     # degrees (base angle)
        trap_h     = 0.75     # Z (extrusion height)
        # Depth (Y extent) slightly larger than p2_wid
        # Using angle: tan(angle) = depth / ((base - top)/2)
        # => (base - top)/2 = depth / tan(angle)
        # Choose depth slightly larger than p2_wid
        trap_depth = 0.12     # Y extent (slightly > 0.103421)
        # Compute top width from angle
        trap_top = trap_base - 2.0 * (trap_depth / math.tan(math.radians(trap_angle)))
    
        # --- Step 1: Create Part 1 (base rectangle) ---
        # Centered at origin in XY, extruded from Z=0 to Z=0.75
        part1 = (
            cq.Workplane("XY")
            .box(p1_len, p1_wid, p1_h, centered=(True, True, False))
        )
    
        # --- Step 2: Create Part 2 (middle rectangle) on top of Part 1 ---
        # Centered in X, centered in Y, placed at Z = p1_h
        part2 = (
            cq.Workplane("XY", origin=(0, 0, p1_h))
            .box(p2_len, p2_wid, p2_h, centered=(True, True, False))
        )
    
        # --- Step 3: Create Part 3 (trapezoid) on top of Part 2 ---
        # Trapezoid in XY plane, extruded in Z
        # Bottom edge (wider) at Y = -trap_depth/2, top edge (narrower) at Y = +trap_depth/2
        # Centered in X
        z_trap = p1_h + p2_h  # Z start = 1.5
    
        half_base = trap_base / 2.0
        half_top  = trap_top  / 2.0
        half_d    = trap_depth / 2.0
    
        # Vertices of trapezoid (in XY, centered at origin):
        # Bottom-left, Bottom-right, Top-right, Top-left
        v_bl = (-half_base, -half_d)
        v_br = ( half_base, -half_d)
        v_tr = ( half_top,   half_d)
        v_tl = (-half_top,   half_d)
    
        part3 = (
            cq.Workplane("XY", origin=(0, 0, z_trap))
            .polyline([v_bl, v_br, v_tr, v_tl])
            .close()
            .extrude(trap_h)
        )
    
        # --- Step 4: Union all three parts ---
        result = part1.union(part2).union(part3)
    
        # --- Final object verification ---
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        total_height = p1_h + p2_h + trap_h  # 2.25
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total height: expected {total_height}, got {bb.zlen}"
    
        # X extent: max of all three parts = p1_len = 1.40217
        expected_xlen = p1_len
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected {expected_xlen}, got {bb.xlen}"
    
        # Y extent: max of all three parts = p2_wid = 0.103421 (Part 2 is widest in Y)
        # Wait: trap_depth=0.12 > p2_wid=0.103421 > p1_wid=0.062517
        expected_ylen = trap_depth
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected {expected_ylen}, got {bb.ylen}"
    
        # Z extent
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_height) < TOL, f"Z max: expected {total_height}, got {bb.zmax}"
    
        # Volume check: sum of three parts (they don't overlap since stacked)
        vol_p1 = p1_len * p1_wid * p1_h
        vol_p2 = p2_len * p2_wid * p2_h
        # Trapezoid volume = ((base + top) / 2) * depth * height
        vol_p3 = ((trap_base + trap_top) / 2.0) * trap_depth * trap_h
        expected_vol = vol_p1 + vol_p2 + vol_p3
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Check that the trapezoid top width is smaller than base
        assert trap_top < trap_base, \
            f"Trap top ({trap_top:.5f}) should be < base ({trap_base:.5f})"
    
        # Check trapezoid depth > p2_wid
        assert trap_depth > p2_wid, \
            f"Trap depth ({trap_depth}) should be > p2_wid ({p2_wid})"
    
        # Check p2_len < p1_len (second rect shorter in X)
        assert p2_len < p1_len, \
            f"p2_len ({p2_len}) should be < p1_len ({p1_len})"
    
        # Check p2_wid > p1_wid (second rect wider in Y)
        assert p2_wid > p1_wid, \
            f"p2_wid ({p2_wid}) should be > p1_wid ({p1_wid})"
    
        # Verify the solid has 3 distinct Z-level regions by checking faces
        # The model should have faces at z=0, z=0.75, z=1.5, z=2.25
        bottom_faces = result.faces("<Z").size()
        top_faces    = result.faces(">Z").size()
        assert bottom_faces >= 1, f"Expected at least 1 bottom face, got {bottom_faces}"
        assert top_faces >= 1,    f"Expected at least 1 top face, got {top_faces}"
    
        print(f"trap_top = {trap_top:.5f}")
        print(f"trap_depth = {trap_depth:.5f}")
        print(f"Expected volume = {expected_vol:.5f}")
        print(f"Actual volume   = {actual_vol:.5f}")
        print(f"BBox: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00009843/gpt_generated.stl')
