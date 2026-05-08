import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_radius = 20.0
        inner_radius = 10.0   # ~half of outer
        height = 15.0
        channel_size = 6.0    # square side length
    
        # --- Step 1: Create cylinder by extruding a circle ---
        result = cq.Workplane("XY").circle(outer_radius).extrude(height)
    
        # --- Step 2: Cut central hole using cutThruAll for reliability ---
        result = (
            result
            .faces(">Z").workplane()
            .circle(inner_radius)
            .cutThruAll()
        )
    
        # --- Step 3: Create channel - small square connected to outer edge, cut through height ---
        # Square of side channel_size, centered at (outer_radius, 0) so it straddles the outer wall
        # Half of the square (3mm) is inside the cylinder, creating a slot/channel
        result = (
            result
            .faces(">Z").workplane()
            .center(outer_radius, 0.0)
            .rect(channel_size, channel_size)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # The channel cut is centered at x=outer_radius, spanning y=-channel_size/2..+channel_size/2.
        # This removes the outermost part of the cylinder in that y-range.
        # The new xmax is the cylinder arc at y=±(channel_size/2):
        #   xmax = sqrt(outer_radius² - (channel_size/2)²)
        expected_xmax = math.sqrt(outer_radius**2 - (channel_size / 2)**2)  # ~19.774
        assert abs(bb.xmin - (-outer_radius)) < TOL, \
            f"xmin expected {-outer_radius}, got {bb.xmin}"
        assert abs(bb.xmax - expected_xmax) < TOL, \
            f"xmax expected {expected_xmax:.4f}, got {bb.xmax}"
    
        # Y extent: cylinder goes from -outer_radius to +outer_radius (channel is symmetric in Y)
        assert abs(bb.ymin - (-outer_radius)) < TOL, \
            f"ymin expected {-outer_radius}, got {bb.ymin}"
        assert abs(bb.ymax - outer_radius) < TOL, \
            f"ymax expected {outer_radius}, got {bb.ymax}"
    
        # Z extent: 0 to height
        assert abs(bb.zmin - 0.0) < TOL, \
            f"zmin expected 0, got {bb.zmin}"
        assert abs(bb.zmax - height) < TOL, \
            f"zmax expected {height}, got {bb.zmax}"
    
        # Volume check:
        cyl_vol = math.pi * outer_radius**2 * height        # ~18849.6
        hole_vol = math.pi * inner_radius**2 * height       # ~4712.4
        actual_vol = result.val().Volume()
    
        # Volume must be less than full cylinder (cuts remove material)
        assert actual_vol < cyl_vol - TOL, \
            f"Volume should be less than full cylinder {cyl_vol:.2f}, got {actual_vol:.2f}"
        # Volume must be less than cylinder minus hole (channel also removes material)
        assert actual_vol < (cyl_vol - hole_vol) - TOL, \
            f"Volume should be less than cylinder-hole {cyl_vol - hole_vol:.2f}, got {actual_vol:.2f}"
        # Volume must be positive
        assert actual_vol > 0, \
            f"Volume should be positive, got {actual_vol}"
    
        # Check cylindrical faces exist (outer cylinder wall + inner hole wall = at least 2)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces (outer + inner hole), got {cyl_faces}"
    
        # Check planar faces exist (top, bottom, channel walls, etc.)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 4, \
            f"Expected at least 4 planar faces, got {planar_faces}"
    
        # Check the hole: center point should NOT be inside the solid
        center_point = (0.0, 0.0, height / 2)
        assert not result.val().isInside(center_point), \
            f"Center point {center_point} should be in the hole (not in solid)"
    
        # Check a point on the cylinder body IS inside the solid
        # x=15, y=0 is inside cylinder, outside hole, but check if it's in the channel
        # Channel spans x=17..23, y=-3..3 — so x=15 is outside channel
        body_point = (15.0, 0.0, height / 2)
        assert result.val().isInside(body_point), \
            f"Body point {body_point} should be inside the solid"
    
        # Check channel cut: point inside channel region should NOT be in solid
        # Channel square centered at x=20, spans x=17..23, y=-3..3
        # x=19, y=0 is inside the channel cut (inside cylinder boundary)
        channel_point = (outer_radius - 1.0, 0.0, height / 2)  # x=19, y=0
        assert not result.val().isInside(channel_point), \
            f"Channel point {channel_point} should be in the channel (not in solid)"
    
        # Check a point between hole and channel is solid
        # At x=15, y=5 — inside cylinder, outside hole, outside channel
        solid_check = (15.0, 5.0, height / 2)
        assert result.val().isInside(solid_check), \
            f"Point {solid_check} should be inside the solid body"
    
        print(f"All assertions passed!")
        print(f"Bounding box: x=[{bb.xmin:.2f}, {bb.xmax:.2f}], "
              f"y=[{bb.ymin:.2f}, {bb.ymax:.2f}], z=[{bb.zmin:.2f}, {bb.zmax:.2f}]")
        print(f"Volume: {actual_vol:.2f} mm³  (cyl={cyl_vol:.2f}, hole={hole_vol:.2f})")
        print(f"Cylindrical faces: {cyl_faces}, Planar faces: {planar_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672309/gpt_generated.stl')
