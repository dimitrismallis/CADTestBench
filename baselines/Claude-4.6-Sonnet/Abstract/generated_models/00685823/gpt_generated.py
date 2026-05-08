import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        side = 50.0       # square side length
        radius = 25.0     # quarter-circle cutout radius
        height = 20.0     # extrusion height
    
        # --- Step 1: Draw the 2D profile ---
        # Square occupies [0, side] x [0, side] in XY plane.
        # Top-right corner is at (side, side).
        # The quarter-circle cutout is centered at (side, side) with given radius.
        # Arc goes from (side, side - radius) to (side - radius, side).
        # The arc is concave (curves inward toward the corner).
        #
        # Arc center: (side, side) = (50, 50)
        # Arc start:  (50, 25)  -- on the right edge
        # Arc end:    (25, 50)  -- on the top edge
        # Arc midpoint at 45° from center (pointing bottom-left from corner):
        #   (50 - 25*cos(45°), 50 - 25*sin(45°)) = (50 - 17.678, 50 - 17.678) = (32.322, 32.322)
        #
        # Trace outline counter-clockwise:
        #   (0,0) → (50,0) → (50,25) → arc → (25,50) → (0,50) → close
    
        arc_mid_x = side - radius * math.cos(math.radians(45))
        arc_mid_y = side - radius * math.sin(math.radians(45))
    
        profile = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(side, 0)
            .lineTo(side, side - radius)
            .threePointArc(
                (arc_mid_x, arc_mid_y),
                (side - radius, side)
            )
            .lineTo(0, side)
            .close()
        )
    
        # --- Step 2: Extrude the profile ---
        result = profile.extrude(height)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - side) < TOL, f"X length: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side) < TOL, f"Y length: expected {side}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Bounding box origin (starts at 0)
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Volume check:
        # Full square volume minus quarter-cylinder volume
        full_vol = side * side * height
        quarter_cyl_vol = math.pi * radius**2 * height / 4.0
        expected_vol = full_vol - quarter_cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count:
        # Bottom face (1) + Top face (1) + Left side (1) + Bottom side (1) +
        # Right side partial (1) + Top side partial (1) + Curved cylindrical face (1) = 7
        face_count = result.faces().size()
        assert face_count == 7, f"Face count: expected 7, got {face_count}"
    
        # Check cylindrical face exists (the arc cutout)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 6, f"Planar faces: expected 6, got {planar_faces}"
    
        # The top-right corner should NOT be inside the solid (it was cut out)
        top_right_inside = result.val().isInside((side - 1, side - 1, height / 2))
        assert not top_right_inside, "Top-right corner should be cut out but is inside the solid"
    
        # The bottom-left area should be inside the solid
        bottom_left_inside = result.val().isInside((1, 1, height / 2))
        assert bottom_left_inside, "Bottom-left area should be inside the solid"
    
        # Center of the square at mid-height should be inside
        center_inside = result.val().isInside((side / 2, side / 2, height / 2))
        assert center_inside, f"Center of square should be inside the solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00685823/gpt_generated.stl')
