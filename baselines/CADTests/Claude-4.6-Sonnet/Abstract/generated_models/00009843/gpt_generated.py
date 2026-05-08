import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        # Base rectangle
        base_w = 60.0   # X width
        base_d = 40.0   # Y depth
        base_h = 5.0    # Z height (slight extrusion)
    
        # Second rectangle (narrower left/right only)
        rect2_w = 50.0  # X width (smaller than base by 5 on each side)
        rect2_d = 40.0  # Y depth (same as base)
        rect2_h = 5.0   # Z height (slight extrusion)
    
        # Trapezoid (inverted isosceles: wider at top, narrower at bottom)
        # Bottom width slightly longer than rect2_w
        trap_bot_w = 52.0   # bottom width (slightly longer than rect2_w=50)
        trap_top_w = 70.0   # top width (wider)
        trap_d = 40.0        # Y depth (same)
        trap_h = 10.0        # Z height
    
        # --- Step 1: Base rectangle extruded ---
        result = cq.Workplane("XY").rect(base_w, base_d).extrude(base_h)
    
        # --- Step 2: Second rectangle on top (narrower in X, same Y) ---
        result = (
            result
            .faces(">Z").workplane()
            .rect(rect2_w, rect2_d)
            .extrude(rect2_h)
        )
    
        # --- Step 3: Inverted isosceles trapezoid on top ---
        # The trapezoid has:
        #   bottom edge (at z = base_h + rect2_h): width = trap_bot_w
        #   top edge (at z = base_h + rect2_h + trap_h): width = trap_top_w
        # It's centered at x=0, y=0
        # We build the profile as a closed wire using lineTo/close
        # The workplane is at z = base_h + rect2_h, XY plane
        # Points (in workplane 2D coords):
        #   bottom-left:  (-trap_bot_w/2, -trap_d/2)
        #   bottom-right: ( trap_bot_w/2, -trap_d/2)
        #   top-right:    ( trap_top_w/2,  trap_d/2)  -- but this is in 3D after extrude
        # Wait - the trapezoid is a 3D shape. The trapezoidal cross-section is in XZ plane
        # (varying width in X as Z increases), constant in Y.
        # 
        # Better approach: use a 2D profile in XY at the top face workplane,
        # but the trapezoid shape varies in X. We need to use a loft or
        # draw the trapezoid profile as a 2D shape and extrude it.
        #
        # Actually, the trapezoid is the top-view cross section:
        # bottom (at current z): width trap_bot_w, depth trap_d
        # top (at z + trap_h): width trap_top_w, depth trap_d
        # This is a frustum-like shape. We can use loft.
    
        z_trap_start = base_h + rect2_h
    
        result = (
            result
            .faces(">Z").workplane()
            .rect(trap_bot_w, trap_d)
            .workplane(offset=trap_h)
            .rect(trap_top_w, trap_d)
            .loft(combine=True)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X: widest part is trap_top_w = 70
        assert abs(bb.xlen - trap_top_w) < TOL, f"X extent: expected {trap_top_w}, got {bb.xlen}"
        # Y: all layers have same depth = 40
        assert abs(bb.ylen - base_d) < TOL, f"Y extent: expected {base_d}, got {bb.ylen}"
        # Z: total height = base_h + rect2_h + trap_h = 5 + 5 + 10 = 20
        total_h = base_h + rect2_h + trap_h
        assert abs(bb.zlen - total_h) < TOL, f"Z extent: expected {total_h}, got {bb.zlen}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - total_h) < TOL, f"Z max: expected {total_h}, got {bb.zmax}"
    
        # X extents (centered at 0)
        assert abs(bb.xmin - (-trap_top_w / 2)) < TOL, f"X min: expected {-trap_top_w/2}, got {bb.xmin}"
        assert abs(bb.xmax - (trap_top_w / 2)) < TOL, f"X max: expected {trap_top_w/2}, got {bb.xmax}"
    
        # Volume check
        # Layer 1: base rectangle box
        vol1 = base_w * base_d * base_h  # 60*40*5 = 12000
    
        # Layer 2: second rectangle box
        vol2 = rect2_w * rect2_d * rect2_h  # 50*40*5 = 10000
    
        # Layer 3: frustum (loft between two rectangles)
        # Volume of a prismatoid: V = h/6 * (A1 + A2 + 4*Am)
        # where Am is area of mid-section
        A1 = trap_bot_w * trap_d   # 52*40 = 2080
        A2 = trap_top_w * trap_d   # 70*40 = 2800
        mid_w = (trap_bot_w + trap_top_w) / 2  # 61
        Am = mid_w * trap_d         # 61*40 = 2440
        vol3 = trap_h / 6 * (A1 + A2 + 4 * Am)  # 10/6*(2080+2800+9760) = 10/6*14640 = 24400
    
        expected_vol = vol1 + vol2 + vol3
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check that the object is a single solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Check center of mass is roughly at x=0, y=0 (symmetric)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
    
        # Check that the bottom face is at z=0 with area = base_w * base_d
        bottom_faces = result.faces("<Z")
        assert bottom_faces.size() >= 1, "No bottom face found"
        bottom_area = bottom_faces.val().Area()
        expected_bottom_area = base_w * base_d
        assert abs(bottom_area - expected_bottom_area) < TOL, \
            f"Bottom face area: expected {expected_bottom_area}, got {bottom_area}"
    
        # Check that the top face is at z=total_h with area = trap_top_w * trap_d
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "No top face found"
        top_area = top_faces.val().Area()
        expected_top_area = trap_top_w * trap_d
        assert abs(top_area - expected_top_area) < TOL, \
            f"Top face area: expected {expected_top_area}, got {top_area}"
    
        # Check cylindrical faces count = 0 (no holes)
        cyl_faces = result.faces("%Cylinder")
        assert cyl_faces.size() == 0, f"Expected no cylindrical faces, got {cyl_faces.size()}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00009843/gpt_generated.stl')
