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
        width = 40.0       # tag width
        height = 60.0      # tag height
        thickness = 3.0    # tag thickness
        fillet_r = 8.0     # top corner fillet radius
        hole_d = 5.0       # hole diameter
        hole_r = hole_d / 2.0
        # Hole center: centered horizontally, slightly below top edge
        hole_offset_from_top = 8.0
        hole_y = height / 2.0 - hole_offset_from_top  # in local sketch coords
    
        hw = width / 2.0
        hh = height / 2.0
        r = fillet_r
    
        # --- Step 1: Create the tag profile with correct arc geometry ---
        # Quarter-circle arc at top-right corner:
        #   start: (hw, hh - r)
        #   mid:   (hw - r + r*cos(45°), hh - r + r*sin(45°))
        #   end:   (hw - r, hh)
        cos45 = math.cos(math.pi / 4)
        sin45 = math.sin(math.pi / 4)
    
        # Arc midpoint for top-right corner (center of arc is at (hw-r, hh-r))
        tr_mid_x = (hw - r) + r * cos45
        tr_mid_y = (hh - r) + r * sin45
    
        # Arc midpoint for top-left corner (center of arc is at (-hw+r, hh-r))
        tl_mid_x = (-hw + r) - r * cos45
        tl_mid_y = (hh - r) + r * sin45
    
        tag_profile = (
            cq.Workplane("XY")
            .moveTo(-hw, -hh)                    # bottom-left (sharp)
            .lineTo(hw, -hh)                     # bottom edge →
            .lineTo(hw, hh - r)                  # right edge ↑ to arc start
            .threePointArc((tr_mid_x, tr_mid_y), (hw - r, hh))   # top-right arc
            .lineTo(-hw + r, hh)                 # top edge ←
            .threePointArc((tl_mid_x, tl_mid_y), (-hw, hh - r))  # top-left arc
            .lineTo(-hw, -hh)                    # left edge ↓
            .close()
        )
    
        # --- Step 2: Extrude the profile ---
        result = tag_profile.extrude(thickness)
    
        # --- Step 3: Add circular hole near top, centered ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .center(0, hole_y)
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Check bounding box
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - width) < TOL, f"Width: expected {width}, got {bb.xlen}"
        assert abs(bb.ylen - height) < TOL, f"Height: expected {height}, got {bb.ylen}"
        assert abs(bb.zlen - thickness) < TOL, f"Thickness: expected {thickness}, got {bb.zlen}"
    
        # Check that the object is centered at x=0
        assert abs(bb.xmin + bb.xmax) < TOL, f"Not centered in X: xmin={bb.xmin}, xmax={bb.xmax}"
    
        # Check volume: should be less than full box (due to rounded corners and hole)
        full_box_vol = width * height * thickness
        actual_vol = result.val().Volume()
        assert actual_vol < full_box_vol, f"Volume should be less than full box {full_box_vol}, got {actual_vol}"
        assert actual_vol > 0, f"Volume should be positive, got {actual_vol}"
    
        # Volume reduction from 2 top rounded corners + hole
        # Each corner removes a square area minus a quarter circle
        corner_removal = 2 * (r**2 - math.pi * r**2 / 4) * thickness
        hole_vol = math.pi * hole_r**2 * thickness
        expected_vol = full_box_vol - corner_removal - hole_vol
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check cylindrical face exists (the hole)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face (hole), got {cyl_faces}"
    
        # Check the hole goes through: a point at the hole center should NOT be inside the solid
        hole_center_point = (0, hole_y, thickness / 2.0)
        solid = result.val()
        assert not solid.isInside(hole_center_point), \
            f"Point at hole center {hole_center_point} should be outside (in the hole)"
    
        # Check a point in the body IS inside
        body_point = (0, 0, thickness / 2.0)
        assert solid.isInside(body_point), \
            f"Point in body {body_point} should be inside the solid"
    
        # Check top face is at correct Z
        assert abs(bb.zmax - thickness) < TOL, f"Top Z: expected {thickness}, got {bb.zmax}"
        assert abs(bb.zmin) < TOL, f"Bottom Z: expected 0, got {bb.zmin}"
    
        print(f"✓ Tag model created successfully")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected ~{expected_vol:.2f} mm³)")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00670266/gpt_generated.stl')
