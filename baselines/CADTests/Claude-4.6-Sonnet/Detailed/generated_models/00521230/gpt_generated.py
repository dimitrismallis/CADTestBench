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
        cyl_diameter = 0.02262
        cyl_radius = cyl_diameter / 2.0       # 0.01131
        cyl_height = 0.75
    
        hole_diameter = 0.015476
        hole_radius = hole_diameter / 2.0     # 0.007738
    
        # Cylinder is centered at origin: bottom at z=-0.375, top at z=+0.375
        z_bottom = -cyl_height / 2.0   # -0.375
        z_top    =  cyl_height / 2.0   #  0.375
    
        # Hole positions along Z axis (distances from bottom/top edge)
        # Near top: 0.004167 from top edge
        z_top_hole_centered  = z_top    - 0.004167   #  0.370833
        # Near bottom (farther from center): 0.123228 from bottom
        z_bot_hole1_centered = z_bottom + 0.123228   # -0.251772
        # Near bottom (closer to center): 0.06399 from bottom
        z_bot_hole2_centered = z_bottom + 0.06399    # -0.31101
    
        # --- Step 1: Create the main cylinder along Z axis ---
        result = cq.Workplane("XY").cylinder(cyl_height, cyl_radius)
    
        # --- Step 2: Cut three holes PERPENDICULAR to the cylinder axis ---
        # Holes go through the cylinder in the X direction (radially).
        # Use a plane with normal=(1,0,0) at the correct Z height for each hole.
    
        # Hole 1: near top
        wp1 = cq.Workplane(
            cq.Plane(
                origin=(0, 0, z_top_hole_centered),
                xDir=(0, 1, 0),
                normal=(1, 0, 0)
            )
        )
        cutter1 = wp1.circle(hole_radius).extrude(cyl_diameter * 2, both=True)
        result = result.cut(cutter1)
    
        # Hole 2: near bottom (farther from center)
        wp2 = cq.Workplane(
            cq.Plane(
                origin=(0, 0, z_bot_hole1_centered),
                xDir=(0, 1, 0),
                normal=(1, 0, 0)
            )
        )
        cutter2 = wp2.circle(hole_radius).extrude(cyl_diameter * 2, both=True)
        result = result.cut(cutter2)
    
        # Hole 3: near bottom (closer to center)
        wp3 = cq.Workplane(
            cq.Plane(
                origin=(0, 0, z_bot_hole2_centered),
                xDir=(0, 1, 0),
                normal=(1, 0, 0)
            )
        )
        cutter3 = wp3.circle(hole_radius).extrude(cyl_diameter * 2, both=True)
        result = result.cut(cutter3)
    
        # --- Step 3: Rotate 90° around X axis to lay cylinder horizontally ---
        # Rotation 90° around X: (x,y,z) -> (x, -z, y)
        # Cylinder axis (Z) becomes Y axis after this rotation
        result = result.rotateAboutCenter((1, 0, 0), 90)
    
        # --- Step 4: Translate to final position ---
        result = result.translate((0, 0, cyl_radius))
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # After 90° rotation around X: cylinder axis now along Y
        # xlen ~ diameter, ylen ~ height, zlen ~ diameter
        expected_xlen = cyl_diameter
        expected_ylen = cyl_height
        expected_zlen = cyl_diameter
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Volume check:
        # Main cylinder volume minus 3 holes drilled perpendicular (through diameter)
        cyl_vol = math.pi * cyl_radius**2 * cyl_height
        hole_vol_each = math.pi * hole_radius**2 * cyl_diameter
        expected_vol = cyl_vol - 3 * hole_vol_each
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: main cylinder body + 3 hole cylinders = at least 4
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 4, \
            f"Expected at least 4 cylindrical faces, got {cyl_faces}"
    
        # Check single solid
        n_solids = result.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        # Check center of mass is within the bounding box
        com = cq.Shape.centerOfMass(solid)
        assert bb.xmin <= com.x <= bb.xmax, \
            f"COM x={com.x:.6f} outside bounding box [{bb.xmin:.6f}, {bb.xmax:.6f}]"
        assert bb.ymin <= com.y <= bb.ymax, \
            f"COM y={com.y:.6f} outside bounding box [{bb.ymin:.6f}, {bb.ymax:.6f}]"
        assert bb.zmin <= com.z <= bb.zmax, \
            f"COM z={com.z:.6f} outside bounding box [{bb.zmin:.6f}, {bb.zmax:.6f}]"
    
        # COM x should be near 0 (symmetric about X=0)
        assert abs(com.x) < TOL * 10, \
            f"COM x: expected ~0 (symmetric), got {com.x:.6f}"
    
        # Verify holes exist by checking that points on hole axes are outside the solid.
        # After rotation (x,y,z)->(x,-z,y) about center ~(0,0,0), then translate (0,0,cyl_radius):
        # Original hole axis center (0, 0, z_h) -> rotated (0, -z_h, 0) -> translated (0, -z_h, cyl_radius)
        # The hole is drilled in X direction, so check point at x=0 on the hole axis
    
        # Hole 1 (near top): original z = z_top_hole_centered = 0.370833
        h1_center = (0.0, -z_top_hole_centered, cyl_radius)
        assert not solid.isInside(h1_center), \
            f"Hole 1 center {h1_center} should be outside solid (hole should exist)"
    
        # Hole 2 (near bottom, farther): original z = z_bot_hole1_centered = -0.251772
        h2_center = (0.0, -z_bot_hole1_centered, cyl_radius)
        assert not solid.isInside(h2_center), \
            f"Hole 2 center {h2_center} should be outside solid (hole should exist)"
    
        # Hole 3 (near bottom, closer): original z = z_bot_hole2_centered = -0.31101
        h3_center = (0.0, -z_bot_hole2_centered, cyl_radius)
        assert not solid.isInside(h3_center), \
            f"Hole 3 center {h3_center} should be outside solid (hole should exist)"
    
        # Verify solid material exists between holes (a point on the cylinder axis mid-height)
        # Mid-height in original frame: (0, 0, 0) -> rotated (0, 0, 0) -> translated (0, 0, cyl_radius)
        mid_point = (0.0, 0.0, cyl_radius)
        assert solid.isInside(mid_point), \
            f"Mid-cylinder point {mid_point} should be inside solid"
    
        print(f"Bounding box: x={bb.xlen:.6f}, y={bb.ylen:.6f}, z={bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Cylindrical faces: {cyl_faces}")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00521230/gpt_generated.stl')
