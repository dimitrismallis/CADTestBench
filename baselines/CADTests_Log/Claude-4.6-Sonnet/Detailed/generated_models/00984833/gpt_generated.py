import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 0.475652
        width_narrow = 0.049547   # top tier (narrower)
        width_wide   = 0.198188   # base tier (wider)
        height       = 0.317101   # height of each tier
    
        # --- Step 1: Base tier (wider rectangle), centered at origin in XY ---
        # centered=True means the box is centered at (0,0,0)
        # So it spans Z from -height/2 to +height/2
        base = (
            cq.Workplane("XY")
            .box(length, width_wide, height, centered=True)
        )
    
        # --- Step 2: Top tier (narrower rectangle), centered in XY, placed on top ---
        # The base top face is at Z = +height/2
        # The top tier should sit on top, so its bottom is at Z = +height/2
        # Using centered=(True, True, False) so it starts at Z=height/2 and goes up
        top = (
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, height / 2))
            .box(length, width_narrow, height, centered=(True, True, False))
        )
    
        # --- Step 3: Union the two tiers ---
        result = base.union(top)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        expected_xlen = length
        expected_ylen = width_wide   # wider dimension dominates Y
        expected_zlen = height * 2   # two tiers stacked
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Z extents: base centered at 0, so zmin = -height/2, zmax = +height + height/2
        assert abs(bb.zmin - (-height / 2)) < TOL, \
            f"Z min: expected {-height/2}, got {bb.zmin}"
        assert abs(bb.zmax - (height * 3 / 2)) < TOL, \
            f"Z max: expected {height * 3 / 2}, got {bb.zmax}"
    
        # Volume check: sum of two rectangular boxes
        vol_base = length * width_wide   * height
        vol_top  = length * width_narrow * height
        expected_vol = vol_base + vol_top
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # The object should be a single solid (union)
        assert result.solids().size() == 1, \
            f"Expected 1 solid, got {result.solids().size()}"
    
        # Face count: two rectangular boxes unioned sharing a partial face
        # Base box: 6 faces; top box: 6 faces; the shared interface creates splits
        # The top face of base is partially covered by the narrower top box
        # Expect more than 6 faces due to the step geometry
        face_count = result.faces().size()
        assert face_count >= 8, \
            f"Expected at least 8 faces for tiered shape, got {face_count}"
    
        # Center of mass should be at X=0, Y=0 (symmetric), Z somewhere between tiers
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected 0, got {com.y}"
    
        # The top tier is narrower in Y — check that the top face is narrower
        top_faces = result.faces(">Z")
        top_bb = top_faces.val().BoundingBox()
        assert abs(top_bb.ylen - width_narrow) < TOL, \
            f"Top face Y width: expected {width_narrow}, got {top_bb.ylen}"
        assert abs(top_bb.xlen - length) < TOL, \
            f"Top face X length: expected {length}, got {top_bb.xlen}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00984833/gpt_generated.stl')
