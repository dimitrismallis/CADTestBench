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
        # Rectangle: length=40, width=20 (smaller side ~half of larger side: 20 = 40/2)
        rect_length = 40.0   # larger side
        rect_width  = 20.0   # smaller side (half of larger)
    
        # Right trapezoid: longer base = rect_width = 20 (connects to right end of rectangle)
        # shorter parallel side = 10 (half of longer base)
        # horizontal extent = 20
        trap_horiz  = 20.0   # horizontal extent of trapezoid
        trap_long   = 20.0   # longer base (= rect_width, connects to rectangle)
        trap_short  = 10.0   # shorter parallel side
    
        # Extrusion depth
        depth = 20.0
    
        # --- Step 1: Build the combined 2D profile as a closed wire ---
        # Combined profile vertices (in XY plane):
        # Rectangle occupies x: 0..40, y: 0..20
        # Trapezoid occupies x: 40..60, y: 0..20 (left/longer base) tapering to y: 0..10 (right/shorter)
        #
        # Right trapezoid vertices:
        #   (40, 0)  -> (60, 0)  : bottom horizontal base (length 20) — right angle at (40,0) and (60,0)
        #   (60, 0)  -> (60, 10) : right vertical side (length 10)    — right angle at (60,0)
        #   (60, 10) -> (40, 20) : slanted top
        #   (40, 20) -> (40, 0)  : left vertical side (length 20) = longer base connecting to rectangle
        #
        # Full combined profile (CCW):
        # (0,0) -> (60,0) -> (60,10) -> (40,20) -> (0,20) -> (0,0)
        #
        # This gives:
        #   - Left rectangle portion: x=0..40, y=0..20 (full height 20)
        #   - Right trapezoid portion: x=40..60, stepping from height 20 down to height 10
    
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(60, 0)       # bottom edge (rect bottom + trap bottom)
            .lineTo(60, 10)      # right vertical side of trapezoid
            .lineTo(40, 20)      # slanted top of trapezoid
            .lineTo(0, 20)       # top of rectangle
            .close()             # back to (0,0)
            .extrude(depth)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - 60.0) < TOL, f"X length: expected 60.0, got {bb.xlen}"
        assert abs(bb.ylen - 20.0) < TOL, f"Y length: expected 20.0, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL, f"Z length (depth): expected {depth}, got {bb.zlen}"
    
        # Bounding box position
        assert abs(bb.xmin - 0.0) < TOL, f"xmin: expected 0.0, got {bb.xmin}"
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0.0, got {bb.ymin}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.xmax - 60.0) < TOL, f"xmax: expected 60.0, got {bb.xmax}"
        assert abs(bb.ymax - 20.0) < TOL, f"ymax: expected 20.0, got {bb.ymax}"
        assert abs(bb.zmax - depth) < TOL, f"zmax: expected {depth}, got {bb.zmax}"
    
        # Volume check:
        # The 2D profile area = rectangle area + trapezoid area
        # Rectangle: 40 * 20 = 800
        # Right trapezoid: (longer_base + shorter_base) / 2 * horizontal_extent
        #   = (20 + 10) / 2 * 20 = 300
        # Total area = 800 + 300 = 1100
        # Volume = area * depth = 1100 * 20 = 22000
        rect_area = rect_length * rect_width                      # 40 * 20 = 800
        trap_area = (trap_long + trap_short) / 2.0 * trap_horiz  # (20+10)/2 * 20 = 300
        expected_vol = (rect_area + trap_area) * depth            # 1100 * 20 = 22000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count check:
        # The extruded solid has:
        #   - 1 bottom face (pentagon)
        #   - 1 top face (pentagon)
        #   - 5 side faces (one per edge of the pentagon profile)
        # Total = 7 faces
        face_count = result.faces().size()
        assert face_count == 7, f"Face count: expected 7, got {face_count}"
    
        # Check that the shape is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check the tiered nature: a point inside the rectangle portion should be inside the solid
        # Point in rectangle region: (20, 10, 10) — well within the rectangle
        assert result.val().isInside((20, 10, 10)), \
            "Point (20,10,10) should be inside the solid (rectangle region)"
    
        # Point in trapezoid region near bottom: (50, 5, 10) — inside trapezoid
        assert result.val().isInside((50, 5, 10)), \
            "Point (50,5,10) should be inside the solid (trapezoid region)"
    
        # Point clearly outside: above the slanted top of the trapezoid.
        # At x=50, the slant from (40,20) to (60,10) gives y = 20 + (50-40)/(60-40)*(10-20) = 15.
        # So (50, 17, 10) is clearly above the slant boundary and should be outside.
        assert not result.val().isInside((50, 17, 10)), \
            "Point (50,17,10) should be outside the solid (above slanted trapezoid top)"
    
        # Point clearly outside: beyond the right edge of the trapezoid
        assert not result.val().isInside((65, 5, 10)), \
            "Point (65,5,10) should be outside the solid (beyond right edge)"
    
        # Point clearly outside: above the rectangle top
        assert not result.val().isInside((20, 25, 10)), \
            "Point (20,25,10) should be outside the solid (above rectangle top)"
    
        # Verify the planar faces count (all faces should be planar for this shape)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 7, \
            f"Planar face count: expected 7, got {planar_face_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00675498/gpt_generated.stl')
