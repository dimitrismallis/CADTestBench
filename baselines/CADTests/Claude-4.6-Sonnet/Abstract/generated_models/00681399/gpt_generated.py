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
        sq_side   = 40.0   # square block side length
        sq_height = 20.0   # square block height
        hole_d    = 16.0   # hole diameter (and pipe inner diameter)
        hole_r    = hole_d / 2.0
        pipe_od   = 20.0   # pipe outer diameter
        pipe_or   = pipe_od / 2.0
        pipe_h    = 18.0   # pipe height (almost same as block height)
    
        # --- Step 1: Create the square block ---
        # Extrude a 40x40 square to height 20mm
        result = cq.Workplane("XY").rect(sq_side, sq_side).extrude(sq_height)
    
        # --- Step 2: Negative extrusion (hole) through the square block ---
        # Sketch a circle at the center of the top face and cut through
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Step 3: Sketch annulus on the top face of the square block ---
        # The annulus has inner radius = hole_r, outer radius = pipe_or
        # Extrude upward by pipe_h (18mm)
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(pipe_or)   # outer circle
            .circle(hole_r)    # inner circle (creates annular region)
            .extrude(pipe_h)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        # X and Y should still be 40mm (square block dominates)
        assert abs(bb.xlen - sq_side) < TOL, f"BB xlen: expected {sq_side}, got {bb.xlen}"
        assert abs(bb.ylen - sq_side) < TOL, f"BB ylen: expected {sq_side}, got {bb.ylen}"
        # Total Z height = block (20) + pipe (18) = 38mm
        expected_total_h = sq_height + pipe_h
        assert abs(bb.zlen - expected_total_h) < TOL, f"BB zlen: expected {expected_total_h}, got {bb.zlen}"
    
        # Z extents: bottom at 0, top at 38
        assert abs(bb.zmin - 0.0) < TOL, f"BB zmin: expected 0.0, got {bb.zmin}"
        assert abs(bb.zmax - expected_total_h) < TOL, f"BB zmax: expected {expected_total_h}, got {bb.zmax}"
    
        # Volume check:
        # Block volume = 40*40*20 = 32000
        # Hole volume  = pi * 8^2 * 20 = 4021.24
        # Pipe volume  = pi * (10^2 - 8^2) * 18 = pi * 36 * 18 = 2035.75
        block_vol = sq_side * sq_side * sq_height
        hole_vol  = math.pi * hole_r**2 * sq_height
        pipe_vol  = math.pi * (pipe_or**2 - hole_r**2) * pipe_h
        expected_vol = block_vol - hole_vol + pipe_vol
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: hole inner wall + pipe inner wall + pipe outer wall = 3 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check hole exists: a point at center of block mid-height should be outside (inside the hole)
        center_mid = (0.0, 0.0, sq_height / 2.0)
        assert not solid.isInside(center_mid), \
            f"Center of block at mid-height should be inside the hole (outside solid), but isInside returned True"
    
        # Check pipe wall exists: a point at pipe outer radius midpoint should be inside the solid
        pipe_mid_z = sq_height + pipe_h / 2.0
        pipe_wall_pt = ((hole_r + pipe_or) / 2.0, 0.0, pipe_mid_z)
        assert solid.isInside(pipe_wall_pt), \
            f"Point in pipe wall at {pipe_wall_pt} should be inside solid, but isInside returned False"
    
        # Check that a point outside the pipe outer radius at pipe height is outside the solid
        outside_pipe_pt = (pipe_or + 5.0, 0.0, pipe_mid_z)
        assert not solid.isInside(outside_pipe_pt), \
            f"Point outside pipe at {outside_pipe_pt} should be outside solid, but isInside returned True"
    
        # Check that the block corner is inside the solid
        block_corner_pt = (sq_side / 2.0 - 1.0, sq_side / 2.0 - 1.0, sq_height / 2.0)
        assert solid.isInside(block_corner_pt), \
            f"Block corner point {block_corner_pt} should be inside solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f} mm³)")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681399/gpt_generated.stl')
