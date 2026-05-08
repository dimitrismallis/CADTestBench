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
        cyl_height = 0.6
        cyl_diameter = 1.498046
        cyl_radius = cyl_diameter / 2.0  # 0.749023
    
        hole_diameter = 0.748126
        hole_radius = hole_diameter / 2.0  # 0.374063
    
        chan_length = 0.188827   # radial extent
        chan_width = cyl_diameter / 2.0  # 0.749023 (half diameter)
        chan_depth = cyl_height  # 0.6
    
        padding = 0.142454  # from outer edge of cylinder inward to start of channel
    
        # --- Step 1: Create the base cylinder ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Cut the central hole through the cylinder ---
        result = result.faces(">Z").workplane().hole(hole_diameter)
    
        # --- Step 3: Create and union the rectangular channel ---
        # The channel is attached to the outer edge of the cylinder.
        # Padding = 0.142454 from the outer edge means the channel starts at:
        #   x_start = cyl_radius - padding = 0.749023 - 0.142454 = 0.606569
        # The channel extends outward (in +X) by chan_length = 0.188827
        #   x_end = x_start + chan_length = 0.795396
        # Channel center in X: x_start + chan_length/2 = 0.606569 + 0.094414 = 0.700983
    
        x_start = cyl_radius - padding  # 0.606569
        x_end = x_start + chan_length    # 0.795396
        chan_center_x = x_start + chan_length / 2.0  # 0.700983
    
        channel = (
            cq.Workplane("XY")
            .box(chan_length, chan_width, chan_depth,
                 centered=(True, True, True))
            .translate((chan_center_x, 0, 0))
        )
    
        result = result.union(channel)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X: cylinder goes from -cyl_radius to +cyl_radius
        # Channel extends to x_end = 0.795396 (beyond cylinder radius)
        expected_xmin = -cyl_radius   # -0.749023
        expected_xmax = x_end          # 0.795396
        expected_xlen = expected_xmax - expected_xmin  # 1.544419
    
        assert abs(bb.xmin - expected_xmin) < TOL, \
            f"xmin: expected {expected_xmin:.4f}, got {bb.xmin:.4f}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"xmax: expected {expected_xmax:.4f}, got {bb.xmax:.4f}"
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"xlen: expected {expected_xlen:.4f}, got {bb.xlen:.4f}"
    
        # Y: cylinder diameter = 1.498046 dominates (channel width = 0.749023 < cyl_diameter)
        assert abs(bb.ylen - cyl_diameter) < TOL, \
            f"ylen: expected {cyl_diameter:.4f}, got {bb.ylen:.4f}"
    
        # Z: cylinder height = 0.6, channel depth = 0.6 (same)
        assert abs(bb.zlen - cyl_height) < TOL, \
            f"zlen: expected {cyl_height:.4f}, got {bb.zlen:.4f}"
    
        # Volume check
        vol_cylinder = math.pi * cyl_radius**2 * cyl_height
        vol_hole = math.pi * hole_radius**2 * cyl_height
        vol_annular = vol_cylinder - vol_hole
        vol_channel_box = chan_length * chan_width * chan_depth
        # Total approximate: annular cylinder + full channel box
        # (channel box partially overlaps cylinder, so actual vol < vol_annular + vol_channel_box)
        vol_total_approx = vol_annular + vol_channel_box
        actual_vol = solid.Volume()
        # Allow 20% tolerance since overlap subtraction is complex
        assert abs(actual_vol - vol_total_approx) / vol_total_approx < 0.20, \
            f"Volume: expected ~{vol_total_approx:.4f}, got {actual_vol:.4f}"
    
        # Check cylindrical faces exist (outer cylinder surface + inner hole surface)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check the hole is hollow: center point should NOT be inside solid
        assert not solid.isInside((0, 0, 0)), \
            "Center of cylinder should be hollow (hole), but isInside returned True"
    
        # Check a point inside the cylinder wall is inside the solid
        wall_point = (cyl_radius * 0.8, 0, 0)
        assert solid.isInside(wall_point), \
            f"Point in cylinder wall {wall_point} should be inside solid"
    
        # Check channel exists: a point beyond cylinder radius but within channel x_end
        # Channel outside cylinder: x in (cyl_radius, x_end) = (0.749023, 0.795396)
        # Midpoint: (0.749023 + 0.795396) / 2 = 0.772210
        channel_outside_x = (cyl_radius + x_end) / 2.0  # ~0.772210
        channel_point = (channel_outside_x, 0, 0)
        assert solid.isInside(channel_point), \
            f"Point in channel beyond cylinder radius {channel_point} should be inside solid"
    
        # Check a point clearly outside the model is not inside
        outside_point = (x_end + 0.1, 0, 0)
        assert not solid.isInside(outside_point), \
            f"Point outside model {outside_point} should not be inside solid"
    
        # Check top and bottom faces exist
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
        assert bot_faces >= 1, f"Expected at least 1 bottom face, got {bot_faces}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], "
              f"y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {actual_vol:.4f} (expected ~{vol_total_approx:.4f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Channel outside-cylinder test point: {channel_point}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672309/gpt_generated.stl')
