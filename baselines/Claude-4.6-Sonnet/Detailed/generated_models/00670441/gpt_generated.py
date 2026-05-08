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
        side_length = 1.00328
        height = 0.271665
        rot_z = 22.4       # degrees around Z
        rot_x = -90.0      # degrees around X
        tx, ty, tz = -0.176576, 0.0, 0.286546
    
        # --- Step 1: Compute circumradius for regular octagon ---
        # For a regular n-gon with side s: R = s / (2 * sin(pi/n))
        n = 8
        R = side_length / (2 * math.sin(math.pi / n))
        diameter = 2 * R  # CadQuery polygon uses circumscribed circle diameter
    
        # --- Step 2: Create regular octagon and extrude ---
        result = (
            cq.Workplane("XY")
            .polygon(n, diameter)
            .extrude(height)
        )
    
        # --- Step 3: Rotate 22.4 degrees around Z-axis ---
        # rotate(axisStartPoint, axisEndPoint, angleDegrees)
        result = result.rotate((0, 0, 0), (0, 0, 1), rot_z)
    
        # --- Step 4: Rotate -90 degrees around X-axis ---
        result = result.rotate((0, 0, 0), (1, 0, 0), rot_x)
    
        # --- Step 5: Translate to (-0.176576, 0, 0.286546) ---
        result = result.translate((tx, ty, tz))
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
    
        # Check volume: volume of octagon prism = area_octagon * height
        # Area of regular octagon with side s: A = 2*(1+sqrt(2))*s^2
        area_octagon = 2 * (1 + math.sqrt(2)) * side_length**2
        expected_volume = area_octagon * height
        actual_volume = solid.Volume()
        assert abs(actual_volume - expected_volume) / expected_volume < 0.01, \
            f"Volume: expected ~{expected_volume:.6f}, got {actual_volume:.6f}"
    
        # Check center of mass position
        # Original octagon prism center is at (0, 0, height/2)
        # After Z rotation: still at (0, 0, height/2) since it's on Z axis
        # After X rotation by -90 deg: (x,y,z) -> (x, z, -y)
        # So (0, 0, height/2) -> (0, height/2, 0)
        # After translation: (0 + tx, height/2 + ty, 0 + tz)
        cx_expected = 0 + tx
        cy_expected = height / 2 + ty
        cz_expected = 0 + tz
    
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x - cx_expected) < TOL, \
            f"Center X: expected {cx_expected:.6f}, got {com.x:.6f}"
        assert abs(com.y - cy_expected) < TOL, \
            f"Center Y: expected {cy_expected:.6f}, got {com.y:.6f}"
        assert abs(com.z - cz_expected) < TOL, \
            f"Center Z: expected {cz_expected:.6f}, got {com.z:.6f}"
    
        # Check face count: octagon prism has 8 rectangular side faces + 2 octagonal end faces = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check that the solid has exactly 1 solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check bounding box: after -90 deg X rotation, the height (Z) becomes Y extent
        # The octagon's XY extent stays roughly the same
        # After rotation: xlen ~ octagon_diameter, ylen ~ height, zlen ~ octagon_diameter
        bb = solid.BoundingBox()
        # The octagon diameter (circumscribed) = 2*R
        # After Z rotation by 22.4 deg, the bounding box of the octagon changes slightly
        # but should be close to 2*R in both X and Y
        # After X rotation by -90, Y and Z swap (with sign change on one)
        # So: xlen ~ octagon_bb_x, ylen ~ octagon_height = 0.271665, zlen ~ octagon_bb_y
        assert abs(bb.ylen - height) < TOL, \
            f"BBox Y (height after rotation): expected {height:.6f}, got {bb.ylen:.6f}"
    
        print(f"Volume: {actual_volume:.6f} (expected {expected_volume:.6f})")
        print(f"Center of mass: ({com.x:.6f}, {com.y:.6f}, {com.z:.6f})")
        print(f"Bounding box: x={bb.xlen:.6f}, y={bb.ylen:.6f}, z={bb.zlen:.6f}")
        print(f"Face count: {face_count}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670441/gpt_generated.stl')
