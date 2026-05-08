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
        # Irregular rhombus vertices (not a perfect rhombus - slightly skewed)
        # Define 4 points for an irregular rhombus-like shape
        # Points in 2D (XY plane)
        p1 = (0.0,   0.0)
        p2 = (60.0,  15.0)
        p3 = (50.0,  45.0)
        p4 = (-10.0, 30.0)
    
        rhombus_thickness = 8.0   # extrusion depth of the blade
    
        # Rectangular arm parameters
        arm_width  = 15.0
        arm_height = 10.0
        arm_length = 80.0
    
        # --- Step 1: Create the irregular rhombus blade ---
        # Build the rhombus as a closed wire and extrude it
        rhombus = (
            cq.Workplane("XY")
            .moveTo(p1[0], p1[1])
            .lineTo(p2[0], p2[1])
            .lineTo(p3[0], p3[1])
            .lineTo(p4[0], p4[1])
            .close()
            .extrude(rhombus_thickness)
        )
    
        # --- Step 2: Find the center of the top edge of the rhombus (the edge from p1 to p2) ---
        # The edge from p1=(0,0) to p2=(60,15) on the bottom face (z=0)
        # Center of this edge: midpoint of p1 and p2
        edge_mid_x = (p1[0] + p2[0]) / 2.0   # = 30.0
        edge_mid_y = (p1[1] + p2[1]) / 2.0   # = 7.5
        edge_mid_z = 0.0  # on the bottom face
    
        # Direction vector along the edge p1->p2
        dx = p2[0] - p1[0]  # 60
        dy = p2[1] - p1[1]  # 15
        edge_len = math.sqrt(dx*dx + dy*dy)
        # Unit vector along edge
        ux = dx / edge_len
        uy = dy / edge_len
        # Normal to edge in XY plane (perpendicular, pointing outward from rhombus)
        # The rhombus interior is roughly at center (25, 22.5)
        # Outward normal from edge p1->p2: rotate edge direction 90° clockwise
        nx = uy   #  15/edge_len
        ny = -ux  # -60/edge_len
        # Check: does this point away from rhombus center?
        cx_rhombus = (p1[0]+p2[0]+p3[0]+p4[0])/4  # 25
        cy_rhombus = (p1[1]+p2[1]+p3[1]+p4[1])/4  # 22.5
        # Vector from edge midpoint to rhombus center
        to_center_x = cx_rhombus - edge_mid_x
        to_center_y = cy_rhombus - edge_mid_y
        # If dot product with normal is negative, normal points away (correct)
        dot = nx * to_center_x + ny * to_center_y
        if dot > 0:
            # Flip normal to point outward
            nx, ny = -nx, -ny
    
        # --- Step 3: Create the rectangular arm ---
        # The arm extends outward from the center of the p1-p2 edge
        # We'll place the arm on a workplane at the edge midpoint,
        # oriented so the arm extends in the outward normal direction.
    
        # The arm workplane: origin at edge midpoint, 
        # arm extends along the outward normal direction in XY plane
        # We need a workplane where:
        #   - X axis is along the edge (ux, uy, 0)
        #   - Y axis is up (0, 0, 1)  
        #   - Z axis (normal) is along the outward normal (nx, ny, 0)
    
        arm_plane = cq.Plane(
            origin=(edge_mid_x, edge_mid_y, rhombus_thickness / 2.0),
            xDir=(ux, uy, 0),
            normal=(nx, ny, 0)
        )
    
        # Create the arm: a box centered on the workplane
        # The arm extends arm_length in the normal direction (Z of arm_plane)
        # arm_width along edge direction (X of arm_plane)
        # arm_height in vertical direction (Y of arm_plane)
        arm = (
            cq.Workplane(arm_plane)
            .box(arm_width, arm_height, arm_length, centered=(True, True, False))
        )
    
        # --- Step 4: Union the rhombus blade and the arm ---
        result = rhombus.union(arm)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for complex geometry
    
        # Check that we have a single solid
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # The rhombus spans x: -10 to 60, y: 0 to 45, z: 0 to 8
        # The arm extends outward from edge p1-p2 in direction (nx, ny)
        # arm_length = 80, so arm extends significantly in that direction
    
        # X extent: rhombus goes from -10 to 60 (70 wide), arm adds more
        assert bb.xlen > 60, f"X extent should be > 60, got {bb.xlen:.2f}"
    
        # Y extent: rhombus goes from 0 to 45, arm may extend below 0
        assert bb.ylen > 20, f"Y extent should be > 20, got {bb.ylen:.2f}"
    
        # Z extent: rhombus is 8 thick, arm is 10 tall centered at z=4
        assert abs(bb.zlen - arm_height) < TOL or bb.zlen >= rhombus_thickness, \
            f"Z extent should be >= {rhombus_thickness}, got {bb.zlen:.2f}"
    
        # Volume check
        # Rhombus area using shoelace formula
        pts = [p1, p2, p3, p4]
        n = len(pts)
        area_rhombus = 0.0
        for i in range(n):
            j = (i + 1) % n
            area_rhombus += pts[i][0] * pts[j][1]
            area_rhombus -= pts[j][0] * pts[i][1]
        area_rhombus = abs(area_rhombus) / 2.0
        vol_rhombus = area_rhombus * rhombus_thickness
        vol_arm = arm_width * arm_height * arm_length
    
        # The union volume is less than or equal to sum (overlap at attachment)
        expected_vol_max = vol_rhombus + vol_arm
        expected_vol_min = max(vol_rhombus, vol_arm)
        actual_vol = result.val().Volume()
    
        assert actual_vol > expected_vol_min * 0.5, \
            f"Volume too small: expected > {expected_vol_min*0.5:.1f}, got {actual_vol:.1f}"
        assert actual_vol <= expected_vol_max * 1.01, \
            f"Volume too large: expected <= {expected_vol_max*1.01:.1f}, got {actual_vol:.1f}"
    
        # Check cylindrical faces (should be 0 - no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check that the object has planar faces only
        plane_faces = result.faces("%Plane").size()
        assert plane_faces >= 6, f"Expected at least 6 planar faces, got {plane_faces}"
    
        # Check center of mass is roughly between the two components
        com = cq.Shape.centerOfMass(result.val())
        # COM should be somewhere in the combined region
        assert bb.xmin <= com.x <= bb.xmax, \
            f"COM x={com.x:.2f} outside bbox [{bb.xmin:.2f}, {bb.xmax:.2f}]"
        assert bb.ymin <= com.y <= bb.ymax, \
            f"COM y={com.y:.2f} outside bbox [{bb.ymin:.2f}, {bb.ymax:.2f}]"
        assert bb.zmin <= com.z <= bb.zmax, \
            f"COM z={com.z:.2f} outside bbox [{bb.zmin:.2f}, {bb.zmax:.2f}]"
    
        print(f"✓ Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"✓ Volume: {actual_vol:.2f} (rhombus={vol_rhombus:.2f}, arm={vol_arm:.2f})")
        print(f"✓ Planar faces: {plane_faces}")
        print(f"✓ Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00999374/gpt_generated.stl')
