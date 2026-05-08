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
        rect_w = 120.0      # length of rectangle (X direction)
        rect_h = 60.0       # width of rectangle (Y direction)
        cut = 15.0          # corner triangle leg length
        top_thick = 5.0     # tabletop thickness
        hex_r = 25.0        # hexagon circumradius (vertex-to-center)
        leg_len = 60.0      # leg extrusion length
    
        half_w = rect_w / 2   # 60
        half_h = rect_h / 2   # 30
    
        # Hexagon centers: place so outermost vertex aligns with tabletop end (x = ±half_w)
        # polygon(6, diam) in CadQuery places first vertex at angle 0 → (hex_r, 0) from center
        # So hex extends to hex_cx + hex_r in X → set hex_cx = half_w - hex_r
        hex_cx = half_w - hex_r   # = 60 - 25 = 35
    
        # --- Step 1: Build octagonal profile ---
        # Rectangle corners at (±60, ±30), cut right-angle triangles (legs=cut) from each corner
        pts = [
            ( half_w - cut,  half_h),       # top edge, right side
            ( half_w,  half_h - cut),       # right edge, top side
            ( half_w, -(half_h - cut)),     # right edge, bottom side
            ( half_w - cut, -half_h),       # bottom edge, right side
            (-(half_w - cut), -half_h),     # bottom edge, left side
            (-half_w, -(half_h - cut)),     # left edge, bottom side
            (-half_w,  half_h - cut),       # left edge, top side
            (-(half_w - cut),  half_h),     # top edge, left side
        ]
    
        # --- Step 2: Extrude octagonal tabletop ---
        tabletop = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(top_thick)
        )
    
        # --- Step 3: Draw hexagons on top face and extrude as legs ---
        # Hexagons centered at (±hex_cx, 0) on the top face, extruded upward (legs)
        result = (
            tabletop
            .faces(">Z")
            .workplane()
            .pushPoints([(hex_cx, 0), (-hex_cx, 0)])
            .polygon(6, hex_r * 2)   # diameter = 2 * circumradius
            .extrude(leg_len)
        )
    
        # --- Final object verification ---
        TOL = 0.5
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box checks
        # X: tabletop spans ±half_w = ±60, hex outermost vertex at ±(hex_cx + hex_r) = ±60
        assert abs(bb.xlen - rect_w) < TOL, \
            f"X length: expected {rect_w}, got {bb.xlen}"
    
        # Y: tabletop spans ±half_h = ±30; hex extends ±hex_r*sin(60°) ≈ ±21.65 in Y
        assert abs(bb.ylen - rect_h) < TOL, \
            f"Y length: expected {rect_h}, got {bb.ylen}"
    
        # Z: tabletop (5) + legs (60) = 65
        expected_zlen = top_thick + leg_len
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"Z length: expected {expected_zlen}, got {bb.zlen}"
    
        # Check bounding box Z extents
        assert abs(bb.zmin - 0) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Z max: expected {expected_zlen}, got {bb.zmax}"
    
        # Volume check
        # Octagon area: rect area - 4 corner right-angle triangles
        oct_area = rect_w * rect_h - 4 * 0.5 * cut * cut
        tabletop_vol = oct_area * top_thick
    
        # Hexagon area: (3*sqrt(3)/2) * r^2 where r is circumradius
        hex_area = (3 * math.sqrt(3) / 2) * hex_r ** 2
        # Subtract overlap: where hex base intersects tabletop (hex base is on top face)
        # The hex base is fully within the tabletop top face, so no subtraction needed for volume
        # But the extrusion adds on top of the tabletop
        legs_vol = 2 * hex_area * leg_len
    
        expected_vol = tabletop_vol + legs_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # Check number of solids
        solids_count = result.solids().size()
        assert solids_count >= 1, f"Expected at least 1 solid, got {solids_count}"
    
        # Check planar faces exist (octagon has 8 sides + top + bottom + 2 hex tops + 12 hex sides)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 10, \
            f"Expected at least 10 planar faces, got {planar_faces}"
    
        # Check symmetry: center of mass should be near x=0, y=0
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
        assert abs(com.y) < TOL, f"Center of mass Y: expected ~0, got {com.y}"
    
        # Check that the top of the model is at z = top_thick + leg_len = 65
        assert abs(bb.zmax - expected_zlen) < TOL, \
            f"Top Z: expected {expected_zlen}, got {bb.zmax}"
    
        # Verify hex center positions are symmetric
        assert abs(hex_cx - (half_w - hex_r)) < TOL, \
            f"Hex center X: expected {half_w - hex_r}, got {hex_cx}"
    
        # Verify hex outermost vertex aligns with tabletop end
        hex_max_x = hex_cx + hex_r
        assert abs(hex_max_x - half_w) < TOL, \
            f"Hex max X: expected {half_w}, got {hex_max_x}"
    
        print(f"✓ Bounding box: {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f}")
        print(f"✓ Volume: {actual_vol:.1f} (expected ~{expected_vol:.1f})")
        print(f"✓ Planar faces: {planar_faces}")
        print(f"✓ Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
        print(f"✓ Hex center X: ±{hex_cx:.1f}, hex max X: ±{hex_max_x:.1f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998698/gpt_generated.stl')
