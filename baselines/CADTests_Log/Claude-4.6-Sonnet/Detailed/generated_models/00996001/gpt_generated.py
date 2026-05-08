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
        col_width    = 0.416667   # width of each upright column
        horiz_width  = 0.083333   # thickness of horizontal connecting bar
        extrude_h    = 0.475      # extrusion depth in +Z direction
        hole_diam    = 0.1375     # hole diameter
        hole_radius  = hole_diam / 2.0
    
        # Derived dimensions
        total_width   = col_width + horiz_width + col_width  # ≈ 0.916667
        profile_h     = 1.0                                  # total height of U profile (Y axis)
        upright_h     = profile_h - horiz_width              # height of the leg portion ≈ 0.916667
    
        # --- Step 1: Build U-shaped profile in XY plane, extrude in +Z ---
        # Profile: x = width axis (0 → total_width), y = height axis (0 → profile_h)
        # Extrusion: +Z direction (depth = extrude_h)
        # Resulting bounding box: xlen=total_width, ylen=profile_h, zlen=extrude_h
        #
        # U-shape vertices (open at top, legs point up = inverted table):
        #   (0, 0) → (total_width, 0)                       bottom outer
        #   → (total_width, profile_h)                       top-right outer
        #   → (total_width - col_width, profile_h)           top-right inner
        #   → (total_width - col_width, horiz_width)         inner right corner of bar
        #   → (col_width, horiz_width)                       inner left corner of bar
        #   → (col_width, profile_h)                         top-left inner
        #   → (0, profile_h)                                 top-left outer
        #   → close back to (0, 0)
        result = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(total_width, 0)
            .lineTo(total_width, profile_h)
            .lineTo(total_width - col_width, profile_h)
            .lineTo(total_width - col_width, horiz_width)
            .lineTo(col_width, horiz_width)
            .lineTo(col_width, profile_h)
            .lineTo(0, profile_h)
            .close()
            .extrude(extrude_h)
        )
    
        # --- Step 2: Drill hole through the horizontal bar ---
        # The horizontal bar occupies z = 0 to z = extrude_h (full depth),
        # and y = 0 to y = horiz_width (bar thickness in profile height direction).
        # The hole is at the center of the horizontal surface:
        #   x_center = total_width / 2
        #   z_center = extrude_h / 2  (center along extrusion depth)
        # The hole goes through the bar in the Y direction (through horiz_width thickness).
        #
        # Select the face at minimum Y (y=0, the bottom of the horizontal bar),
        # create a workplane there, and drill the hole through horiz_width in +Y.
        x_center = total_width / 2.0   # ≈ 0.458333
        z_center = extrude_h / 2.0     # ≈ 0.2375
    
        result = (
            result
            .faces("<Y")
            .workplane()
            .pushPoints([(x_center, z_center)])
            .hole(hole_diam, horiz_width)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Use findSolid() to reliably get the main body
        solid = result.findSolid()
        bb    = solid.BoundingBox()
    
        # 1. Bounding box checks
        # Profile drawn in XY: x=total_width, y=profile_h; extruded in Z: z=extrude_h
        assert abs(bb.xlen - total_width) < TOL, \
            f"X length: expected {total_width:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - profile_h) < TOL, \
            f"Y length: expected {profile_h:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h:.6f}, got {bb.zlen:.6f}"
    
        # 2. Volume check
        # U cross-section area = full rectangle − inner cutout
        inner_w      = total_width - 2 * col_width   # = horiz_width ≈ 0.083333
        u_area       = total_width * profile_h - inner_w * upright_h
        hole_vol     = math.pi * hole_radius**2 * horiz_width
        expected_vol = u_area * extrude_h - hole_vol
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # 3. Cylindrical face for the hole wall
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count >= 1, \
            f"Expected ≥1 cylindrical face (hole wall), got {cyl_count}"
    
        # 4. Point-in-solid checks
        # Left upright should be solid (x in left col, y mid-height, z mid-depth)
        pt_left = (col_width / 2.0, profile_h / 2.0, extrude_h / 2.0)
        assert solid.isInside(pt_left), \
            f"Left upright point {pt_left} should be inside solid"
    
        # Right upright should be solid
        pt_right = (total_width - col_width / 2.0, profile_h / 2.0, extrude_h / 2.0)
        assert solid.isInside(pt_right), \
            f"Right upright point {pt_right} should be inside solid"
    
        # Horizontal bar material (near left edge, away from hole) should be solid
        pt_bar = (col_width / 4.0, horiz_width / 2.0, extrude_h / 2.0)
        assert solid.isInside(pt_bar), \
            f"Horizontal bar point {pt_bar} should be inside solid"
    
        # Center of hole axis should be outside (inside the hole)
        pt_hole = (x_center, horiz_width / 2.0, z_center)
        assert not solid.isInside(pt_hole, tolerance=1e-3), \
            f"Hole center point {pt_hole} should be outside solid (inside hole)"
    
        # Gap between uprights (above bar, y > horiz_width) should be empty
        pt_gap = (x_center, (horiz_width + profile_h) / 2.0, extrude_h / 2.0)
        assert not solid.isInside(pt_gap), \
            f"Gap point {pt_gap} should be outside solid"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00996001/gpt_generated.stl')
