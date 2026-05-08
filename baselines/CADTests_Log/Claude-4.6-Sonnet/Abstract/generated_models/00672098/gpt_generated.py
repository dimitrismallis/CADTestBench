import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_width   = 60.0   # total width of the U
        outer_height  = 40.0   # total height of the U
        wall_thick    = 10.0   # thickness of left/right arms and bottom bar
        extrude_depth =  5.0   # small extrusion depth (Z)
    
        # Derived dimensions
        inner_width  = outer_width  - 2 * wall_thick   # 40 mm  (notch width)
        inner_height = outer_height - wall_thick        # 30 mm  (notch depth from top)
    
        hw = outer_width  / 2   # 30  (half outer width)
        hh = outer_height / 2   # 20  (half outer height)
        iw = inner_width  / 2   # 20  (half inner width)
        ih = inner_height        # 30  (notch depth)
    
        # --- Step 1: Define the 8-vertex U-profile (CCW, centered at origin) ---
        #
        #   7----2
        #   |    |
        #   6  3 |   <- top of arms
        #   |  | |
        #   5  4 |   <- inner bottom (hh - ih = -10)
        #   |    |
        #   0----1   <- bottom
        #
        pts = [
            (-hw, -hh),        # 0: bottom-left
            ( hw, -hh),        # 1: bottom-right
            ( hw,  hh),        # 2: top-right outer
            ( iw,  hh),        # 3: top-right inner (step left)
            ( iw,  hh - ih),   # 4: inner bottom-right  (= -10)
            (-iw,  hh - ih),   # 5: inner bottom-left   (= -10)
            (-iw,  hh),        # 6: top-left inner (step right)
            (-hw,  hh),        # 7: top-left outer
        ]
    
        # --- Step 2: Build the closed wire and extrude ---
        result = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .lineTo(*pts[5])
            .lineTo(*pts[6])
            .lineTo(*pts[7])
            .close()
            .extrude(extrude_depth)
        )
    
        # -----------------------------------------------------------------------
        # --- Final object verification ---
        # -----------------------------------------------------------------------
        TOL = 0.01
        solid = result.val()
    
        # 1. Bounding box dimensions
        bb = solid.BoundingBox()
        assert abs(bb.xlen - outer_width)   < TOL, \
            f"X extent: expected {outer_width}, got {bb.xlen}"
        assert abs(bb.ylen - outer_height)  < TOL, \
            f"Y extent: expected {outer_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z extent: expected {extrude_depth}, got {bb.zlen}"
    
        # 2. Volume: (outer rect - inner notch) × depth
        outer_area   = outer_width * outer_height   # 60 × 40 = 2400
        inner_area   = inner_width * inner_height   # 40 × 30 = 1200
        expected_vol = (outer_area - inner_area) * extrude_depth  # 6000
        actual_vol   = solid.Volume()
        assert abs(actual_vol - expected_vol) < 1.0, \
            f"Volume: expected {expected_vol}, got {actual_vol:.4f}"
    
        # 3. Face count: 2 flat (top/bottom) + 8 side faces = 10
        n_faces = result.faces().size()
        assert n_faces == 10, \
            f"Face count: expected 10, got {n_faces}"
    
        # 4. Exactly one top face and one bottom face
        assert result.faces(">Z").size() == 1, \
            "Should have exactly 1 top face (max Z)"
        assert result.faces("<Z").size() == 1, \
            "Should have exactly 1 bottom face (min Z)"
    
        # 5. Vertical edges (parallel to Z): 8 corners → 8 vertical edges
        n_vert_edges = result.edges("|Z").size()
        assert n_vert_edges == 8, \
            f"Vertical edges: expected 8, got {n_vert_edges}"
    
        # 6. Total edges: 8 top + 8 bottom + 8 vertical = 24
        n_edges = result.edges().size()
        assert n_edges == 24, \
            f"Edge count: expected 24, got {n_edges}"
    
        # 7. Total vertices: 8 top + 8 bottom = 16
        n_verts = result.vertices().size()
        assert n_verts == 16, \
            f"Vertex count: expected 16, got {n_verts}"
    
        # 8. Containment: point inside the bottom bar should be inside the solid
        bottom_bar_pt = (0.0, -hh + wall_thick / 2, extrude_depth / 2)
        assert solid.isInside(bottom_bar_pt), \
            f"Point {bottom_bar_pt} should be inside the bottom bar of the U"
    
        # 9. Containment: point inside the notch should be OUTSIDE the solid
        notch_pt = (0.0, hh - ih / 2, extrude_depth / 2)
        assert not solid.isInside(notch_pt), \
            f"Point {notch_pt} should be outside (inside the open notch of the U)"
    
        # 10. Symmetry: center of mass X should be 0 (left-right symmetric U)
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, \
            f"Center of mass X should be 0 (symmetric U), got {com.x:.6f}"
    
        # 11. Center of mass Z should be at mid-depth
        assert abs(com.z - extrude_depth / 2) < TOL, \
            f"Center of mass Z should be {extrude_depth/2}, got {com.z:.6f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00672098/gpt_generated.stl')
