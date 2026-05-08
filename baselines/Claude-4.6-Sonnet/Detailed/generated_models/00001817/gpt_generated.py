import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        top_length = 1.20302
        top_width  = 0.55872
        top_height = 0.020134
    
        leg_side   = 0.060403
        leg_height = 0.75
    
        # --- Step 1: Create table top centered at origin ---
        # Table top spans Z: -top_height/2 to +top_height/2
        table_top = cq.Workplane("XY").box(top_length, top_width, top_height)
    
        # --- Step 2: Compute leg corner positions ---
        # Legs are placed at corners, inset by half leg width from table edge
        # Leg center X: ±(top_length/2 - leg_side/2)
        # Leg center Y: ±(top_width/2  - leg_side/2)
        lx = top_length / 2 - leg_side / 2   # 0.571309
        ly = top_width  / 2 - leg_side / 2   # 0.249159
    
        # Leg top face is flush with table top bottom face
        # Table top bottom Z = -top_height/2
        # Leg is centered at Z = -top_height/2 - leg_height/2
        leg_z_center = -top_height / 2 - leg_height / 2
    
        # --- Step 3: Create four legs and union with table top ---
        corners = [
            ( lx,  ly),
            ( lx, -ly),
            (-lx,  ly),
            (-lx, -ly),
        ]
    
        result = table_top
        for (cx, cy) in corners:
            leg = (
                cq.Workplane("XY")
                .box(leg_side, leg_side, leg_height,
                     centered=(True, True, True))
                .translate((cx, cy, leg_z_center))
            )
            result = result.union(leg)
    
        # --- Final object verification ---
        TOL = 1e-3
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box
        expected_xlen = top_length   # 1.20302
        expected_ylen = top_width    # 0.55872
        expected_zlen = top_height + leg_height  # 0.020134 + 0.75 = 0.770134
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents: top of table top at +top_height/2, bottom of legs at -top_height/2 - leg_height
        expected_zmax = top_height / 2
        expected_zmin = -top_height / 2 - leg_height
        assert abs(bb.zmax - expected_zmax) < TOL, \
            f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zmin - expected_zmin) < TOL, \
            f"Z min: expected {expected_zmin}, got {bb.zmin}"
    
        # Volume check
        top_vol  = top_length * top_width * top_height
        leg_vol  = leg_side * leg_side * leg_height
        total_vol = top_vol + 4 * leg_vol
        computed_vol = result.val().Volume()
        assert abs(computed_vol - total_vol) / total_vol < 0.01, \
            f"Volume: expected ~{total_vol:.6f}, got {computed_vol:.6f}"
    
        # The table should have exactly 1 solid (all unioned)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Top face: the table top's upper face should be at zmax
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "Expected at least one top face"
        top_face_z = top_faces.val().Center().z
        assert abs(top_face_z - expected_zmax) < TOL, \
            f"Top face Z center: expected {expected_zmax}, got {top_face_z}"
    
        # Bottom faces: legs' bottom faces at zmin
        bottom_faces = result.faces("<Z")
        assert bottom_faces.size() >= 1, "Expected at least one bottom face"
    
        # Center of mass should be near X=0, Y=0 (symmetric table)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be ~0, got {com.y}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
        print(f"  Volume: {computed_vol:.6f} (expected {total_vol:.6f})")
        print(f"  Center of mass: ({com.x:.5f}, {com.y:.5f}, {com.z:.5f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00001817/gpt_generated.stl')
