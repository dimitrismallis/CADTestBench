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
        outer_r = 20.0      # outer radius of pipe
        inner_r = 14.0      # inner radius (wall thickness = 6mm)
        height  = 60.0      # pipe height
        sector_angle = 90.0 # degrees of sector to cut out
    
        # --- Step 1: Create hollow cylinder (annular ring extruded) ---
        # Draw outer circle, then subtract inner circle to get annulus
        pipe = (
            cq.Workplane("XY")
            .circle(outer_r)
            .extrude(height)
        )
        # Cut inner cylinder to make it hollow
        pipe = (
            pipe
            .faces(">Z").workplane()
            .circle(inner_r)
            .cutThruAll()
        )
    
        # --- Step 2: Cut out a 90° sector ---
        # Build a sector cutter: a "pie slice" solid that spans the sector angle
        # We'll create it as a 2D profile (pie slice) and extrude it
        # The sector goes from 0° to 90° (in XY plane), covering full radial extent
        cut_r = outer_r + 2.0  # slightly larger than outer radius to ensure clean cut
    
        # Build the pie-slice profile using lineTo and arc
        sector_cutter = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .lineTo(cut_r, 0)                                          # along +X
            .threePointArc(
                (cut_r * math.cos(math.radians(45)),
                 cut_r * math.sin(math.radians(45))),                  # midpoint at 45°
                (cut_r * math.cos(math.radians(sector_angle)),
                 cut_r * math.sin(math.radians(sector_angle)))         # end at 90°
            )
            .close()
            .extrude(height)
        )
    
        # --- Step 3: Subtract the sector cutter from the pipe ---
        result = pipe.cut(sector_cutter)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for volume/area checks
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X: from -outer_r to +outer_r (the cut removes the +X+Y quadrant but the
        #    bounding box still spans -outer_r to +outer_r because the 270° arc remains)
        assert abs(bb.xlen - 2 * outer_r) < TOL, \
            f"X bounding box: expected {2*outer_r}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * outer_r) < TOL, \
            f"Y bounding box: expected {2*outer_r}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z bounding box: expected {height}, got {bb.zlen}"
    
        # Volume check:
        # Full annulus volume = pi * (R^2 - r^2) * h
        # After removing 90° sector (1/4 of the annulus):
        full_annulus_vol = math.pi * (outer_r**2 - inner_r**2) * height
        expected_vol = full_annulus_vol * (270.0 / 360.0)
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count checks:
        # The result should have:
        #   - 1 outer cylindrical face (270° arc)
        #   - 1 inner cylindrical face (270° arc)
        #   - 1 bottom flat annular face (270° arc annulus)
        #   - 1 top flat annular face (270° arc annulus)
        #   - 2 flat rectangular cut faces (the two radial cut planes at 0° and 90°)
        # Total = 6 faces
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # Check cylindrical faces (outer and inner curved surfaces)
        cyl_face_count = result.faces("%Cylinder").size()
        assert cyl_face_count == 2, \
            f"Cylindrical face count: expected 2, got {cyl_face_count}"
    
        # Check planar faces (top, bottom, and 2 radial cut faces)
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count == 4, \
            f"Planar face count: expected 4, got {planar_face_count}"
    
        # Check that the center of the pipe is hollow (a point inside the inner radius
        # at mid-height should be OUTSIDE the solid)
        mid_z = height / 2.0
        inner_point = (0.0, 0.0, mid_z)  # center axis — should be outside solid
        assert not result.val().isInside(inner_point), \
            "Center of pipe should be hollow (outside solid)"
    
        # Check that a point in the pipe wall (270° region) is inside the solid
        # At angle 180° (pointing -X), midway through wall, mid height
        wall_r = (outer_r + inner_r) / 2.0
        wall_point = (-wall_r, 0.0, mid_z)  # at 180°, in the wall
        assert result.val().isInside(wall_point), \
            f"Point in pipe wall at 180° should be inside solid: {wall_point}"
    
        # Check that a point in the cut sector is outside the solid
        # At angle 45° (midpoint of cut sector), midway through wall, mid height
        sector_point = (
            wall_r * math.cos(math.radians(45)),
            wall_r * math.sin(math.radians(45)),
            mid_z
        )
        assert not result.val().isInside(sector_point), \
            f"Point in cut sector at 45° should be outside solid: {sector_point}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00995686/gpt_generated.stl')
