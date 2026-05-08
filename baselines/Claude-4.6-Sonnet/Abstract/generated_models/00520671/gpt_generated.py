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
        base_r = 20.0       # base cylinder radius
        base_h = 3.0        # base cylinder height (slight extrusion)
        inner_r = 8.0       # second (inner) cylinder radius
        inner_h = 12.0      # second cylinder height (taller extrusion)
        rect_w = 6.0        # rectangle cut width (Y direction)
        rect_d = 5.0        # rectangle cut depth (X direction)
        rect_h = base_h     # cut through full base height
    
        # --- Step 1: Create the base (first) cylinder, slightly extruded ---
        base = (
            cq.Workplane("XY")
            .circle(base_r)
            .extrude(base_h)
        )
    
        # --- Step 2: Create the second cylinder in the middle, extruded taller ---
        # The second cylinder sits on top of the base cylinder, centered at (0,0)
        inner = (
            cq.Workplane("XY")
            .workplane(offset=base_h)
            .circle(inner_r)
            .extrude(inner_h)
        )
    
        # Union the two cylinders
        result = base.union(inner)
    
        # --- Step 3: Cut a small rectangle on the right side of the second cylinder ---
        # Position the rectangle on the right side (+X) of the inner cylinder,
        # cutting into the base cylinder only (Z from 0 to base_h).
        # The rectangle starts at x = inner_r (right edge of inner cylinder)
        # and extends outward by rect_d, centered in Y.
        # We place the cutting box so its left face is at x = inner_r.
        cut_x_center = inner_r + rect_d / 2.0  # center of the cutting box in X
        cut_z_center = base_h / 2.0            # center in Z (middle of base height)
    
        rect_cut = (
            cq.Workplane("XY")
            .box(rect_d, rect_w, rect_h,
                 centered=False)
            .translate((inner_r, -rect_w / 2.0, 0))
        )
    
        result = result.cut(rect_cut)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks:
        # X: should span from -base_r to +base_r (the cut only removes material, doesn't extend)
        assert abs(bb.xmin - (-base_r)) < TOL, f"xmin expected {-base_r}, got {bb.xmin}"
        assert abs(bb.xmax - base_r) < TOL, f"xmax expected {base_r}, got {bb.xmax}"
    
        # Y: should span from -base_r to +base_r
        assert abs(bb.ymin - (-base_r)) < TOL, f"ymin expected {-base_r}, got {bb.ymin}"
        assert abs(bb.ymax - base_r) < TOL, f"ymax expected {base_r}, got {bb.ymax}"
    
        # Z: from 0 to base_h + inner_h
        total_h = base_h + inner_h
        assert abs(bb.zmin - 0.0) < TOL, f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_h) < TOL, f"zmax expected {total_h}, got {bb.zmax}"
    
        # Volume check:
        # Base cylinder volume
        vol_base = math.pi * base_r**2 * base_h
        # Inner cylinder volume
        vol_inner = math.pi * inner_r**2 * inner_h
        # Rectangle cut volume (approximate — it's clipped by the base cylinder boundary)
        # The cut box goes from x=inner_r to x=inner_r+rect_d, y=-rect_w/2 to y=+rect_w/2, z=0 to z=base_h
        # Part of this box may be outside the base cylinder, so actual removed volume <= rect_d*rect_w*rect_h
        vol_rect_max = rect_d * rect_w * rect_h  # upper bound on removed volume
        expected_vol_max = vol_base + vol_inner  # no cut
        expected_vol_min = vol_base + vol_inner - vol_rect_max  # max cut
    
        actual_vol = result.val().Volume()
        assert actual_vol < expected_vol_max, f"Volume should be less than uncut: {expected_vol_max:.2f}, got {actual_vol:.2f}"
        assert actual_vol > expected_vol_min - TOL, f"Volume too small: min expected ~{expected_vol_min:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical faces exist (base cylinder curved face + inner cylinder curved face)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check that the inner cylinder top face is at z = base_h + inner_h
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_h) < TOL, f"Top face Z expected {total_h}, got {top_face_z}"
    
        # Check that the bottom face is at z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, f"Bottom face Z expected 0, got {bot_face_z}"
    
        # Check the rectangle cut exists: a point inside the cut region should be outside the solid
        # Point in the middle of the cut region (inside the base cylinder's original extent but in the cut)
        cut_test_point = (inner_r + rect_d / 2.0, 0.0, base_h / 2.0)
        is_inside = result.val().isInside(cut_test_point)
        assert not is_inside, f"Point {cut_test_point} should be outside (in the cut), but is inside the solid"
    
        # Check a point inside the base cylinder (not in the cut) is inside the solid
        inside_test_point = (-10.0, 0.0, base_h / 2.0)
        assert result.val().isInside(inside_test_point), f"Point {inside_test_point} should be inside the solid"
    
        # Check a point inside the inner cylinder is inside the solid
        inner_test_point = (0.0, 0.0, base_h + inner_h / 2.0)
        assert result.val().isInside(inner_test_point), f"Point {inner_test_point} should be inside the inner cylinder"
    
        print("All assertions passed!")
        print(f"  Bounding box: X=[{bb.xmin:.2f}, {bb.xmax:.2f}], Y=[{bb.ymin:.2f}, {bb.ymax:.2f}], Z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"  Volume: {actual_vol:.2f} mm³")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520671/gpt_generated.stl')
