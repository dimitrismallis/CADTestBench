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
        length   = 80.0   # long dimension (X)
        width    = 40.0   # short dimension (Y)
        height   = 10.0   # extrusion height
        fillet_r = 8.0    # corner fillet radius
        hole_d   = 6.0    # hole diameter
        hole_r   = hole_d / 2.0
    
        r      = fillet_r
        half_l = length / 2.0   # 40
        half_w = width  / 2.0   # 20
    
        # --- Step 1: Create rectangular box ---
        base = cq.Workplane("XY").box(length, width, height)
    
        # --- Step 2: Fillet only the two vertical edges on the +Y side ---
        # The two vertical edges at the +Y corners are at:
        # (-40, +20, z) and (+40, +20, z) for z in [−5, +5]
        # We select edges that are parallel to Z (|Z) and at maximum Y (>Y)
        # ">Y" for edges gives the edge(s) with center of mass at max Y
        # But there are 2 such edges (left and right), so we need both.
        # Use "|Z and >Y" — edges parallel to Z that are at max Y
    
        result = (
            base
            .edges("|Z and >Y")
            .fillet(fillet_r)
        )
    
        # --- Step 3: Two circular holes near the rounded corners on the +Y side ---
        hole_x = half_l - r          # 32
        hole_y = half_w - r - 2.0    # 10
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([(-hole_x, hole_y), (hole_x, hole_y)])
            .hole(hole_d)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width)  < TOL, f"Y length: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z length: expected {height}, got {bb.zlen}"
    
        # Cylindrical faces: 2 fillet cylinders + 2 hole cylinders = 4
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count == 4, f"Cylindrical faces: expected 4, got {cyl_count}"
    
        # Volume: profile area * height - 2 hole volumes
        rect_area    = length * width
        corner_cut   = r * r - math.pi * r * r / 4.0
        profile_area = rect_area - 2.0 * corner_cut
        hole_vol     = 2.0 * math.pi * hole_r**2 * height
        expected_vol = profile_area * height - hole_vol
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.02, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Holes exist: points inside hole columns should be outside the solid
        solid = result.val()
        left_hole_pt  = cq.Vector(-hole_x, hole_y, height / 2.0)
        right_hole_pt = cq.Vector( hole_x, hole_y, height / 2.0)
        assert not solid.isInside(left_hole_pt,  tolerance=0.1), \
            "Left hole: point should be outside solid"
        assert not solid.isInside(right_hole_pt, tolerance=0.1), \
            "Right hole: point should be outside solid"
    
        # Rounded corners: points very close to the sharp corner should be outside
        assert not solid.isInside(cq.Vector(-half_l + 0.1,  half_w - 0.1, height / 2.0), tolerance=0.01), \
            "Top-left corner should be rounded (outside solid)"
        assert not solid.isInside(cq.Vector( half_l - 0.1,  half_w - 0.1, height / 2.0), tolerance=0.01), \
            "Top-right corner should be rounded (outside solid)"
    
        # Bottom corners should remain sharp (inside solid)
        assert solid.isInside(cq.Vector(-half_l + 0.1, -half_w + 0.1, height / 2.0), tolerance=0.01), \
            "Bottom-left corner should be sharp (inside solid)"
        assert solid.isInside(cq.Vector( half_l - 0.1, -half_w + 0.1, height / 2.0), tolerance=0.01), \
            "Bottom-right corner should be sharp (inside solid)"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00986712/gpt_generated.stl')
