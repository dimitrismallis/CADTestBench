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
        block_length = 0.990099
        block_width  = 0.415842
        block_height = 0.990099
    
        hole_diameter  = 0.471867
        hole_radius    = hole_diameter / 2.0   # 0.2359335
    
        pipe_outer_diameter = 0.517113
        pipe_outer_radius   = pipe_outer_diameter / 2.0  # 0.2585565
        pipe_inner_radius   = hole_radius                # same as hole
        pipe_height         = 0.334158
    
        translation = (0, -0.207921, 0.025308)
    
        # --- Step 1: Create the square block ---
        block = (
            cq.Workplane("XY")
            .box(block_length, block_width, block_height)
        )
    
        # --- Step 2: Create circular hole through the block from the top ---
        block_with_hole = (
            block
            .faces(">Z")
            .workplane()
            .circle(hole_radius)
            .cutThruAll()
        )
    
        # --- Step 3 & 4: Sketch annulus on top surface and extrude upward ---
        result = (
            block_with_hole
            .faces(">Z")
            .workplane()
            .circle(pipe_outer_radius)
            .circle(pipe_inner_radius)
            .extrude(pipe_height, combine=True)
        )
    
        # --- Step 5: Translate the entire assembly ---
        result = result.translate(translation)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # The pipe outer diameter (0.517113) is larger than the block width (0.415842),
        # so the bounding box Y is determined by the pipe outer diameter.
        # The pipe outer diameter (0.517113) < block_length (0.990099), so X is block_length.
        expected_xlen = block_length                              # 0.990099 (block dominates X)
        expected_ylen = pipe_outer_diameter                       # 0.517113 (pipe dominates Y)
        expected_zlen = block_height + pipe_height                # 1.324257
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Check translation: center of bounding box
        # Original bounding box before translation:
        # X: -block_length/2 to +block_length/2  => cx = 0
        # Y: -pipe_outer_radius to +pipe_outer_radius => cy = 0
        # Z: -block_height/2 to +block_height/2 + pipe_height
        #    => cz = pipe_height/2
        orig_cx = 0.0
        orig_cy = 0.0
        orig_cz = pipe_height / 2.0
    
        expected_cx = orig_cx + translation[0]
        expected_cy = orig_cy + translation[1]
        expected_cz = orig_cz + translation[2]
    
        cob = solid.CenterOfBoundBox()
        assert abs(cob.x - expected_cx) < TOL, \
            f"Center X: expected {expected_cx:.6f}, got {cob.x:.6f}"
        assert abs(cob.y - expected_cy) < TOL, \
            f"Center Y: expected {expected_cy:.6f}, got {cob.y:.6f}"
        assert abs(cob.z - expected_cz) < TOL, \
            f"Center Z: expected {expected_cz:.6f}, got {cob.z:.6f}"
    
        # Volume check:
        # The hole cylinder (radius = hole_radius = 0.2359335) extends beyond the block
        # in Y (block half-width = 0.207921 < hole_radius). So the actual removed volume
        # is the intersection of the cylinder with the block, not the full cylinder.
        #
        # Intersection area of circle (radius r) with rectangle (half-width w in Y):
        # Since r < block_half_length (circle fits in X), and r > w (extends beyond in Y):
        # Area = 2*w*sqrt(r^2 - w^2) + 2*r^2*arcsin(w/r)
        r = hole_radius
        w = block_width / 2.0
        L = block_length / 2.0
        # r < L check: 0.2359335 < 0.495050 ✓
        # r > w check: 0.2359335 > 0.207921 ✓
        intersection_area = 2 * w * math.sqrt(r**2 - w**2) + 2 * r**2 * math.asin(w / r)
        hole_vol_actual = intersection_area * block_height
    
        block_vol = block_length * block_width * block_height
        pipe_vol  = math.pi * (pipe_outer_radius**2 - pipe_inner_radius**2) * pipe_height
        expected_vol = block_vol - hole_vol_actual + pipe_vol
    
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check cylindrical faces exist (hole inner wall + pipe inner wall + pipe outer wall)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 2, \
            f"Expected at least 2 cylindrical faces, got {cyl_faces}"
    
        # Check that a point inside the hole is NOT inside the solid
        # Hole center at z=0 (middle of block height), x=0, y=0 (before translation)
        hole_check_point = (
            translation[0],
            translation[1],
            translation[2]  # z=0 of original block center maps to translation[2]
        )
        assert not solid.isInside(hole_check_point), \
            f"Point {hole_check_point} should be inside the hole (not solid), but isInside returned True"
    
        # Check that a point inside the block material is inside the solid
        # Near the edge of the block in X, away from the hole
        material_point = (
            translation[0] + block_length/2 - 0.05,
            translation[1],
            translation[2]
        )
        assert solid.isInside(material_point), \
            f"Point {material_point} should be inside the block material, but isInside returned False"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Cylindrical faces: {cyl_faces}")
        print(f"  Intersection area: {intersection_area:.6f} (full circle: {math.pi * r**2:.6f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681399/gpt_generated.stl')
