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
        W = 60.0    # main rectangle width (X)
        H = 40.0    # main rectangle height (Y)
        cw = 10.0   # corner cutout width (X)
        ch = 8.0    # corner cutout height (Y)
        ext = 5.0   # extrusion depth (Z)
    
        # --- Step 1: Draw the profile as a closed polygon ---
        # The main rectangle spans from (0,0) to (W,H).
        # Bottom-left corner cutout: remove (0,0)→(cw,ch) region
        # Bottom-right corner cutout: remove (W-cw,0)→(W,ch) region
        #
        # Vertices going counter-clockwise from bottom-left cutout corner:
        # (cw, 0) → (W-cw, 0) → (W-cw, ch) → (W, ch) → (W, H) → (0, H) → (0, ch) → (cw, ch) → close
        #
        # Shift so the shape is centered at origin in XY:
        ox = -W / 2
        oy = -H / 2
    
        result = (
            cq.Workplane("XY")
            .moveTo(ox + cw,      oy + 0)
            .lineTo(ox + W - cw,  oy + 0)
            .lineTo(ox + W - cw,  oy + ch)
            .lineTo(ox + W,       oy + ch)
            .lineTo(ox + W,       oy + H)
            .lineTo(ox + 0,       oy + H)
            .lineTo(ox + 0,       oy + ch)
            .lineTo(ox + cw,      oy + ch)
            .close()
            .extrude(ext)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        bb = result.val().BoundingBox()
    
        # Bounding box should still span the full W x H x ext
        assert abs(bb.xlen - W) < TOL, f"X length: expected {W}, got {bb.xlen}"
        assert abs(bb.ylen - H) < TOL, f"Y length: expected {H}, got {bb.ylen}"
        assert abs(bb.zlen - ext) < TOL, f"Z length: expected {ext}, got {bb.zlen}"
    
        # Volume: full rectangle minus two corner cutouts
        expected_vol = (W * H - 2 * cw * ch) * ext
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # The profile has 8 vertices → 8 edges on top and bottom faces → 8 vertical side faces
        # Total faces: 1 bottom + 1 top + 8 side faces = 10
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # All faces should be planar (no cylinders)
        planar_count = result.faces("%Plane").size()
        assert planar_count == 10, f"Planar face count: expected 10, got {planar_count}"
    
        # Check that the two bottom corners are indeed cut out (points inside cutouts should be outside the solid)
        solid = result.val()
        # Bottom-left cutout center (in world coords, z=ext/2)
        bl_cutout_center = (ox + cw/2, oy + ch/2, ext/2)
        assert not solid.isInside(bl_cutout_center), \
            f"Bottom-left cutout center should be outside the solid"
    
        # Bottom-right cutout center
        br_cutout_center = (ox + W - cw/2, oy + ch/2, ext/2)
        assert not solid.isInside(br_cutout_center), \
            f"Bottom-right cutout center should be outside the solid"
    
        # Center of the main body should be inside
        body_center = (0.0, 0.0, ext/2)
        assert solid.isInside(body_center), \
            f"Body center should be inside the solid"
    
        # Top center should be inside
        top_center = (0.0, oy + H - 5, ext/2)
        assert solid.isInside(top_center), \
            f"Top region center should be inside the solid"
    
        # Edge count: 8 edges on top + 8 edges on bottom + 8 vertical edges = 24
        edge_count = result.edges().size()
        assert edge_count == 24, f"Edge count: expected 24, got {edge_count}"
    
        # Vertex count: 8 top + 8 bottom = 16
        vertex_count = result.vertices().size()
        assert vertex_count == 16, f"Vertex count: expected 16, got {vertex_count}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00984234/gpt_generated.stl')
