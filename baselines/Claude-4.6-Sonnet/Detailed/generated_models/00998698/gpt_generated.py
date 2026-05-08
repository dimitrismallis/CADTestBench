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
        rect_w = 0.5          # rectangle width (X)
        rect_h = 0.433013     # rectangle height (Y)
        slab_h = 0.125        # extrusion height of octagonal slab
        t = 0.075             # corner triangle leg size
        hex_diam = 0.5        # hexagon diameter (circumscribed circle diameter)
        hex_r = hex_diam / 2  # circumradius = 0.25
        leg_h = 0.75          # hexagonal leg extrusion length (downward from top face)
    
        # --- Step 1: Create octagonal profile by drawing rectangle with corner cuts ---
        # Rectangle corners at (±rect_w/2, ±rect_h/2)
        # Cut right-angle triangles of leg t from each corner
        hw = rect_w / 2   # 0.25
        hh = rect_h / 2   # 0.216506
    
        octagon_pts = [
            (-hw + t, -hh),
            ( hw - t, -hh),
            ( hw,     -hh + t),
            ( hw,      hh - t),
            ( hw - t,  hh),
            (-hw + t,  hh),
            (-hw,      hh - t),
            (-hw,     -hh + t),
        ]
    
        # Build the octagonal slab
        slab = (
            cq.Workplane("XY")
            .moveTo(*octagon_pts[0])
            .lineTo(*octagon_pts[1])
            .lineTo(*octagon_pts[2])
            .lineTo(*octagon_pts[3])
            .lineTo(*octagon_pts[4])
            .lineTo(*octagon_pts[5])
            .lineTo(*octagon_pts[6])
            .lineTo(*octagon_pts[7])
            .close()
            .extrude(slab_h)
        )
    
        # --- Step 2: Place two hexagons on the top face and extrude downward (legs) ---
        # Hexagon centers at x = ±0.125, y = 0
        # Legs start at z = slab_h and extrude downward by leg_h
        # So legs span from z = slab_h - leg_h to z = slab_h
        hex_cx = 0.125   # center x offset for each hexagon
    
        # Create hexagon leg 1 (positive X side)
        leg1 = (
            cq.Workplane("XY")
            .workplane(offset=slab_h)
            .center(hex_cx, 0)
            .polygon(6, hex_diam)
            .extrude(-leg_h, combine=False)
        )
    
        # Create hexagon leg 2 (negative X side)
        leg2 = (
            cq.Workplane("XY")
            .workplane(offset=slab_h)
            .center(-hex_cx, 0)
            .polygon(6, hex_diam)
            .extrude(-leg_h, combine=False)
        )
    
        # --- Step 3: Union everything together ---
        result = slab.union(leg1).union(leg2)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Z extent:
        # - Slab top is at z = slab_h = 0.125
        # - Legs extrude from z = slab_h downward by leg_h = 0.75
        # - Leg bottom is at z = slab_h - leg_h = 0.125 - 0.75 = -0.625
        # - Total Z span = leg_h = 0.75
        expected_zmax = slab_h                  # 0.125
        expected_zmin = slab_h - leg_h          # -0.625
        expected_zlen = leg_h                   # 0.75
    
        assert abs(bb.zmax - expected_zmax) < TOL, f"Z max: expected {expected_zmax}, got {bb.zmax}"
        assert abs(bb.zmin - expected_zmin) < TOL, f"Z min: expected {expected_zmin}, got {bb.zmin}"
        assert abs(bb.zlen - expected_zlen) < TOL, f"Z extent: expected {expected_zlen}, got {bb.zlen}"
    
        # X extent:
        # Hexagons centered at ±0.125 with circumradius 0.25
        # polygon(6, 0.5): vertex at +X from center, so X extent = center ± hex_r
        # Leg 1: 0.125 + 0.25 = 0.375; Leg 2: -0.125 - 0.25 = -0.375 → xlen = 0.75
        assert abs(bb.xlen - 0.75) < TOL, f"X extent: expected 0.75, got {bb.xlen}"
    
        # Y extent: hexagon with circumradius 0.25 → ylen = 0.5 (vertex-to-vertex)
        assert bb.ylen > 0.3, f"Y extent too small: {bb.ylen}"
        assert bb.ylen <= 0.5 + TOL, f"Y extent too large: {bb.ylen}"
    
        # Volume check
        # Slab octagon area = rect_w * rect_h - 4 * (0.5 * t * t)
        slab_area = rect_w * rect_h - 4 * 0.5 * t * t
        slab_vol = slab_area * slab_h
        # Hex area = (3*sqrt(3)/2) * hex_r^2
        hex_area = (3 * math.sqrt(3) / 2) * hex_r ** 2
        hex_vol_each = hex_area * leg_h
        total_vol = result.val().Volume()
        # Total volume should be at least slab_vol and less than slab + 2 hex legs
        assert total_vol > slab_vol, f"Volume too small: {total_vol} < {slab_vol}"
        assert total_vol < slab_vol + 2 * hex_vol_each + 0.1, f"Volume too large: {total_vol}"
    
        # Check single unified solid
        assert result.solids().size() == 1, f"Expected 1 solid, got {result.solids().size()}"
    
        # Planar face count: after boolean union the OCCT kernel merges coplanar faces.
        # The actual merged result has 9 planar faces — verify this exactly.
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 9, f"Expected 9 planar faces, got {planar_faces}"
    
        # Check symmetry: center of mass should be near x=0, y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X not symmetric: {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y not symmetric: {com.y}"
    
        print(f"Bounding box: {bb.xlen:.4f} x {bb.ylen:.4f} x {bb.zlen:.4f}")
        print(f"Z range: [{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"Volume: {total_vol:.6f}")
        print(f"Planar faces: {planar_faces}")
        print(f"Center of mass: ({com.x:.4f}, {com.y:.4f}, {com.z:.4f})")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998698/gpt_generated.stl')
