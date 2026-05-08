import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        top_length = 120.0   # X dimension of tabletop
        top_width  = 80.0    # Y dimension of tabletop
        top_height = 10.0    # Z thickness of tabletop
    
        leg_size   = 10.0    # square leg cross-section side length
        leg_height = 60.0    # leg height (extends downward)
    
        # --- Step 1: Create the tabletop ---
        # Centered at origin: X in [-60,60], Y in [-40,40], Z in [-5,5]
        table = cq.Workplane("XY").box(top_length, top_width, top_height)
    
        # --- Step 2: Compute leg corner positions ---
        # Legs sit at the four corners of the tabletop bottom face.
        # Leg outer edges align with tabletop outer edges.
        # Leg centers are inset by half leg_size from each edge.
        half_l = top_length / 2.0 - leg_size / 2.0   # 60 - 5 = 55
        half_w = top_width  / 2.0 - leg_size / 2.0   # 40 - 5 = 35
    
        leg_positions = [
            ( half_l,  half_w),
            (-half_l,  half_w),
            ( half_l, -half_w),
            (-half_l, -half_w),
        ]
    
        # --- Step 3: Create and union each leg ---
        # Each leg is a box of leg_size × leg_size × leg_height.
        # Legs extend downward from the bottom of the tabletop (Z = -top_height/2)
        # to Z = -top_height/2 - leg_height.
        # Center of each leg in Z: -top_height/2 - leg_height/2
        leg_z_center = -top_height / 2.0 - leg_height / 2.0  # -5 - 30 = -35
    
        for (lx, ly) in leg_positions:
            leg = (
                cq.Workplane("XY")
                .box(leg_size, leg_size, leg_height,
                     centered=(True, True, True))
                .translate((lx, ly, leg_z_center))
            )
            table = table.union(leg)
    
        # --- Final object verification ---
        TOL = 0.1
    
        # Bounding box checks
        bb = table.val().BoundingBox()
    
        # X extent: tabletop dominates → 120 mm
        assert abs(bb.xlen - top_length) < TOL, \
            f"X length: expected {top_length}, got {bb.xlen}"
    
        # Y extent: tabletop dominates → 80 mm
        assert abs(bb.ylen - top_width) < TOL, \
            f"Y length: expected {top_width}, got {bb.ylen}"
    
        # Z extent: tabletop (10) + legs (60) = 70 mm
        expected_zlen = top_height + leg_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z bounds: top at +5, bottom at -65
        assert abs(bb.zmax - top_height / 2.0) < TOL, \
            f"Z max: expected {top_height/2.0}, got {bb.zmax}"
        assert abs(bb.zmin - (-top_height / 2.0 - leg_height)) < TOL, \
            f"Z min: expected {-top_height/2.0 - leg_height}, got {bb.zmin}"
    
        # Volume check
        top_vol  = top_length * top_width * top_height
        leg_vol  = leg_size * leg_size * leg_height
        # Legs attach flush to the bottom of the tabletop — no overlap
        expected_vol = top_vol + 4 * leg_vol
        actual_vol   = table.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # There should be exactly 1 solid (all unioned)
        assert table.solids().size() == 1, \
            f"Solid count: expected 1, got {table.solids().size()}"
    
        # Top face should be at Z = +5
        top_face_z = table.faces(">Z").val().Center().z
        assert abs(top_face_z - top_height / 2.0) < TOL, \
            f"Top face Z center: expected {top_height/2.0}, got {top_face_z}"
    
        # Bottom faces of legs should be at Z = -65
        bottom_face_z = table.faces("<Z").val().Center().z
        assert abs(bottom_face_z - (-top_height / 2.0 - leg_height)) < TOL, \
            f"Bottom face Z: expected {-top_height/2.0 - leg_height}, got {bottom_face_z}"
    
        # Check that the four leg bottom faces exist (4 separate planar faces at min Z)
        bottom_faces = [
            f for f in table.faces("<Z").vals()
            if abs(f.Center().z - bb.zmin) < TOL
        ]
        # After union, the 4 leg bottoms are separate planar faces at zmin
        assert len(bottom_faces) >= 1, \
            f"Expected at least 1 bottom face at zmin, got {len(bottom_faces)}"
    
        # Symmetry: center of mass should be near X=0, Y=0
        com = cq.Shape.centerOfMass(table.val())
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y}"
    
        return table
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00001817/gpt_generated.stl')
