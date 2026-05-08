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
        pipe_outer_r   = 10.0   # pipe outer radius (diameter 20mm)
        pipe_inner_r   = 8.0    # pipe inner radius (diameter 16mm), wall = 2mm
        pipe_length    = 60.0   # total pipe length
        flange_outer_r = 17.0   # flange outer radius (diameter 34mm)
        flange_thick   = 2.0    # flange thickness (very thin)
    
        # --- Step 1: Create the pipe body ---
        # Extrude the outer circle positively to form the pipe cylinder
        pipe = (
            cq.Workplane("XY")
            .circle(pipe_outer_r)
            .extrude(pipe_length)
        )
    
        # --- Step 2: Cut the inner bore (hollow the pipe) ---
        # Negative extrusion of the inner circle through the full pipe length
        pipe = (
            pipe
            .faces(">Z")
            .workplane()
            .circle(pipe_inner_r)
            .cutThruAll()
        )
    
        # --- Step 3: Add the thin flange at the bottom end (z=0 face) ---
        # The flange is a thin disc at the base of the pipe, wider than the pipe OD
        flange = (
            cq.Workplane("XY")
            .circle(flange_outer_r)
            .extrude(flange_thick)
        )
    
        # --- Step 4: Cut the bore through the flange as well ---
        flange = (
            flange
            .faces(">Z")
            .workplane()
            .circle(pipe_inner_r)
            .cutThruAll()
        )
    
        # --- Step 5: Position the flange below the pipe (at z = -flange_thick) ---
        # The pipe starts at z=0 and goes to z=pipe_length
        # The flange sits at z=-flange_thick to z=0
        flange = flange.translate((0, 0, -flange_thick))
    
        # --- Step 6: Union pipe and flange ---
        result = pipe.union(flange)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        total_height = pipe_length + flange_thick  # 62mm
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total height: expected {total_height}, got {bb.zlen}"
        assert abs(bb.xlen - 2 * flange_outer_r) < TOL, \
            f"X extent: expected {2*flange_outer_r}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * flange_outer_r) < TOL, \
            f"Y extent: expected {2*flange_outer_r}, got {bb.ylen}"
    
        # Z extents: bottom of flange to top of pipe
        assert abs(bb.zmin - (-flange_thick)) < TOL, \
            f"Z min: expected {-flange_thick}, got {bb.zmin}"
        assert abs(bb.zmax - pipe_length) < TOL, \
            f"Z max: expected {pipe_length}, got {bb.zmax}"
    
        # Volume check
        # Pipe annulus volume: pi*(R_outer^2 - R_inner^2)*pipe_length
        pipe_vol = math.pi * (pipe_outer_r**2 - pipe_inner_r**2) * pipe_length
        # Flange annulus volume: pi*(R_flange^2 - R_inner^2)*flange_thick
        flange_vol = math.pi * (flange_outer_r**2 - pipe_inner_r**2) * flange_thick
        expected_vol = pipe_vol + flange_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: pipe outer, pipe inner bore, flange outer, flange inner (same bore)
        # After union: outer pipe cylinder, inner bore cylinder, flange outer cylinder
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 3, \
            f"Expected at least 3 cylindrical faces, got {cyl_faces}"
    
        # Check the bore is hollow: a point on the axis inside the pipe should be outside the solid
        solid = result.val()
        axis_point_mid = (0, 0, pipe_length / 2)  # center of pipe bore
        assert not solid.isInside(axis_point_mid), \
            f"Pipe bore should be hollow at {axis_point_mid}, but point is inside solid"
    
        # Check a point in the pipe wall is inside the solid
        wall_point = (pipe_outer_r - 0.5, 0, pipe_length / 2)
        assert solid.isInside(wall_point), \
            f"Point in pipe wall {wall_point} should be inside solid"
    
        # Check a point in the flange (outside pipe OD) is inside the solid
        flange_point = (flange_outer_r - 0.5, 0, -flange_thick / 2)
        assert solid.isInside(flange_point), \
            f"Point in flange {flange_point} should be inside solid"
    
        # Check a point outside the flange OD is outside the solid
        outside_point = (flange_outer_r + 1.0, 0, -flange_thick / 2)
        assert not solid.isInside(outside_point), \
            f"Point outside flange {outside_point} should be outside solid"
    
        # Symmetry: center of mass should be near x=0, y=0
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y should be ~0, got {com.y}"
    
        print("All assertions passed!")
        print(f"  Total height: {bb.zlen:.2f} mm")
        print(f"  Flange OD: {bb.xlen:.2f} mm")
        print(f"  Volume: {actual_vol:.2f} mm³ (expected {expected_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00039012/gpt_generated.stl')
