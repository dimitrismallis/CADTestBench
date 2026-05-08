import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_w = 60.0       # half-base = 30
        height = 80.0       # full triangle height
        fillet_r = 6.0      # bottom corner fillet radius
        trunc_y = 65.0      # y-level where top is cut off
        extrude_d = 10.0    # extrusion depth
        hole_r = 2.0        # small hole radius
    
        # Triangle vertices (before truncation):
        # Bottom-left: (-30, 0), Bottom-right: (30, 0), Apex: (0, 80)
        # Left side line: from (-30,0) to (0,80)  => direction (30, 80)
        # Right side line: from (30,0) to (0,80)  => direction (-30, 80)
    
        # Find where left and right sides intersect y = trunc_y:
        t_trunc = trunc_y / height
        trunc_left_x  = -30 + 30 * t_trunc   # = -5.625
        trunc_right_x =  30 - 30 * t_trunc   # =  5.625
    
        # Left side unit direction (from BL toward apex):
        left_len = math.sqrt(30**2 + 80**2)   # ≈ 85.44
        left_dir = (30 / left_len, 80 / left_len)
    
        # Right side unit direction (from BR toward apex):
        right_dir = (-30 / left_len, 80 / left_len)
    
        # --- Fillet tangent points ---
        # Bottom-left corner (-30, 0):
        bl_tan_bottom = (-30 + fillet_r, 0.0)
        bl_tan_left   = (-30 + fillet_r * left_dir[0],
                          fillet_r * left_dir[1])
    
        # Bottom-right corner (30, 0):
        br_tan_right  = (30 + fillet_r * right_dir[0],
                          fillet_r * right_dir[1])
        br_tan_bottom = (30 - fillet_r, 0.0)
    
        # --- Fillet arc midpoints (point on arc closest to the corner) ---
        # BL fillet:
        bis_bl      = (1.0 + left_dir[0], left_dir[1])
        bis_bl_len  = math.sqrt(bis_bl[0]**2 + bis_bl[1]**2)
        bis_bl_unit = (bis_bl[0] / bis_bl_len, bis_bl[1] / bis_bl_len)
        cos_bl      = left_dir[0] * 1.0 + left_dir[1] * 0.0
        half_bl     = math.acos(max(-1.0, min(1.0, cos_bl))) / 2.0
        d_bl        = fillet_r / math.sin(half_bl)
        center_bl   = (-30 + d_bl * bis_bl_unit[0],
                        d_bl * bis_bl_unit[1])
        arc_mid_bl  = (center_bl[0] - fillet_r * bis_bl_unit[0],
                       center_bl[1] - fillet_r * bis_bl_unit[1])
    
        # BR fillet (mirror of BL):
        bis_br      = (right_dir[0] - 1.0, right_dir[1])
        bis_br_len  = math.sqrt(bis_br[0]**2 + bis_br[1]**2)
        bis_br_unit = (bis_br[0] / bis_br_len, bis_br[1] / bis_br_len)
        cos_br      = right_dir[0] * (-1.0) + right_dir[1] * 0.0
        half_br     = math.acos(max(-1.0, min(1.0, cos_br))) / 2.0
        d_br        = fillet_r / math.sin(half_br)
        center_br   = (30 + d_br * bis_br_unit[0],
                        d_br * bis_br_unit[1])
        arc_mid_br  = (center_br[0] - fillet_r * bis_br_unit[0],
                       center_br[1] - fillet_r * bis_br_unit[1])
    
        # --- Build the 2D profile via Sketch API ---
        # Traverse counter-clockwise:
        #   bottom edge → BR fillet arc → right side → top flat → left side → BL fillet arc → close
        s = (
            cq.Sketch()
            .segment(bl_tan_bottom, br_tan_bottom)
            .arc(br_tan_bottom, arc_mid_br, br_tan_right)
            .segment(br_tan_right, (trunc_right_x, trunc_y))
            .segment((trunc_right_x, trunc_y), (trunc_left_x, trunc_y))
            .segment((trunc_left_x, trunc_y), bl_tan_left)
            .arc(bl_tan_left, arc_mid_bl, bl_tan_bottom)
            .assemble(tag="face")
        )
    
        # --- Step 1: Extrude the sketch ---
        result = cq.Workplane("XY").placeSketch(s).extrude(extrude_d)
    
        # --- Step 2: Add through-holes near each corner ---
        # Near bottom-left rounded corner:
        hole_bl  = (-20.0,  8.0)
        # Near bottom-right rounded corner:
        hole_br  = ( 20.0,  8.0)
        # Near truncated top edge:
        hole_top = (  0.0, trunc_y - 8.0)
    
        result = (
            result
            .faces(">Z").workplane()
            .pushPoints([hole_bl, hole_br, hole_top])
            .hole(hole_r * 2)   # hole() takes diameter
        )
    
        # --- Final object verification ---
        TOL = 0.5
        solid = result.val()
        bb    = solid.BoundingBox()
    
        # --- Compute expected bounding box X from fillet geometry ---
        leftmost_x = min(bl_tan_left[0], center_bl[0] - fillet_r)
        expected_xlen = 2.0 * abs(leftmost_x)   # symmetric profile
    
        # Bounding box X
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length expected ~{expected_xlen:.3f}, got {bb.xlen:.3f}"
    
        # Bounding box Y: 0 to trunc_y
        assert abs(bb.ylen - trunc_y) < TOL, \
            f"Y length expected ~{trunc_y}, got {bb.ylen:.3f}"
    
        # Bounding box Z: extrusion depth
        assert abs(bb.zlen - extrude_d) < TOL, \
            f"Z length expected {extrude_d}, got {bb.zlen:.3f}"
    
        # --- Volume check ---
        # Approximate cross-section as a trapezoid (top_width × trunc_y, base = base_w)
        top_width  = trunc_right_x - trunc_left_x   # ≈ 11.25
        trap_area  = 0.5 * (base_w + top_width) * trunc_y
        hole_area  = 3.0 * math.pi * hole_r**2
        approx_vol = (trap_area - hole_area) * extrude_d
        actual_vol = solid.Volume()
        # Allow 15% tolerance (fillets reduce area)
        assert abs(actual_vol - approx_vol) / approx_vol < 0.15, \
            f"Volume expected ~{approx_vol:.1f}, got {actual_vol:.1f}"
    
        # --- Cylindrical faces count ---
        # 2 from extruded bottom corner fillet arcs + 3 from through-holes = 5 total
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count == 5, \
            f"Expected 5 cylindrical faces (2 corner fillets + 3 holes), got {cyl_count}"
    
        # --- Holes are through-holes: points at hole centres should be outside solid ---
        mid_z = extrude_d / 2.0
        for label, pt in [("BL hole",  (hole_bl[0],  hole_bl[1],  mid_z)),
                          ("BR hole",  (hole_br[0],  hole_br[1],  mid_z)),
                          ("Top hole", (hole_top[0], hole_top[1], mid_z))]:
            assert not solid.isInside(pt), \
                f"{label} centre {pt} should be outside solid (inside hole)"
    
        # --- Body centre is inside solid ---
        body_centre = (0.0, trunc_y / 3.0, mid_z)
        assert solid.isInside(body_centre), \
            f"Body centre {body_centre} should be inside solid"
    
        # --- Symmetry: centre of mass X ≈ 0 ---
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, \
            f"Centre of mass X should be ~0 (symmetric), got {com.x:.4f}"
    
        print("All assertions passed!")
        print(f"  BBox: x={bb.xlen:.3f}, y={bb.ylen:.3f}, z={bb.zlen:.3f}")
        print(f"  Expected xlen: {expected_xlen:.3f}")
        print(f"  Volume: {actual_vol:.2f}  (approx trapezoid: {approx_vol:.2f})")
        print(f"  Cylindrical faces: {cyl_count}")
        print(f"  Centre of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998356/gpt_generated.stl')
