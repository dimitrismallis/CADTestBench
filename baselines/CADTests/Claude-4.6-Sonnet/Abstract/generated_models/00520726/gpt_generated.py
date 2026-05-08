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
        side = 8.0          # square side length (mm)
        height = 14.0       # extrusion height (~1.75x side, "almost twice")
        wall = 1.5          # shell wall thickness
        stud_radius = 2.4   # stud radius (about 1/3 of side)
        stud_height = height / 7.0  # ~2mm, about 1/7th of height
    
        # --- Step 1: Extrude a square (box) ---
        # Box centered at origin in XY, extending from Z=0 to Z=height
        result = cq.Workplane("XY").box(side, side, height, centered=(True, True, False))
    
        # --- Step 2: Hollow out keeping the top face ---
        # Shell with negative thickness (inward), removing the bottom face (<Z)
        result = result.faces("<Z").shell(-wall)
    
        # --- Step 3: Add stud on top ---
        # Select top face, place workplane, draw circle, extrude upward
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(stud_radius)
            .extrude(stud_height)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Bounding box: X and Y should be 'side', Z should be height + stud_height
        assert abs(bb.xlen - side) < TOL, f"X extent: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - side) < TOL, f"Y extent: expected {side}, got {bb.ylen}"
        expected_total_height = height + stud_height
        assert abs(bb.zlen - expected_total_height) < TOL, \
            f"Z extent: expected {expected_total_height}, got {bb.zlen}"
    
        # Bottom at Z=0, top at Z=height+stud_height
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - expected_total_height) < TOL, \
            f"Z max: expected {expected_total_height}, got {bb.zmax}"
    
        # Volume check: hollow box + stud
        # Outer box volume
        outer_vol = side * side * height
        # Inner box volume (hollow interior)
        inner_side = side - 2 * wall
        inner_height = height - wall  # top is kept, bottom is open
        inner_vol = inner_side * inner_side * inner_height
        # Stud volume
        stud_vol = math.pi * stud_radius**2 * stud_height
        expected_vol = outer_vol - inner_vol + stud_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Cylindrical faces: at least 2 (stud outer + stud inner if hollow, or just outer)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces >= 1, f"Expected at least 1 cylindrical face, got {cyl_faces}"
    
        # The stud should be centered on top face (center at x=0, y=0)
        center = result.val().Center()
        # Center of mass should be near x=0, y=0 due to symmetry
        assert abs(center.x) < TOL, f"Center X: expected ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y: expected ~0, got {center.y}"
    
        # Check stud height is approximately height/7
        assert abs(stud_height - height / 7.0) < TOL, \
            f"Stud height: expected {height/7.0}, got {stud_height}"
    
        print(f"All assertions passed!")
        print(f"  side={side}, height={height}, stud_height={stud_height:.3f}")
        print(f"  BBox: {bb.xlen:.3f} x {bb.ylen:.3f} x {bb.zlen:.3f}")
        print(f"  Volume: {actual_vol:.3f} (expected ~{expected_vol:.3f})")
        print(f"  Cylindrical faces: {cyl_faces}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00520726/gpt_generated.stl')
