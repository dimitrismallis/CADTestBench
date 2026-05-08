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
        R = 10.0        # radius of each lobe circle
        extrude_h = 5.0 # extrusion height
    
        # Heart shape construction:
        # Two circles of radius R:
        #   Left circle center:  (-R/2, 0)
        #   Right circle center: ( R/2, 0)
        # The top of the left circle is at (-R/2, R)
        # The top of the right circle is at (R/2, R)
        # They meet at the top center (0, 0) and at the bottom apex (0, -H)
        #
        # Strategy: use two semicircular arcs for the lobes, 
        # and two straight lines going down to the apex.
        #
        # Left lobe arc: from (0, 0) going left and up, through (-R, 0), back to (-R/2, -R*sin60)
        # This is complex — instead use a well-known parametric heart:
        #
        # Heart via two arcs + two lines:
        # Right lobe: arc from (0, 0) through (R, R) to (0, 2*R)  -- wait, let me think more carefully.
        #
        # Classic approach:
        # - Right lobe: circle center (R/2, R/2), radius = R/2*sqrt(2)... 
        #
        # Simplest robust approach: 
        # Use two circles of radius R centered at (-R, 0) and (R, 0).
        # The heart outline = union of two circles + a triangle pointing down.
        # But in wire form:
        #
        # Points on the heart:
        #   Top-left arc: center (-R, 0), from angle 0 to 180 deg (top semicircle)
        #     start: (-R+R, 0) = (0, 0)  [rightmost point of left circle]
        #     end:   (-R-R, 0) = (-2R, 0) [leftmost point]
        #     mid (top): (-R, R)
        #   Top-right arc: center (R, 0), from 180 to 360 deg
        #     start: (R-R, 0) = (0, 0) [leftmost point of right circle]  
        #     end:   (R+R, 0) = (2R, 0) [rightmost point]
        #     mid (top): (R, R)
        #
        # Actually let me use a cleaner decomposition:
        # Right lobe: arc from (0,0) through (R, R) to (2R, 0)  [top semicircle of right circle]
        # Left lobe:  arc from (-2R, 0) through (-R, R) to (0, 0) [top semicircle of left circle]
        # Bottom: lines from (2R, 0) down to apex (0, -2R) and from (0,-2R) up to (-2R, 0)
        #
        # This gives a heart shape!
    
        # Scale factor
        S = R  # so R=10 means the heart spans from -2R to 2R in X = -20 to 20
    
        # Key points:
        # Right arc: (0,0) -> mid(R, R) -> (2R, 0)   [right lobe top]
        # Line: (2R, 0) -> (0, -2R)                   [right side going to apex]
        # Line: (0, -2R) -> (-2R, 0)                  [left side going from apex]
        # Left arc: (-2R, 0) -> mid(-R, R) -> (0, 0)  [left lobe top]
    
        # --- Step 1: Build heart 2D profile ---
        heart = (
            cq.Workplane("XY")
            .moveTo(0, 0)
            .threePointArc((S, S), (2*S, 0))       # right lobe arc
            .lineTo(0, -2*S)                         # right side to apex
            .lineTo(-2*S, 0)                         # left side from apex
            .threePointArc((-S, S), (0, 0))          # left lobe arc
            .close()
        )
    
        # --- Step 2: Extrude the heart profile ---
        result = heart.extrude(extrude_h)
    
        # --- Final object verification ---
        TOL = 0.5  # generous tolerance for curved geometry
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # X span: from -2R to 2R = -20 to 20, so xlen = 4R = 40
        expected_xlen = 4 * S
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"X length: expected {expected_xlen}, got {bb.xlen}"
    
        # Y span: from -2R to R (top of arc) = from -20 to 10, so ylen = 3R = 30
        # Top of arc: the arc goes through (R, R) so max Y = R = 10
        # Bottom: -2R = -20
        expected_ylen = 3 * S
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"Y length: expected {expected_ylen}, got {bb.ylen}"
    
        # Z span: 0 to extrude_h
        assert abs(bb.zlen - extrude_h) < TOL, \
            f"Z length: expected {extrude_h}, got {bb.zlen}"
    
        # Z min should be 0 (base on XY plane)
        assert abs(bb.zmin) < TOL, f"Z min: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - extrude_h) < TOL, f"Z max: expected {extrude_h}, got {bb.zmax}"
    
        # Volume check: approximate area of heart * height
        # Heart area ≈ area of two semicircles (radius R each) + area of triangle base
        # Two semicircles of radius R = pi*R^2
        # Triangle: base = 4R, height = 2R, area = 0.5 * 4R * 2R = 4R^2
        # But the triangle is not a right triangle from (-2R,0) to (2R,0) to (0,-2R)
        # Triangle area = 0.5 * base * height = 0.5 * 4R * 2R = 4R^2
        # Total 2D area ≈ pi*R^2 + 4*R^2
        approx_area = math.pi * S**2 + 4 * S**2
        approx_vol = approx_area * extrude_h
        actual_vol = result.val().Volume()
        # Allow 10% tolerance since the arcs aren't perfect semicircles
        assert abs(actual_vol - approx_vol) / approx_vol < 0.15, \
            f"Volume: expected ~{approx_vol:.1f}, got {actual_vol:.1f}"
    
        # Face count: 
        # - 1 bottom face (flat, on XY plane)
        # - 1 top face (flat, parallel to XY)
        # - Side faces: 2 curved (from arcs) + 2 flat (from lines) = 4 side faces
        # Total = 6 faces
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Check there are exactly 2 cylindrical faces (from the two arc extrusions)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 2, f"Cylindrical faces: expected 2, got {cyl_faces}"
    
        # Check there are exactly 4 planar faces (top, bottom, 2 side triangles)
        plane_faces = result.faces("%Plane").size()
        assert plane_faces == 4, f"Planar faces: expected 4, got {plane_faces}"
    
        # Check the solid is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check center of mass is roughly at x=0 (symmetric about YZ plane)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"Center of mass X: expected ~0, got {com.x}"
    
        # Check the solid contains a point in the middle of the heart
        mid_point = (0, 0, extrude_h / 2)
        assert result.val().isInside(mid_point), \
            f"Point {mid_point} should be inside the heart solid"
    
        # Check the solid does NOT contain a point far outside
        outside_point = (3*S, 3*S, extrude_h / 2)
        assert not result.val().isInside(outside_point), \
            f"Point {outside_point} should be outside the heart solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"Volume: {actual_vol:.2f} (approx expected: {approx_vol:.2f})")
        print(f"Faces: {face_count}, Cylindrical: {cyl_faces}, Planar: {plane_faces}")
        print(f"Center of mass: ({com.x:.3f}, {com.y:.3f}, {com.z:.3f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00857821/gpt_generated.stl')
