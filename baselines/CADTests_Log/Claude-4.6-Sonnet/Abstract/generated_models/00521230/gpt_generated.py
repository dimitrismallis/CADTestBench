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
        cyl_radius   = 5.0      # cylinder radius (diameter = 10mm)
        cyl_height   = 100.0    # long and thin
        hole_dia     = 8.0      # slightly smaller than cylinder diameter (10mm)
        hole_radius  = hole_dia / 2.0
    
        # Hole Z positions (cylinder centered at origin, z from -50 to +50)
        top_hole_z    = 40.0    # near top (10mm from top face)
        bottom_hole_z = -35.0   # near bottom but slightly closer to center than top hole
                                 # (15mm from bottom face, vs 10mm from top)
    
        # --- Step 1: Create the long thin cylinder along Z axis ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Drill the top hole (near top, along X axis) ---
        # Use a cutting cylinder oriented along X, placed at z = top_hole_z
        top_hole_cutter = (
            cq.Workplane("YZ")
            .workplane(offset=-cyl_radius - 1)   # start outside the cylinder
            .center(0, top_hole_z)               # move to correct Z height
            .circle(hole_radius)
            .extrude(2 * (cyl_radius + 1))       # cut all the way through
        )
        result = result.cut(top_hole_cutter)
    
        # --- Step 3: Drill bottom hole 1 (near bottom, along X axis) ---
        bottom_hole1_cutter = (
            cq.Workplane("YZ")
            .workplane(offset=-cyl_radius - 1)
            .center(0, bottom_hole_z)
            .circle(hole_radius)
            .extrude(2 * (cyl_radius + 1))
        )
        result = result.cut(bottom_hole1_cutter)
    
        # --- Step 4: Drill bottom hole 2 (near bottom, along Y axis) ---
        bottom_hole2_cutter = (
            cq.Workplane("XZ")
            .workplane(offset=-cyl_radius - 1)
            .center(0, bottom_hole_z)
            .circle(hole_radius)
            .extrude(2 * (cyl_radius + 1))
        )
        result = result.cut(bottom_hole2_cutter)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # 1. Bounding box: cylinder is 10mm diameter, 100mm tall
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - 10.0) < TOL, f"X extent: expected 10.0, got {bb.xlen}"
        assert abs(bb.ylen - 10.0) < TOL, f"Y extent: expected 10.0, got {bb.ylen}"
        assert abs(bb.zlen - 100.0) < TOL, f"Z extent: expected 100.0, got {bb.zlen}"
    
        # 2. Volume: solid cylinder minus three hole volumes
        #    Solid cylinder volume = pi * r^2 * h = pi * 25 * 100
        #    Each hole is a cylinder of radius 4, length = 2*cyl_radius = 10
        #    But holes intersect the cylinder, so actual removed volume per hole
        #    is the chord-based intersection. Approximate check: volume < solid cylinder
        solid_vol = math.pi * cyl_radius**2 * cyl_height
        actual_vol = result.val().Volume()
        assert actual_vol < solid_vol, f"Volume should be less than solid cylinder ({solid_vol:.2f}), got {actual_vol:.2f}"
        assert actual_vol > 0.5 * solid_vol, f"Volume too small, likely over-cut: got {actual_vol:.2f}"
    
        # 3. Check cylindrical faces exist (the main cylinder body + hole walls)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, f"Expected at least 4 cylindrical faces (1 outer + 3 holes), got {cyl_faces}"
    
        # 4. Check that holes exist by probing points inside the hole channels
        shape = result.val()
    
        # Top hole along X at z=40: point at (0, 0, 40) should be OUTSIDE (inside the hole)
        top_hole_center = (0.0, 0.0, top_hole_z)
        assert not shape.isInside(top_hole_center), \
            f"Point {top_hole_center} should be inside the hole (outside solid), but isInside returned True"
    
        # Bottom hole 1 along X at z=-35: point at (0, 0, -35) should be OUTSIDE
        bot_hole_center = (0.0, 0.0, bottom_hole_z)
        assert not shape.isInside(bot_hole_center), \
            f"Point {bot_hole_center} should be inside the hole (outside solid), but isInside returned True"
    
        # 5. Solid cylinder body: a point at center z=0 should be INSIDE
        assert shape.isInside((0.0, 0.0, 0.0)), \
            "Center of cylinder (0,0,0) should be inside the solid"
    
        # 6. Point near top of cylinder (not in hole) should be inside
        assert shape.isInside((0.0, 0.0, 48.0)), \
            "Point near top (0,0,48) should be inside the solid"
    
        # 7. Point outside cylinder radius should be outside
        assert not shape.isInside((8.0, 0.0, 0.0)), \
            "Point outside cylinder radius (8,0,0) should not be inside the solid"
    
        # 8. Check faces along Z (top and bottom flat faces)
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
        assert bot_faces >= 1, f"Expected at least 1 bottom face, got {bot_faces}"
    
        # 9. Verify the top hole is higher than the bottom holes (z positions)
        assert top_hole_z > bottom_hole_z, \
            f"Top hole z ({top_hole_z}) should be greater than bottom hole z ({bottom_hole_z})"
    
        # 10. Verify bottom holes are closer to center (z=0) than top hole
        assert abs(bottom_hole_z) < abs(top_hole_z), \
            f"|bottom_hole_z| ({abs(bottom_hole_z)}) should be < |top_hole_z| ({abs(top_hole_z)})"
    
        print("All assertions passed!")
        print(f"  Cylinder: radius={cyl_radius}, height={cyl_height}")
        print(f"  Hole diameter: {hole_dia} (cylinder diameter: {2*cyl_radius})")
        print(f"  Top hole Z: {top_hole_z}, Bottom holes Z: {bottom_hole_z}")
        print(f"  Volume: {actual_vol:.2f} mm³ (solid would be {solid_vol:.2f} mm³)")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00521230/gpt_generated.stl')
