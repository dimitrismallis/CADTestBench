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
        length = 1.16102   # X direction
        width  = 0.0729    # Y direction
        height = 1.5       # Z direction
        hole_d = 0.072899  # hole diameter
        hole_r = hole_d / 2.0
    
        # Plate is centered at origin:
        # X: [-length/2, +length/2] = [-0.58051, +0.58051]
        # Y: [-width/2,  +width/2]  = [-0.03645, +0.03645]
        # Z: [-height/2, +height/2] = [-0.75,    +0.75   ]
    
        left_from_left   = 0.252909   # left hole center from left edge
        right_from_right = 0.127776   # right hole center from right edge
        from_top         = 0.595655   # both holes from top
    
        # Compute hole centers in global coords
        x_left  = -length/2 + left_from_left    # -0.58051 + 0.252909 = -0.327601
        x_right = +length/2 - right_from_right  # +0.58051 - 0.127776 = +0.452734
        z_hole  = +height/2 - from_top          # +0.75 - 0.595655 = +0.154345
    
        # --- Step 1: Create the base rectangular plate ---
        result = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Determine the local X direction on the >Y face workplane ---
        # On the >Y face (normal = +Y), CadQuery sets local X = -global X (right-hand rule).
        # So to place a hole at global X = x_left, we use local X = -x_left.
        # Similarly for x_right: local X = -x_right.
        # Local Y on this workplane = global Z (unchanged).
    
        # --- Step 3: Cut both holes using pushPoints on the >Y face workplane ---
        result = (
            result
            .faces(">Y").workplane()
            .pushPoints([(-x_left, z_hole), (-x_right, z_hole)])
            .circle(hole_r)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-3
    
        # Bounding box check
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, \
            f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, \
            f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, \
            f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume check: box minus two cylindrical holes
        box_vol      = length * width * height
        hole_vol     = 2 * math.pi * hole_r**2 * width
        expected_vol = box_vol - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces: 2 holes → 2 cylindrical faces
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, \
            f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Check hole positions via circular edges
        circ_edges = result.edges("%Circle").vals()
        assert len(circ_edges) == 4, \
            f"Circular edges: expected 4 (2 holes × 2 entry/exit), got {len(circ_edges)}"
    
        # Get centers of circular edges and verify X positions
        circ_centers_x = sorted([e.Center().x for e in circ_edges])
        # Should have 2 at x_left and 2 at x_right
        assert abs(circ_centers_x[0] - x_left)  < TOL, \
            f"Left hole X [0]: expected {x_left:.6f}, got {circ_centers_x[0]:.6f}"
        assert abs(circ_centers_x[1] - x_left)  < TOL, \
            f"Left hole X [1]: expected {x_left:.6f}, got {circ_centers_x[1]:.6f}"
        assert abs(circ_centers_x[2] - x_right) < TOL, \
            f"Right hole X [2]: expected {x_right:.6f}, got {circ_centers_x[2]:.6f}"
        assert abs(circ_centers_x[3] - x_right) < TOL, \
            f"Right hole X [3]: expected {x_right:.6f}, got {circ_centers_x[3]:.6f}"
    
        # Verify Z positions of circular edges
        circ_centers_z = [e.Center().z for e in circ_edges]
        for z in circ_centers_z:
            assert abs(z - z_hole) < TOL, \
                f"Hole Z: expected {z_hole:.6f}, got {z:.6f}"
    
        # Verify hole radii via circular edge bounding boxes
        for e in circ_edges:
            e_bb = e.BoundingBox()
            r_measured = max(e_bb.xlen, e_bb.zlen) / 2.0
            assert abs(r_measured - hole_r) < TOL, \
                f"Hole radius: expected {hole_r:.6f}, got {r_measured:.6f}"
    
        # Verify holes are through-holes: ray along Y through each hole center
        # should intersect exactly 2 faces (entry + exit of the cylindrical hole)
        solid = result.val()
    
        left_faces = solid.facesIntersectedByLine(
            (x_left, -width, z_hole), (0, 1, 0), direction="AlongAxis"
        )
        assert len(left_faces) == 2, \
            f"Left hole: ray along Y should intersect 2 faces, got {len(left_faces)}"
    
        right_faces = solid.facesIntersectedByLine(
            (x_right, -width, z_hole), (0, 1, 0), direction="AlongAxis"
        )
        assert len(right_faces) == 2, \
            f"Right hole: ray along Y should intersect 2 faces, got {len(right_faces)}"
    
        # A ray through the solid body (not a hole) should intersect 2 faces
        body_faces = solid.facesIntersectedByLine(
            (0, -width, 0), (0, 1, 0), direction="AlongAxis"
        )
        assert len(body_faces) == 2, \
            f"Body: ray along Y through solid should intersect 2 faces, got {len(body_faces)}"
    
        print("All assertions passed!")
        print(f"  Box: {length} x {width} x {height}")
        print(f"  Left hole X:  {x_left:.6f}")
        print(f"  Right hole X: {x_right:.6f}")
        print(f"  Holes Z:      {z_hole:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00033093/gpt_generated.stl')
