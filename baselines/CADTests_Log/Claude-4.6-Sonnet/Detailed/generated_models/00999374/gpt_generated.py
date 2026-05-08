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
        # --- Step 1: Define rhombus vertices ---
        P0 = (-0.215997, -0.071707)
        P1 = (0.283196/2 - 0.086266, -0.571139/2 + 0.128415)
        P2 = (0.283196/2 + 0.154673, 0.571139/2 - 0.103869)
        P3 = (0.283196/3 - 0.094331, 0.571139 - 0.45031)
    
        # --- Step 2: Create the rhombus sketch and extrude ---
        extrude_height = 0.493701
    
        rhombus = (
            cq.Workplane("XY")
            .moveTo(P0[0], P0[1])
            .lineTo(P1[0], P1[1])
            .lineTo(P2[0], P2[1])
            .lineTo(P3[0], P3[1])
            .close()
            .extrude(extrude_height)
        )
    
        # --- Step 3: Create the rectangular prism (arm) ---
        arm_l = 0.1323
        arm_w = 0.78659
        arm_h = 0.203642
    
        arm = (
            cq.Workplane("XY")
            .box(arm_l, arm_w, arm_h)
        )
    
        # --- Step 4: Rotate arm by -41.7 degrees around Z-axis ---
        arm = arm.rotate((0, 0, 0), (0, 0, 1), -41.7)
    
        # --- Step 5: Translate arm to (0.223543, -0.361526, 0.301748) ---
        arm = arm.translate((0.223543, -0.361526, 0.301748))
    
        # --- Step 6: Union the two shapes ---
        rhombus_solid = rhombus.val()
        arm_solid = arm.val()
    
        combined_solid = rhombus_solid.fuse(arm_solid)
    
        result = cq.Workplane("XY").add(combined_solid)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Check that we have a valid solid with positive volume
        vol = result.val().Volume()
        assert vol > 0, f"Volume should be positive, got {vol}"
    
        # Compute expected volumes
        # Rhombus area via shoelace formula
        pts = [P0, P1, P2, P3]
        n = len(pts)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += pts[i][0] * pts[j][1]
            area -= pts[j][0] * pts[i][1]
        rhombus_area = abs(area) / 2.0
        rhombus_vol = rhombus_area * extrude_height
        arm_vol = arm_l * arm_w * arm_h
    
        # Combined volume must be <= sum of parts (no volume created by union)
        assert vol <= rhombus_vol + arm_vol + TOL, \
            f"Combined volume {vol:.6f} exceeds sum of parts {rhombus_vol + arm_vol:.6f}"
        # Combined volume must be >= the larger individual part
        assert vol >= max(rhombus_vol, arm_vol) - TOL, \
            f"Combined volume {vol:.6f} is less than largest part {max(rhombus_vol, arm_vol):.6f}"
    
        print(f"Rhombus area: {rhombus_area:.6f}")
        print(f"Rhombus volume: {rhombus_vol:.6f}")
        print(f"Arm volume: {arm_vol:.6f}")
        print(f"Combined volume: {vol:.6f}")
    
        # Check bounding box
        bb = result.val().BoundingBox()
        print(f"Bounding box: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], "
              f"y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
    
        # Rhombus leftmost point is P0 x = -0.215997
        assert bb.xmin < -0.1, f"BBox xmin should be < -0.1 (rhombus left edge), got {bb.xmin}"
    
        # Z should start at 0 (base of rhombus on XY plane)
        assert bb.zmin < TOL, f"BBox zmin should be ~0, got {bb.zmin}"
    
        # Z should reach the extrude height (top of rhombus body)
        assert abs(bb.zmax - extrude_height) < TOL, \
            f"BBox zmax should be ~{extrude_height}, got {bb.zmax}"
    
        # The arm center is at z=0.301748, half-height=0.101821
        # arm z range: [0.199927, 0.403569] — fully inside rhombus z range [0, 0.493701]
        arm_z_center = 0.301748
        arm_z_half = arm_h / 2.0
        arm_z_min = arm_z_center - arm_z_half
        arm_z_max = arm_z_center + arm_z_half
        assert arm_z_min > 0, f"Arm bottom z={arm_z_min:.4f} should be above 0"
        assert arm_z_max < extrude_height, \
            f"Arm top z={arm_z_max:.4f} should be below extrude height {extrude_height}"
    
        # Y extent: arm is translated to y=-0.361526, rotated -41.7 deg
        # arm half-diagonal in XY ~ sqrt((arm_l/2)^2 + (arm_w/2)^2) ~ 0.399
        # so ymin should be well below 0
        assert bb.ymin < -0.2, f"BBox ymin should be < -0.2, got {bb.ymin}"
    
        # Face count: rhombus prism (6 faces) + arm box (6 faces), fused → expect >= 6
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count >= 6, f"Should have at least 6 faces, got {face_count}"
    
        # Check center of mass is within bounding box
        com = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        assert bb.xmin <= com.x <= bb.xmax, \
            f"COM x={com.x:.4f} outside bbox x=[{bb.xmin:.4f}, {bb.xmax:.4f}]"
        assert bb.ymin <= com.y <= bb.ymax, \
            f"COM y={com.y:.4f} outside bbox y=[{bb.ymin:.4f}, {bb.ymax:.4f}]"
        assert bb.zmin <= com.z <= bb.zmax, \
            f"COM z={com.z:.4f} outside bbox z=[{bb.zmin:.4f}, {bb.zmax:.4f}]"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00999374/gpt_generated.stl')
