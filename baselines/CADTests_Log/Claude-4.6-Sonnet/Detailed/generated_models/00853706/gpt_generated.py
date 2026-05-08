import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # Parameters
        # Hexagon 1 (base)
        hex1_side = 1.15342
        hex1_h    = 0.249723
        hex1_rot  = 0.0  # degrees
    
        # Hexagon 2
        hex2_side = 0.865066
        hex2_h    = 0.199778
        hex2_rot  = 30.0  # rotated 30° so vertices don't align with hex1
    
        # Hexagon 3
        hex3_side = 0.576711
        hex3_h    = 0.099889
        hex3_rot  = 15.0  # rotated 15° so vertices don't align with hex2
    
        # Triangle (3-sided polygon)
        tri_r     = 0.228054  # circumradius
        tri_h     = 0.079911
        tri_rot   = 10.0  # rotated 10° so vertices don't align with hex3
    
        # Z positions (cumulative)
        z0 = 0.0
        z1 = hex1_h                          # 0.249723
        z2 = z1 + hex2_h                     # 0.449501
        z3 = z2 + hex3_h                     # 0.549390
    
        # For CadQuery polygon(): nSides, diameter
        # For a regular hexagon, side length = circumradius, so diameter = 2 * side_length
        # For a regular polygon with n sides, circumradius R = side / (2 * sin(pi/n))
        # For hexagon: R = side (since sin(pi/6) = 0.5, so R = side/(2*0.5) = side)
        # For triangle: R = tri_r, diameter = 2 * tri_r
    
        hex1_diam = 2.0 * hex1_side
        hex2_diam = 2.0 * hex2_side
        hex3_diam = 2.0 * hex3_side
        tri_diam  = 2.0 * tri_r
    
        # --- Step 1: Base hexagon ---
        hex1 = (
            cq.Workplane("XY")
            .transformed(rotate=cq.Vector(0, 0, hex1_rot))
            .polygon(6, hex1_diam)
            .extrude(hex1_h)
        )
    
        # --- Step 2: Second hexagon on top of first ---
        hex2 = (
            cq.Workplane("XY", origin=(0, 0, z1))
            .transformed(rotate=cq.Vector(0, 0, hex2_rot))
            .polygon(6, hex2_diam)
            .extrude(hex2_h)
        )
    
        # --- Step 3: Third hexagon on top of second ---
        hex3 = (
            cq.Workplane("XY", origin=(0, 0, z2))
            .transformed(rotate=cq.Vector(0, 0, hex3_rot))
            .polygon(6, hex3_diam)
            .extrude(hex3_h)
        )
    
        # --- Step 4: Triangle on top of third hexagon ---
        tri = (
            cq.Workplane("XY", origin=(0, 0, z3))
            .transformed(rotate=cq.Vector(0, 0, tri_rot))
            .polygon(3, tri_diam)
            .extrude(tri_h)
        )
    
        # --- Step 5: Union all parts ---
        result = hex1.union(hex2).union(hex3).union(tri)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Total height should be sum of all four extrusions
        total_h = hex1_h + hex2_h + hex3_h + tri_h
        assert abs(bb.zlen - total_h) < TOL, \
            f"Total height: expected {total_h:.6f}, got {bb.zlen:.6f}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min: expected 0.0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - total_h) < TOL, \
            f"Z max: expected {total_h:.6f}, got {bb.zmax:.6f}"
    
        # XY extents: dominated by the largest hexagon (hex1)
        # For a regular hexagon with side s, the flat-to-flat distance = s*sqrt(3), vertex-to-vertex = 2*s
        # The bounding box in XY is 2*s x s*sqrt(3) (for 0° rotation)
        # At 0° rotation, vertices are at angles 0,60,120... so xlen = 2*s, ylen = s*sqrt(3)
        hex1_vertex_to_vertex = 2.0 * hex1_side  # = hex1_diam
        hex1_flat_to_flat = hex1_side * math.sqrt(3)
        # With 0° rotation, polygon vertices at 0°,60°,... so x extent = 2*R, y extent = sqrt(3)*R
        assert abs(bb.xlen - hex1_vertex_to_vertex) < TOL, \
            f"XY xlen: expected {hex1_vertex_to_vertex:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - hex1_flat_to_flat) < TOL, \
            f"XY ylen: expected {hex1_flat_to_flat:.6f}, got {bb.ylen:.6f}"
    
        # Volume check: sum of individual volumes
        # Volume of regular hexagon prism = (3*sqrt(3)/2) * s^2 * h
        def hex_vol(s, h):
            return (3 * math.sqrt(3) / 2) * s**2 * h
    
        # Volume of regular triangle prism = (sqrt(3)/4) * a^2 * h, where a = side length
        # For circumradius R, side a = R * sqrt(3)
        def tri_vol(R, h):
            a = R * math.sqrt(3)
            return (math.sqrt(3) / 4) * a**2 * h
    
        expected_vol = (hex_vol(hex1_side, hex1_h) +
                        hex_vol(hex2_side, hex2_h) +
                        hex_vol(hex3_side, hex3_h) +
                        tri_vol(tri_r, tri_h))
    
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check we have a single solid (compound or solid)
        # The result should have at least 1 solid
        assert result.solids().size() >= 1, \
            f"Expected at least 1 solid, got {result.solids().size()}"
    
        # Check cylindrical faces count = 0 (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Expected 0 cylindrical faces, got {cyl_faces}"
    
        # Check that the top face is at the correct Z
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_h) < TOL, \
            f"Top face Z center: expected {total_h:.6f}, got {top_face_z:.6f}"
    
        # Check bottom face is at Z=0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z center: expected 0.0, got {bot_face_z:.6f}"
    
        print(f"All assertions passed!")
        print(f"Total height: {bb.zlen:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"BBox: x={bb.xlen:.4f}, y={bb.ylen:.4f}, z={bb.zlen:.4f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00853706/gpt_generated.stl')
