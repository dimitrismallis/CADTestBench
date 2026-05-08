import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        length = 1.5
        width  = 0.004152
        height = 0.720946
        fillet_r = 0.077855
    
        # --- Build the shape directly using a rounded rectangle profile ---
        # Create a rounded rectangle in the XZ plane (length x height cross-section)
        # with corner radius fillet_r, then extrude along Y (width direction).
        # fillet_r = 0.077855 < min(length/2, height/2) = 0.360 ✓
    
        hl = length / 2    # 0.75
        hh = height / 2    # 0.360473
        r  = fillet_r      # 0.077855
        hw = width / 2     # 0.002076
    
        # Arc midpoint for a quarter circle at corner (hl, hh):
        # Start: (hl-r, hh), End: (hl, hh-r)
        # Midpoint on arc: (hl - r + r*cos(45°), hh - r + r*sin(45°))
        #                = (hl - r*(1 - cos45), hh - r*(1 - sin45))
        # cos45 = sin45 = 1/√2 ≈ 0.7071
        c45 = math.cos(math.radians(45))
    
        # Corner arc midpoints (on the arc, at 45° from each end):
        # Top-right corner (hl, hh): arc from (hl-r, hh) to (hl, hh-r)
        # midpoint: (hl - r + r*c45, hh - r + r*c45) = (hl - r*(1-c45), hh - r*(1-c45))
    
        def arc_mid(cx, cz, r, start_angle_deg, end_angle_deg):
            """Midpoint of arc centered at (cx,cz) from start to end angle."""
            mid_angle = math.radians((start_angle_deg + end_angle_deg) / 2)
            return (cx + r * math.cos(mid_angle), cz + r * math.sin(mid_angle))
    
        # Corner centers:
        # Top-right: (hl-r, hh-r), arc from 0° to 90°
        # Top-left:  (-(hl-r), hh-r), arc from 90° to 180°
        # Bot-left:  (-(hl-r), -(hh-r)), arc from 180° to 270°
        # Bot-right: (hl-r, -(hh-r)), arc from 270° to 360°
    
        tr_mid = arc_mid(hl-r, hh-r, r, 0, 90)    # top-right arc midpoint
        tl_mid = arc_mid(-(hl-r), hh-r, r, 90, 180)  # top-left
        bl_mid = arc_mid(-(hl-r), -(hh-r), r, 180, 270)  # bot-left
        br_mid = arc_mid(hl-r, -(hh-r), r, 270, 360)  # bot-right
    
        print(f"Arc midpoints:")
        print(f"  Top-right: {tr_mid}")
        print(f"  Top-left:  {tl_mid}")
        print(f"  Bot-left:  {bl_mid}")
        print(f"  Bot-right: {br_mid}")
    
        # Build the rounded rectangle profile on XZ plane
        # Start at bottom-right straight edge start, go counterclockwise
        result = (
            cq.Workplane("XZ")
            .moveTo(hl - r, -hh)           # start of bottom edge (right side)
            .lineTo(-(hl - r), -hh)        # bottom edge (left)
            .threePointArc(bl_mid, (-(hl), -(hh - r)))  # bottom-left corner arc
            .lineTo(-hl, hh - r)           # left edge (up)
            .threePointArc(tl_mid, (-(hl - r), hh))     # top-left corner arc
            .lineTo(hl - r, hh)            # top edge (right)
            .threePointArc(tr_mid, (hl, hh - r))         # top-right corner arc
            .lineTo(hl, -(hh - r))         # right edge (down)
            .threePointArc(br_mid, (hl - r, -hh))        # bottom-right corner arc
            .close()
            .extrude(hw, both=True)        # extrude symmetrically in Y direction
        )
    
        # --- Final object verification ---
        TOL = 0.01
        bb = result.val().BoundingBox()
    
        print(f"\nBBox: x={bb.xlen:.6f}, y={bb.ylen:.6f}, z={bb.zlen:.6f}")
        print(f"Volume: {result.val().Volume():.10f}")
        print(f"Faces: {result.faces().size()}")
        print(f"Edges: {result.edges().size()}")
        print(f"Vertices: {result.vertices().size()}")
        print(f"Cylindrical faces: {result.faces('%Cylinder').size()}")
        print(f"Planar faces: {result.faces('%Plane').size()}")
    
        center = cq.Shape.centerOfMass(result.val())
        print(f"Center of mass: ({center.x:.6f}, {center.y:.6f}, {center.z:.6f})")
    
        # Bounding box checks
        assert abs(bb.xlen - length) < TOL, f"X length: expected {length}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, f"Y width: expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - height) < TOL, f"Z height: expected {height}, got {bb.zlen}"
    
        # Volume: rounded rectangle area × width
        # Area of rounded rect = length*height - 4*(r² - π*r²/4) = length*height - r²*(4 - π)
        rounded_rect_area = length * height - fillet_r**2 * (4 - math.pi)
        expected_vol = rounded_rect_area * width
        actual_vol = result.val().Volume()
    
        print(f"\nExpected volume: {expected_vol:.10f}")
        print(f"Actual volume:   {actual_vol:.10f}")
    
        assert actual_vol > 0, f"Volume should be positive"
        vol_tol = 0.001  # 0.1% absolute tolerance
        assert abs(actual_vol - expected_vol) < vol_tol, \
            f"Volume mismatch: expected {expected_vol:.8f}, got {actual_vol:.8f}"
    
        # Should have cylindrical faces (4 corner arcs extruded)
        cyl_faces = result.faces('%Cylinder').size()
        assert cyl_faces >= 4, f"Expected at least 4 cylindrical faces, got {cyl_faces}"
    
        # Center of mass at origin
        assert abs(center.x) < TOL, f"Center X should be ~0, got {center.x}"
        assert abs(center.y) < TOL, f"Center Y should be ~0, got {center.y}"
        assert abs(center.z) < TOL, f"Center Z should be ~0, got {center.z}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681463/gpt_generated.stl')
