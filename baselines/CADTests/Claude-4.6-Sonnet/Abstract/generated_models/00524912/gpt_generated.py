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
        # Door (larger rectangle) in X-Y plane
        door_length = 40.0   # X direction
        door_width  = 20.0   # Y direction
        door_thick  = 2.0    # Z extrusion (thickness)
    
        # Hinge (smaller rectangle) in Y-Z plane
        # Approximately half the length and width of the door
        hinge_width  = door_width  / 2.0   # Y direction = 10
        hinge_height = door_length / 2.0   # Z direction = 20  (half of door_length)
        # Extruded almost twice as much as door thickness
        hinge_thick  = door_thick * 1.9    # X extrusion = 3.8
    
        # --- Step 1: Create the door (larger rectangle) in X-Y plane ---
        # Box centered at origin: x[-20,20], y[-10,10], z[-1,1]
        door = cq.Workplane("XY").box(door_length, door_width, door_thick)
    
        # --- Step 2: Create the hinge (smaller rectangle) in Y-Z plane ---
        # The hinge face lies in the Y-Z plane, extruded in X direction.
        # Centered at origin: x[-1.9,1.9], y[-10,10], z[-10,10]
        # This makes the hinge perpendicular to the door (door is flat in XY, hinge stands in YZ)
        # They share an edge/region along the Y axis where z=1 (top of door) and x in [-1.9,1.9]
        hinge = cq.Workplane("YZ").box(hinge_width, hinge_height, hinge_thick)
    
        # --- Step 3: Union door and hinge ---
        # Both centered at origin; they intersect/connect along shared edges
        result = door.union(hinge)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        # X: door dominates → 40, but hinge adds ±1.9 in X which is within door's ±20
        assert abs(bb.xlen - door_length) < TOL, \
            f"X bounding box: expected {door_length}, got {bb.xlen}"
    
        # Y: door is 20, hinge is 10 (half) → door dominates at 20
        assert abs(bb.ylen - door_width) < TOL, \
            f"Y bounding box: expected {door_width}, got {bb.ylen}"
    
        # Z: door is 2 (z:-1 to 1), hinge is 20 (z:-10 to 10) → hinge dominates at 20
        assert abs(bb.zlen - hinge_height) < TOL, \
            f"Z bounding box: expected {hinge_height}, got {bb.zlen}"
    
        # Volume check: door_vol + hinge_vol - intersection_vol
        # Intersection is where both overlap: x[-1.9,1.9] × y[-10,10] × z[-1,1]
        door_vol  = door_length * door_width * door_thick          # 40*20*2 = 1600
        hinge_vol = hinge_thick * hinge_width * hinge_height       # 3.8*10*20 = 760
        inter_vol = hinge_thick * hinge_width * door_thick         # 3.8*10*2 = 76
        expected_vol = door_vol + hinge_vol - inter_vol            # 1600+760-76 = 2284
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The result should be a single solid (union)
        assert result.solids().size() == 1, \
            f"Expected 1 solid after union, got {result.solids().size()}"
    
        # Center of mass should be near origin (symmetric in X and Y)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
        # Z center: door contributes z=0, hinge contributes z=0 → combined ~0
        assert abs(com.z) < TOL, f"Center of mass Z should be ~0, got {com.z}"
    
        # Verify hinge is roughly twice the thickness of door
        assert hinge_thick / door_thick > 1.8, \
            f"Hinge thickness should be ~2x door thickness: hinge={hinge_thick}, door={door_thick}"
    
        # Verify hinge dimensions are ~half of door
        assert abs(hinge_width  - door_width  / 2) < TOL, \
            f"Hinge width should be half door width: {hinge_width} vs {door_width/2}"
        assert abs(hinge_height - door_length / 2) < TOL, \
            f"Hinge height should be half door length: {hinge_height} vs {door_length/2}"
    
        # Verify perpendicularity: door has planar faces with normals in Z,
        # hinge has planar faces with normals in X — both present in union
        # Check faces with normals in +Z/-Z (door top/bottom)
        z_faces = result.faces("|Z").size()
        assert z_faces >= 2, f"Expected at least 2 faces parallel to XY (door faces), got {z_faces}"
    
        # Check faces with normals in +X/-X (hinge faces)
        x_faces = result.faces("|X").size()
        assert x_faces >= 2, f"Expected at least 2 faces parallel to YZ (hinge faces), got {x_faces}"
    
        print(f"Door: {door_length}x{door_width}x{door_thick} mm")
        print(f"Hinge: {hinge_thick}x{hinge_width}x{hinge_height} mm (YZ plane, extruded in X)")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00524912/gpt_generated.stl')
