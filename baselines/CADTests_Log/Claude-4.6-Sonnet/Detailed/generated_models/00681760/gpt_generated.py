import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        rect_L = 0.525    # length (X)
        rect_W = 0.75     # width (Y)
        rect_H = 0.1125   # height (Z)
        trap_long = 0.525  # longer base of trapezoid
        trap_short = 0.3   # shorter base of trapezoid
        trap_H = 0.1125    # height of trapezoid (Z)
    
        # --- Step 1: Rectangular block ---
        # Centered at origin: X in [-0.2625, 0.2625], Y in [-0.375, 0.375], Z in [-0.05625, 0.05625]
        rect_block = cq.Workplane("XY").box(rect_L, rect_W, rect_H)
    
        # --- Step 2: Trapezoid prism ---
        # Cross-section in XZ plane (extruded along Y):
        # The trapezoid has:
        #   - shorter base (0.3) at bottom (attaches to rectangle's top edge)
        #   - longer base (0.525) at top (inverted trapezoid = wider at top)
        #
        # Profile vertices (in XZ, centered at x=0):
        #   Bottom-left:  (-0.15,   0)       [shorter base half = 0.15]
        #   Bottom-right: ( 0.15,   0)
        #   Top-right:    ( 0.2625, trap_H)  [longer base half = 0.2625]
        #   Top-left:     (-0.2625, trap_H)
        #
        # In the XZ workplane, the normal is -Y, so extrude(rect_W) goes from Y=0 to Y=-rect_W.
        # After translating by +rect_W/2 in Y, it spans Y=-rect_W/2 to Y=+rect_W/2 (centered).
        # Also translate by rect_H/2 in Z so the trapezoid bottom aligns with rectangle top.
    
        trap_bottom_half = trap_short / 2   # 0.15
        trap_top_half = trap_long / 2       # 0.2625
    
        # Build trapezoid profile in XZ plane, extrude along -Y direction
        trap_profile = (
            cq.Workplane("XZ")
            .moveTo(-trap_bottom_half, 0)
            .lineTo(trap_bottom_half, 0)
            .lineTo(trap_top_half, trap_H)
            .lineTo(-trap_top_half, trap_H)
            .close()
            .extrude(rect_W)  # extrudes in -Y direction: Y=0 to Y=-rect_W
        )
    
        # Translate: +rect_W/2 in Y to center, +rect_H/2 in Z to sit on top of rectangle
        trap_prism = trap_profile.translate((0, rect_W / 2, rect_H / 2))
    
        # --- Step 3: Union the two parts ---
        result = rect_block.union(trap_prism)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        # Overall bounding box:
        # X: from -0.2625 to +0.2625 → xlen = 0.525
        # Y: from -0.375 to +0.375   → ylen = 0.75
        # Z: from -rect_H/2 to rect_H/2 + trap_H = -0.05625 to 0.16875 → zlen = 0.225
        bb = result.val().BoundingBox()
    
        expected_xlen = trap_long   # 0.525
        expected_ylen = rect_W      # 0.75
        expected_zlen = rect_H + trap_H  # 0.1125 + 0.1125 = 0.225
    
        assert abs(bb.xlen - expected_xlen) < TOL, f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents:
        assert abs(bb.zmin - (-rect_H / 2)) < TOL, f"Z min: expected {-rect_H/2}, got {bb.zmin}"
        assert abs(bb.zmax - (rect_H / 2 + trap_H)) < TOL, f"Z max: expected {rect_H/2 + trap_H}, got {bb.zmax}"
    
        # Volume check:
        # Rectangle volume:
        vol_rect = rect_L * rect_W * rect_H
        # Trapezoid prism volume = area_of_trapezoid * width
        area_trap = 0.5 * (trap_short + trap_long) * trap_H
        vol_trap = area_trap * rect_W
        # No overlap between rectangle and trapezoid (they share only a face)
        expected_vol = vol_rect + vol_trap
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Check center of mass is at x=0, y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X should be 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y should be 0, got {com.y}"
    
        # Check that the structure has planar faces
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 6, f"Expected at least 6 planar faces, got {planar_faces}"
    
        # Check a point inside the rectangle block is inside the solid
        assert result.val().isInside((0, 0, 0)), "Origin should be inside the solid"
    
        # Check a point inside the trapezoid prism is inside the solid
        trap_center_z = rect_H / 2 + trap_H / 2
        assert result.val().isInside((0, 0, trap_center_z)), \
            f"Point at trapezoid center z={trap_center_z} should be inside solid"
    
        # Check a point outside (above the trapezoid) is NOT inside
        assert not result.val().isInside((0, 0, rect_H / 2 + trap_H + 0.05)), \
            "Point above trapezoid should be outside solid"
    
        print(f"Bounding box: X={bb.xlen:.5f}, Y={bb.ylen:.5f}, Z={bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Center of mass: ({com.x:.5f}, {com.y:.5f}, {com.z:.5f})")
        print(f"Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681760/gpt_generated.stl')
