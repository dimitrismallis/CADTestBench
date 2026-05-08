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
        rect_length = 0.75       # X dimension
        rect_width  = 0.605769   # Y dimension
        trap_base   = 0.375      # base of trapezoid (along Y)
        trap_leg    = 0.028846   # length of angled sides
        base_angle  = 45.0       # degrees
        extrude_h   = 0.018035   # extrusion height
    
        # --- Derived trapezoid dimensions ---
        angle_rad = math.radians(base_angle)
        trap_height = trap_leg * math.sin(angle_rad)          # ~0.020404
        trap_offset = trap_leg * math.cos(angle_rad)          # ~0.020404 (horizontal inset per side)
        trap_top    = trap_base - 2 * trap_offset             # shorter parallel side
    
        # --- Step 1: Build the combined 2D profile ---
        # Rectangle: centered at origin, X: [-0.375, 0.375], Y: [-rect_width/2, rect_width/2]
        # Trapezoid: attached to right edge (X=0.375), base along Y, extending in +X
    
        hw = rect_width / 2   # half-width = 0.302885
        hl = rect_length / 2  # half-length = 0.375
    
        # Trapezoid base half-width
        tb_half = trap_base / 2   # 0.1875
        tt_half = trap_top / 2    # (trap_base - 2*trap_offset) / 2
    
        # Trapezoid center along Y: at center of shorter edge (Y=0)
        ty = 0.0
    
        # Combined profile vertices (counterclockwise):
        # The profile is: rectangle with trapezoid protruding from the right edge
        # 8 vertices total forming an 8-sided polygon
        #
        # Vertices:
        # 0: (-hl, -hw)                        bottom-left of rectangle
        # 1: ( hl, -hw)                        bottom-right of rectangle
        # 2: ( hl, ty - tb_half)               bottom of trapezoid base on rect right edge
        # 3: ( hl + trap_height, ty - tt_half) bottom-right of trapezoid top
        # 4: ( hl + trap_height, ty + tt_half) top-right of trapezoid top
        # 5: ( hl, ty + tb_half)               top of trapezoid base on rect right edge
        # 6: ( hl, hw)                         top-right of rectangle
        # 7: (-hl, hw)                         top-left of rectangle
    
        pts = [
            (-hl, -hw),                          # 0: bottom-left
            ( hl, -hw),                          # 1: bottom-right of rect
            ( hl, ty - tb_half),                 # 2: start of trapezoid base (bottom)
            ( hl + trap_height, ty - tt_half),   # 3: trapezoid top-right (bottom)
            ( hl + trap_height, ty + tt_half),   # 4: trapezoid top-right (top)
            ( hl, ty + tb_half),                 # 5: end of trapezoid base (top)
            ( hl, hw),                           # 6: top-right of rect
            (-hl, hw),                           # 7: top-left
        ]
    
        # --- Step 2: Create the 2D profile and extrude ---
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 0.001
    
        bb = result.val().BoundingBox()
    
        # X: from -hl to hl + trap_height
        expected_xlen = rect_length + trap_height
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y: rect_width
        expected_ylen = rect_width
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z: extrude height
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h:.6f}, got {bb.zlen:.6f}"
    
        # Volume: (rectangle area + trapezoid area) * extrude_h
        rect_area  = rect_length * rect_width
        trap_area  = 0.5 * (trap_base + trap_top) * trap_height
        expected_vol = (rect_area + trap_area) * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check it's a single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check bounding box Z range
        assert abs(bb.zmin) < TOL, \
            f"Z min should be ~0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, \
            f"Z max should be ~{extrude_h}, got {bb.zmax}"
    
        # Check X range
        assert abs(bb.xmin - (-hl)) < TOL, \
            f"X min: expected {-hl}, got {bb.xmin}"
        assert abs(bb.xmax - (hl + trap_height)) < TOL, \
            f"X max: expected {hl+trap_height:.6f}, got {bb.xmax:.6f}"
    
        # Check Y range
        assert abs(bb.ymin - (-hw)) < TOL, \
            f"Y min: expected {-hw}, got {bb.ymin}"
        assert abs(bb.ymax - hw) < TOL, \
            f"Y max: expected {hw}, got {bb.ymax}"
    
        # Planar faces:
        # - 1 bottom face (full profile)
        # - 1 top face (full profile)
        # - 8 side faces (one per edge of the 8-vertex polygon)
        # Total = 10 planar faces
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, \
            f"Expected 10 planar faces, got {planar_count}"
    
        # Verify trapezoid geometry: top width should be base - 2*offset
        assert abs(trap_top - (trap_base - 2 * trap_offset)) < TOL, \
            f"Trapezoid top width mismatch: {trap_top:.6f} vs {trap_base - 2*trap_offset:.6f}"
    
        # Verify trapezoid base is ~2/3 of rect_width
        ratio = trap_base / rect_width
        assert abs(ratio - 2/3) < 0.05, \
            f"Trapezoid base / rect_width ratio: expected ~0.667, got {ratio:.4f}"
    
        # Verify leg length
        computed_leg = math.sqrt(trap_height**2 + trap_offset**2)
        assert abs(computed_leg - trap_leg) < TOL, \
            f"Leg length: expected {trap_leg:.6f}, got {computed_leg:.6f}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Trapezoid height: {trap_height:.6f}, top width: {trap_top:.6f}")
        print(f"Planar faces: {planar_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670960/gpt_generated.stl')
