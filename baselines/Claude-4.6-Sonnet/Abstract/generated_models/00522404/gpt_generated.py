import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        square_side = 20.0        # base square side length (X and Z dimensions)
        base_extrude = 5.0        # small extrusion of base along Y
        pillar_width_x = 20.0     # pillar X dimension (same as square side)
        pillar_width_z = 10.0     # pillar Z dimension (~half of square side)
        pillar_extrude = 100.0    # large extrusion for pillar along Y
    
        # --- Step 1: Create the square base on the X-Z plane ---
        # Use "XZ" workplane so that extrusion goes along Y axis (negative Y direction)
        # centered=True means the square is centered at origin in X and Z
        base = (
            cq.Workplane("XZ")
            .rect(square_side, square_side)
            .extrude(base_extrude)
        )
    
        # --- Step 2: Create the pillar shaft ---
        # Same X length (20), but half Z width (10), centered at same location
        # Extrude a large amount along Y
        pillar = (
            cq.Workplane("XZ")
            .rect(pillar_width_x, pillar_width_z)
            .extrude(pillar_extrude)
        )
    
        # --- Step 3: Union base and pillar ---
        result = base.union(pillar)
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # X extent: square_side = 20
        assert abs(bb.xlen - square_side) < TOL, \
            f"X length: expected {square_side}, got {bb.xlen}"
    
        # Y extent: pillar_extrude = 100 (pillar is taller than base)
        assert abs(bb.ylen - pillar_extrude) < TOL, \
            f"Y length (height): expected {pillar_extrude}, got {bb.ylen}"
    
        # Z extent: square_side = 20 (base is wider in Z than pillar)
        assert abs(bb.zlen - square_side) < TOL, \
            f"Z length: expected {square_side}, got {bb.zlen}"
    
        # Bounding box should be centered at X=0, Z=0
        assert abs(bb.xmin + square_side / 2) < TOL, \
            f"X min: expected {-square_side/2}, got {bb.xmin}"
        assert abs(bb.xmax - square_side / 2) < TOL, \
            f"X max: expected {square_side/2}, got {bb.xmax}"
        assert abs(bb.zmin + square_side / 2) < TOL, \
            f"Z min: expected {-square_side/2}, got {bb.zmin}"
        assert abs(bb.zmax - square_side / 2) < TOL, \
            f"Z max: expected {square_side/2}, got {bb.zmax}"
    
        # XZ workplane extrudes in -Y direction: Y goes from -pillar_extrude to 0
        assert abs(bb.ymin + pillar_extrude) < TOL, \
            f"Y min: expected {-pillar_extrude}, got {bb.ymin}"
        assert abs(bb.ymax) < TOL, \
            f"Y max: expected 0, got {bb.ymax}"
    
        # Volume check:
        # Base volume: 20 * 20 * 5 = 2000
        # Pillar volume: 20 * 10 * 100 = 20000
        # Overlap (base region of pillar): 20 * 10 * 5 = 1000
        # Union volume = 2000 + 20000 - 1000 = 21000
        base_vol = square_side * square_side * base_extrude
        pillar_vol = pillar_width_x * pillar_width_z * pillar_extrude
        overlap_vol = pillar_width_x * pillar_width_z * base_extrude
        expected_vol = base_vol + pillar_vol - overlap_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check that the base is wider than the pillar in Z
        # A point at Z=8 (between pillar edge z=5 and base edge z=10) at Y=-2 (in base region)
        # should be inside the solid
        assert result.val().isInside((0, -2, 8)), \
            "Point in base flange region should be inside solid"
    
        # A point at Z=8 at Y=-50 (in pillar region, beyond base) should be outside
        assert not result.val().isInside((0, -50, 8)), \
            "Point outside pillar (in Z) at pillar height should be outside solid"
    
        # A point at Z=3 at Y=-50 (inside pillar) should be inside
        assert result.val().isInside((0, -50, 3)), \
            "Point inside pillar shaft should be inside solid"
    
        # Face count check: the union should produce a reasonable number of planar faces
        planar_face_count = result.faces("%Plane").size()
        assert planar_face_count >= 8, \
            f"Expected at least 8 planar faces, got {planar_face_count}"
    
        print(f"Bounding box: X={bb.xlen}, Y={bb.ylen}, Z={bb.zlen}")
        print(f"Y range: [{bb.ymin}, {bb.ymax}]")
        print(f"Volume: {actual_vol:.1f} (expected {expected_vol:.1f})")
        print(f"Planar faces: {planar_face_count}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00522404/gpt_generated.stl')
