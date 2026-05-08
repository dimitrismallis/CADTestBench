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
        # Hexagon 1 (base): circumradius=20, extrude=4
        # Hexagon 2: circumradius=14, extrude=3, rotated 30° from hex1
        # Hexagon 3: circumradius=9, extrude=2, rotated 15° from hex2 (so 45° total from hex1)
        # Triangle: circumradius=5, extrude=1, rotated 20° from hex3
    
        hex1_r = 20
        hex1_h = 4
    
        hex2_r = 14
        hex2_h = 3
        hex2_rot = 30  # degrees rotation relative to hex1
    
        hex3_r = 9
        hex3_h = 2
        hex3_rot = 15  # degrees rotation relative to hex2 (cumulative: 45° from hex1)
    
        tri_r = 5
        tri_h = 1
        tri_rot = 20  # degrees rotation relative to hex3
    
        # --- Step 1: Base hexagon (hex1) ---
        # polygon(nSides, diameter) where diameter = 2 * circumradius
        hex1 = (
            cq.Workplane("XY")
            .polygon(6, 2 * hex1_r)
            .extrude(hex1_h)
        )
    
        # --- Step 2: Second hexagon on top of hex1, rotated 30° ---
        z2 = hex1_h  # starts at top of hex1
        hex2 = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, z2), rotate=cq.Vector(0, 0, hex2_rot))
            .polygon(6, 2 * hex2_r)
            .extrude(hex2_h)
        )
    
        # --- Step 3: Third hexagon on top of hex2, rotated further ---
        z3 = z2 + hex2_h  # starts at top of hex2
        hex3 = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, z3), rotate=cq.Vector(0, 0, hex2_rot + hex3_rot))
            .polygon(6, 2 * hex3_r)
            .extrude(hex3_h)
        )
    
        # --- Step 4: Triangle on top of hex3, rotated so vertices don't align ---
        z4 = z3 + hex3_h  # starts at top of hex3
        tri = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, z4), rotate=cq.Vector(0, 0, hex2_rot + hex3_rot + tri_rot))
            .polygon(3, 2 * tri_r)
            .extrude(tri_h)
        )
    
        # --- Step 5: Union all parts ---
        result = hex1.union(hex2).union(hex3).union(tri)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Total height should be hex1_h + hex2_h + hex3_h + tri_h = 4+3+2+1 = 10
        total_height = hex1_h + hex2_h + hex3_h + tri_h
        assert abs(bb.zlen - total_height) < TOL, \
            f"Total height: expected {total_height}, got {bb.zlen}"
    
        # Z min should be 0 (base on XY plane)
        assert abs(bb.zmin) < TOL, \
            f"Z min: expected 0, got {bb.zmin}"
    
        # Z max should be total_height
        assert abs(bb.zmax - total_height) < TOL, \
            f"Z max: expected {total_height}, got {bb.zmax}"
    
        # The widest part is hex1 (base).
        # For polygon(6, diameter) with default orientation (first vertex at 0° = +X direction):
        # - Vertices at angles 0°, 60°, 120°, 180°, 240°, 300°
        # - xlen = 2 * R (vertex at 0° and 180°)
        # - ylen = 2 * R * sin(60°) = R * sqrt(3)  (vertices at 60°, 120°, 240°, 300°)
        expected_xlen = 2 * hex1_r          # = 40
        expected_ylen = hex1_r * math.sqrt(3)  # = 20*sqrt(3) ≈ 34.64
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X extent: expected ~{expected_xlen:.3f}, got {bb.xlen:.3f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y extent: expected ~{expected_ylen:.3f}, got {bb.ylen:.3f}"
    
        # Volume check: sum of individual volumes
        # Regular hexagon area with circumradius r: A = (3*sqrt(3)/2) * r^2
        def hex_area(r):
            return (3 * math.sqrt(3) / 2) * r ** 2
    
        # Equilateral triangle area with circumradius r: side = r*sqrt(3), A = (sqrt(3)/4)*side^2
        def tri_area(r):
            side = r * math.sqrt(3)
            return (math.sqrt(3) / 4) * side ** 2
    
        vol_hex1 = hex_area(hex1_r) * hex1_h
        vol_hex2 = hex_area(hex2_r) * hex2_h
        vol_hex3 = hex_area(hex3_r) * hex3_h
        vol_tri  = tri_area(tri_r)  * tri_h
    
        expected_vol = vol_hex1 + vol_hex2 + vol_hex3 + vol_tri
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Check that the model has exactly 1 solid (all unioned)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Check that the bottom face is at z=0 (hex1 base)
        bottom_faces = result.faces("<Z")
        assert bottom_faces.size() >= 1, "Should have at least one bottom face"
        bottom_z = bottom_faces.val().Center().z
        assert abs(bottom_z) < TOL, \
            f"Bottom face center Z: expected ~0, got {bottom_z}"
    
        # Check that the top face is at z=total_height (triangle top)
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "Should have at least one top face"
        top_z = top_faces.val().Center().z
        assert abs(top_z - total_height) < TOL, \
            f"Top face center Z: expected ~{total_height}, got {top_z}"
    
        # Verify center of mass is roughly at x=0, y=0 (symmetric about Z axis)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
    
        # Verify the model has planar faces (top and bottom of each layer)
        planar_faces = result.faces("%Plane")
        assert planar_faces.size() >= 8, \
            f"Expected at least 8 planar faces (top+bottom of 4 shapes), got {planar_faces.size()}"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (expected ~{expected_vol:.2f})")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00853706/gpt_generated.stl')
