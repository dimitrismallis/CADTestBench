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
        rect_w = 60.0       # rectangle width (larger dimension)
        rect_h = 40.0       # rectangle height (smaller dimension)
        trap_long = 60.0    # trapezium longer parallel side = rect_w
        trap_short = 30.0   # trapezium shorter parallel side
        trap_h = 30.0       # trapezium height
        extrude_d = 80.0    # extrusion depth (large amount)
    
        # The combined profile:
        # - Rectangle: x in [-30, 30], y in [0, 40]
        # - Isosceles Trapezium (inverted - wider at top):
        #     shorter edge (30mm) at y=40, centered: x in [-15, 15]
        #     longer edge (60mm) at y=70, centered: x in [-30, 30]
        # The smaller edge of the trapezium attaches to the top of the rectangle.
        #
        # Build as union of rectangle extrusion + trapezoid extrusion.
    
        half_rw = rect_w / 2       # 30
        half_ts = trap_short / 2   # 15
        half_tl = trap_long / 2    # 30
    
        # --- Step 1: Extrude the rectangle ---
        rect_solid = (
            cq.Workplane("XY")
            .moveTo(-half_rw, 0)
            .lineTo( half_rw, 0)
            .lineTo( half_rw, rect_h)
            .lineTo(-half_rw, rect_h)
            .close()
            .extrude(extrude_d)
        )
    
        # --- Step 2: Extrude the trapezoid ---
        # Trapezoid vertices (isosceles, inverted: narrow at bottom, wide at top):
        # Bottom (narrow): (-15, 40) to (15, 40)
        # Top (wide):      (-30, 70) to (30, 70)
        trap_solid = (
            cq.Workplane("XY")
            .moveTo(-half_ts, rect_h)
            .lineTo( half_ts, rect_h)
            .lineTo( half_tl, rect_h + trap_h)
            .lineTo(-half_tl, rect_h + trap_h)
            .close()
            .extrude(extrude_d)
        )
    
        # --- Step 3: Union the two solids ---
        result = rect_solid.union(trap_solid)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_xlen = rect_w              # 60
        expected_ylen = rect_h + trap_h     # 70
        expected_zlen = extrude_d           # 80
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Volume check:
        # Cross-section area = rectangle area + trapezium area
        rect_area = rect_w * rect_h                                    # 60*40 = 2400
        trap_area = 0.5 * (trap_short + trap_long) * trap_h           # 0.5*(30+60)*30 = 1350
        cross_section_area = rect_area + trap_area                     # 3750
        expected_vol = cross_section_area * extrude_d                  # 3750*80 = 300000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count check:
        # Rectangle extruded: 6 faces (top, bottom, 4 sides)
        # Trapezoid extruded: 6 faces (top, bottom, 4 sides)
        # After union, shared faces merge. The rectangle top (y=40) is partially
        # covered by the trapezoid bottom, leaving two exposed rectangular strips
        # on either side. The overall face count after union will vary.
        # Let's just check it's reasonable (>= 8).
        face_count = result.faces().size()
        assert face_count >= 8, \
            f"Face count: expected >= 8, got {face_count}"
    
        # Check it's a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, \
            f"Solid count: expected 1, got {solid_count}"
    
        # Check bounding box center X is near 0 (symmetric about X=0)
        center = result.val().CenterOfBoundBox()
        assert abs(center.x) < TOL, \
            f"Center X: expected ~0, got {center.x}"
    
        # Check the top face is at y = rect_h + trap_h = 70
        assert abs(bb.ymax - (rect_h + trap_h)) < TOL, \
            f"Top Y: expected {rect_h + trap_h}, got {bb.ymax}"
    
        # Check the bottom face is at y = 0
        assert abs(bb.ymin - 0) < TOL, \
            f"Bottom Y: expected 0, got {bb.ymin}"
    
        # Verify a point inside the rectangle portion is inside the solid
        rect_interior = (0, rect_h / 2, extrude_d / 2)
        assert result.val().isInside(rect_interior), \
            f"Point {rect_interior} should be inside the solid (rectangle region)"
    
        # Verify a point inside the trapezium portion is inside the solid
        trap_interior = (0, rect_h + trap_h / 2, extrude_d / 2)
        assert result.val().isInside(trap_interior), \
            f"Point {trap_interior} should be inside the solid (trapezium region)"
    
        # Verify a point in the notch (outside the solid) is NOT inside
        # At y = rect_h + 1 = 41, the trapezium right boundary is at:
        # x = half_ts + (half_tl - half_ts) * (1/trap_h) = 15 + 15*(1/30) = 15.5
        # So x=25 at y=41 should be outside
        notch_point = (25.0, rect_h + 1.0, extrude_d / 2)
        assert not result.val().isInside(notch_point), \
            f"Point {notch_point} should be OUTSIDE the solid (notch region)"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        print(f"  Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681760/gpt_generated.stl')
