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
        # Large cylinder
        h1 = 0.75
        d1 = 0.470339
        r1 = d1 / 2  # 0.235170
    
        # Second cylinder
        h2 = 0.082627
        d2 = 0.152542
        r2 = d2 / 2  # 0.076271
    
        # Third cylinder
        h3 = 0.190678
        d3 = 0.075981
        r3 = d3 / 2  # 0.037991
    
        # Padding from edge of first cylinder
        padding = 0.247881
    
        # Offset of small cylinders from center of large cylinder
        # "slightly below center" with padding from edge
        offset = r1 - padding  # 0.235170 - 0.247881 = -0.012711
        # magnitude = abs(offset) = 0.012711, direction = -Y (below center)
        cy_offset = offset  # negative value → below center in Y
    
        # --- Step 1: Large cylinder centered at origin, axis along Z ---
        large_cyl = cq.Workplane("XY").cylinder(h1, r1)
        # large cylinder spans z from -h1/2 to h1/2
    
        # --- Step 2: Second cylinder on top face of large cylinder, offset in Y ---
        # Top face of large cylinder is at z = h1/2 = 0.375
        # Second cylinder protrudes upward from top face
        # Center of second cylinder base at (0, cy_offset, h1/2)
        second_cyl = (
            cq.Workplane("XY")
            .workplane(offset=h1 / 2)  # at z = 0.375
            .center(0, cy_offset)
            .cylinder(h2, r2)
        )
        # The cylinder() is centered, so it spans from h1/2 - h2/2 to h1/2 + h2/2
        # We want it to protrude outward (above top face), so we need to shift it up by h2/2
        # Let's use a different approach: place the base at z=h1/2 and extrude upward
    
        # --- Step 2 (revised): Build second cylinder with base at z=h1/2 ---
        second_cyl = (
            cq.Workplane("XY")
            .workplane(offset=h1 / 2)
            .center(0, cy_offset)
            .circle(r2)
            .extrude(h2)
        )
    
        # --- Step 3: Third cylinder concentric with second, protruding outward ---
        # Base at z = h1/2 + h2 (top of second cylinder), protruding further up
        # Wait - "protrudes outward" from the second cylinder - concentric means same axis
        # Third cylinder base at z = h1/2, same position, protrudes outward (upward)
        # But it's taller (h3 = 0.190678 > h2 = 0.082627)
        # "concentric with the second cylinder and protrudes outward" - likely stacked on top of second
        # OR it could mean it starts at the same base as the second cylinder
        # Given h3 > h2, if they share the same base, third extends beyond second
        # Let's place third cylinder with base at z=h1/2, same as second cylinder
        third_cyl = (
            cq.Workplane("XY")
            .workplane(offset=h1 / 2)
            .center(0, cy_offset)
            .circle(r3)
            .extrude(h3)
        )
    
        # --- Step 4: Union all three cylinders ---
        assembly = large_cyl.union(second_cyl).union(third_cyl)
    
        # --- Step 5: Rotate entire assembly by -90 degrees around Y-axis ---
        assembly = assembly.rotate((0, 0, 0), (0, 1, 0), -90)
    
        # --- Final object verification ---
        TOL = 0.01
    
        solid = assembly.val()
        bb = solid.BoundingBox()
    
        # After -90° rotation around Y-axis:
        # Original X → -Z (new Z = -old X)
        # Original Y → Y (unchanged)
        # Original Z → X (new X = old Z)
        #
        # Before rotation:
        # Large cylinder: x in [-r1, r1], y in [-r1, r1], z in [-h1/2, h1/2]
        # Second cylinder: x in [-r2, r2], y in [cy_offset-r2, cy_offset+r2], z in [h1/2, h1/2+h2]
        # Third cylinder: x in [-r3, r3], y in [cy_offset-r3, cy_offset+r3], z in [h1/2, h1/2+h3]
        #
        # After rotation (X_new = Z_old, Y_new = Y_old, Z_new = -X_old):
        # Large cylinder: x_new in [-h1/2, h1/2], y_new in [-r1, r1], z_new in [-r1, r1]
        # Third cylinder extends to z_old = h1/2 + h3 → x_new = h1/2 + h3
        # So total x_new range: [-h1/2, h1/2 + h3]
    
        expected_xlen = h1 / 2 + h3 + h1 / 2  # = h1 + h3
        expected_ylen = 2 * r1  # diameter of large cylinder
        expected_zlen = 2 * r1  # diameter of large cylinder
    
        print(f"BoundingBox: xlen={bb.xlen:.6f}, ylen={bb.ylen:.6f}, zlen={bb.zlen:.6f}")
        print(f"Expected: xlen≈{expected_xlen:.6f}, ylen≈{expected_ylen:.6f}, zlen≈{expected_zlen:.6f}")
        print(f"Volume: {solid.Volume():.6f}")
        print(f"cy_offset: {cy_offset:.6f}")
    
        # X extent: from -h1/2 to h1/2 + h3 (large cyl center at 0, extends ±h1/2 in old Z → new X)
        # Plus third cylinder adds from h1/2 to h1/2+h3
        assert abs(bb.xlen - (h1 + h3)) < TOL, f"X length expected {h1+h3:.4f}, got {bb.xlen:.4f}"
    
        # Y extent: dominated by large cylinder diameter
        assert abs(bb.ylen - d1) < TOL, f"Y length expected {d1:.4f}, got {bb.ylen:.4f}"
    
        # Z extent: dominated by large cylinder diameter (after rotation, old X → new Z)
        assert abs(bb.zlen - d1) < TOL, f"Z length expected {d1:.4f}, got {bb.zlen:.4f}"
    
        # Volume check: sum of three cylinders minus overlaps
        # Large cylinder volume
        vol_large = math.pi * r1**2 * h1
        # Second cylinder volume (fully outside large cyl top face)
        vol_second = math.pi * r2**2 * h2
        # Third cylinder volume (fully outside large cyl top face, inside second for h2 portion)
        vol_third = math.pi * r3**2 * h3
        # Overlap: third cylinder overlaps with second cylinder for height h2
        vol_overlap_23 = math.pi * r3**2 * h2  # third is inside second for h2 height
        expected_vol = vol_large + vol_second + vol_third - vol_overlap_23
        print(f"Expected volume: {expected_vol:.6f}")
        assert abs(solid.Volume() - expected_vol) / expected_vol < 0.05, \
            f"Volume expected ~{expected_vol:.4f}, got {solid.Volume():.4f}"
    
        # Check cylindrical faces exist (at least 3 for the three cylinders)
        cyl_faces = assembly.faces("%Cylinder").size()
        print(f"Cylindrical faces: {cyl_faces}")
        assert cyl_faces >= 3, f"Expected at least 3 cylindrical faces, got {cyl_faces}"
    
        # Check the assembly has exactly 1 solid
        n_solids = assembly.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        return assembly
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00670268/gpt_generated.stl')
