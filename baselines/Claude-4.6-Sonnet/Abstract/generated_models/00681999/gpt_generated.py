import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        rect_w = 90.0    # rectangle width
        rect_h = 60.0    # rectangle height (~2/3 of width: 60/90 = 0.667)
        sq_size = 30.0   # square cutout size (~1/3 of rectangle: 30/90 = 0.333)
        depth = 10.0     # extrusion depth
    
        # --- Step 1: Define the 2D profile using a closed wire ---
        # Rectangle centered at origin: x in [-45, 45], y in [-30, 30]
        # Square cutout: x in [-15, 15], y in [0, 30]
        #   - top edge at y=30 (coincident with center of rectangle's top edge at (0,30))
        #   - bottom edge at y=0 (center of rectangle)
        #
        # We'll trace the outer profile as a single closed polygon (rectangle with notch cut out):
        # Starting from bottom-left corner, going clockwise:
        # (-45, -30) -> (45, -30) -> (45, 30) -> (15, 30) -> (15, 0) -> (-15, 0) -> (-15, 30) -> (-45, 30) -> (-45, -30)
    
        pts = [
            (-45, -30),  # bottom-left
            ( 45, -30),  # bottom-right
            ( 45,  30),  # top-right
            ( 15,  30),  # top-right of notch
            ( 15,   0),  # bottom-right of notch
            (-15,   0),  # bottom-left of notch
            (-15,  30),  # top-left of notch
            (-45,  30),  # top-left
        ]
    
        # Build the profile as a closed polyline
        profile = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .lineTo(pts[7][0], pts[7][1])
            .close()
        )
    
        # --- Step 2: Extrude the profile ---
        result = profile.extrude(depth)
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box should span the full rectangle dimensions
        assert abs(bb.xlen - rect_w) < TOL, f"X length: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - rect_h) < TOL, f"Y length: expected {rect_h}, got {bb.ylen}"
        assert abs(bb.zlen - depth) < TOL,  f"Z length: expected {depth}, got {bb.zlen}"
    
        # Bounding box extents
        assert abs(bb.xmin - (-45)) < TOL, f"xmin: expected -45, got {bb.xmin}"
        assert abs(bb.xmax -  45)   < TOL, f"xmax: expected 45, got {bb.xmax}"
        assert abs(bb.ymin - (-30)) < TOL, f"ymin: expected -30, got {bb.ymin}"
        assert abs(bb.ymax -  30)   < TOL, f"ymax: expected 30, got {bb.ymax}"
        assert abs(bb.zmin -   0)   < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - depth) < TOL, f"zmax: expected {depth}, got {bb.zmax}"
    
        # Volume: full rectangle area minus square cutout area, times depth
        full_area   = rect_w * rect_h          # 90 * 60 = 5400
        cutout_area = sq_size * sq_size        # 30 * 30 = 900
        profile_area = full_area - cutout_area # 4500
        expected_vol = profile_area * depth    # 45000
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) < 1.0, \
            f"Volume: expected {expected_vol}, got {actual_vol}"
    
        # The shape should have exactly 1 solid
        assert result.solids().size() == 1, \
            f"Solids: expected 1, got {result.solids().size()}"
    
        # Face count: the extruded notched profile should have:
        # - 2 flat faces (top and bottom, each is the notched profile)
        # - 8 side faces (one per edge of the 8-sided polygon)
        # Total = 10 faces
        n_faces = result.faces().size()
        assert n_faces == 10, f"Face count: expected 10, got {n_faces}"
    
        # Check the notch: a point inside the cutout region should NOT be inside the solid
        # Cutout region center: (0, 15, 5) — inside the square cutout at mid-depth
        cutout_center = (0, 15, 5)
        assert not result.val().isInside(cutout_center), \
            f"Point {cutout_center} should be outside (in the cutout), but is inside the solid"
    
        # Check a point clearly inside the solid (lower half of rectangle)
        solid_center = (0, -15, 5)
        assert result.val().isInside(solid_center), \
            f"Point {solid_center} should be inside the solid, but is not"
    
        # Check a point in the solid beside the notch (upper half, outside notch)
        beside_notch = (35, 15, 5)
        assert result.val().isInside(beside_notch), \
            f"Point {beside_notch} should be inside the solid, but is not"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681999/gpt_generated.stl')
