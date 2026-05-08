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
        rect_length = 0.120604   # long dimension of rectangle (along X)
        rect_width  = 0.051687   # short dimension of rectangle (along Y) = trapezoid base
    
        # Isosceles trapezoid parameters
        trap_base   = rect_width          # = 0.051687, same as short edge of rectangle
        trap_top    = trap_base / 2.0     # = 0.025843 (top of trapezoid, smaller)
        trap_height = trap_base           # height of trapezoid along X = 0.051687
    
        extrude_h   = 0.75
    
        # --- Step 1: Build combined 2D profile ---
        # Layout in XY plane:
        #   Rectangle occupies x=[0, rect_length], y=[-rect_width/2, +rect_width/2]
        #   Trapezoid attached at x=0 (left short edge), extending to x=-trap_height
        #
        # Vertices of combined profile (going counter-clockwise):
        #   Start at bottom-right of rectangle: (rect_length, -rect_width/2)
        #   -> top-right of rectangle:          (rect_length, +rect_width/2)
        #   -> top-left of rectangle / top-right of trap base: (0, +rect_width/2)
        #   -> top of trapezoid (top-left):     (-trap_height, +trap_top/2)
        #   -> bottom of trapezoid (bottom-left): (-trap_height, -trap_top/2)
        #   -> bottom-left of rectangle / bottom-right of trap base: (0, -rect_width/2)
        #   -> back to start: (rect_length, -rect_width/2)
    
        hw = rect_width / 2.0   # half width = 0.025843
        ht = trap_top / 2.0     # half top   = 0.012922
    
        result = (
            cq.Workplane("XY")
            .moveTo(rect_length, -hw)
            .lineTo(rect_length,  hw)
            .lineTo(0,            hw)
            .lineTo(-trap_height, ht)
            .lineTo(-trap_height, -ht)
            .lineTo(0,           -hw)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # X extent: from -trap_height to rect_length
        expected_xlen = rect_length + trap_height
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
    
        # Y extent: rect_width (the rectangle is wider than the trapezoid top)
        expected_ylen = rect_width
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
    
        # Z extent: extrude height
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h:.6f}, got {bb.zlen:.6f}"
    
        # Volume: area of cross-section * extrude_h
        # Cross-section area = rectangle area + trapezoid area
        rect_area = rect_length * rect_width
        trap_area = 0.5 * (trap_base + trap_top) * trap_height
        total_area = rect_area + trap_area
        expected_vol = total_area * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The shape should be a single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check bounding box extents
        assert abs(bb.xmin - (-trap_height)) < TOL, \
            f"xmin: expected {-trap_height:.6f}, got {bb.xmin:.6f}"
        assert abs(bb.xmax - rect_length) < TOL, \
            f"xmax: expected {rect_length:.6f}, got {bb.xmax:.6f}"
        assert abs(bb.ymin - (-hw)) < TOL, \
            f"ymin: expected {-hw:.6f}, got {bb.ymin:.6f}"
        assert abs(bb.ymax - hw) < TOL, \
            f"ymax: expected {hw:.6f}, got {bb.ymax:.6f}"
        assert abs(bb.zmin - 0.0) < TOL, \
            f"zmin: expected 0.0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - extrude_h) < TOL, \
            f"zmax: expected {extrude_h:.6f}, got {bb.zmax:.6f}"
    
        # Face count: the extruded shape has 2 end faces + side faces
        # Profile has 6 edges -> 6 side faces + 2 end caps = 8 faces total
        face_count = result.faces().size()
        assert face_count == 8, \
            f"Face count: expected 8, got {face_count}"
    
        # Check planar faces only (all faces should be planar for this shape)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 8, \
            f"Planar face count: expected 8, got {planar_count}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x=[{bb.xmin:.6f}, {bb.xmax:.6f}], y=[{bb.ymin:.6f}, {bb.ymax:.6f}], z=[{bb.zmin:.6f}, {bb.zmax:.6f}]")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670457/gpt_generated.stl')
