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
        rect_width  = 0.985934   # X dimension of the sketch rectangle
        rect_height = 1.39258    # Y dimension of the sketch rectangle (= extrusion depth in original description)
        extrude_depth = 0.043025 # Z extrusion depth
    
        # Cut parameters
        # top_edge_length = rect_height - 1.19693
        top_edge_length = rect_height - 1.19693   # = 0.19565
        # cut_width from each side = (rect_width - 0.563939) / 2
        cut_width = (rect_width - 0.563939) / 2   # = 0.210998 (approx)
    
        # The vertical level where the diagonal cut starts (from bottom)
        cut_y = rect_height - (rect_height - 1.19693)  # = 1.19693
        # Actually cut_y is the Y coordinate where the diagonal meets the side edge
        cut_y = 1.19693
    
        # --- Step 1: Build the hexagonal profile as a closed wire ---
        # Vertices of the irregular hexagon (centered at origin for CadQuery):
        # We'll define in absolute coords first, then center
        # Bottom-left: (0, 0)
        # Bottom-right: (rect_width, 0)
        # Right side up: (rect_width, cut_y)
        # Top-right cut: (rect_width - cut_width, rect_height)
        # Top-left cut: (cut_width, rect_height)
        # Left side up: (0, cut_y)
    
        # Center the polygon at origin
        cx = rect_width / 2
        cy = rect_height / 2
    
        pts = [
            (0 - cx,          0 - cy),
            (rect_width - cx, 0 - cy),
            (rect_width - cx, cut_y - cy),
            (rect_width - cut_width - cx, rect_height - cy),
            (cut_width - cx,  rect_height - cy),
            (0 - cx,          cut_y - cy),
        ]
    
        # --- Step 2: Create the hexagonal sketch and extrude ---
        result = (
            cq.Workplane("XY")
            .polyline(pts)
            .close()
            .extrude(extrude_depth)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - rect_width) < TOL, \
            f"X (width): expected {rect_width}, got {bb.xlen}"
        assert abs(bb.ylen - rect_height) < TOL, \
            f"Y (height): expected {rect_height}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_depth) < TOL, \
            f"Z (extrude): expected {extrude_depth}, got {bb.zlen}"
    
        # Volume check
        # Hexagon area = rectangle area - 2 corner triangles
        # Each triangle: base = cut_width, height = (rect_height - cut_y) = top_edge_height
        top_edge_height = rect_height - cut_y   # = 0.19565
        triangle_area = 0.5 * cut_width * top_edge_height
        hex_area = rect_width * rect_height - 2 * triangle_area
        expected_vol = hex_area * extrude_depth
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: hexagonal prism has 8 faces (2 hex faces + 6 side faces)
        face_count = result.faces().size()
        assert face_count == 8, f"Face count: expected 8, got {face_count}"
    
        # Top and bottom faces exist
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces == 1, f"Top face count: expected 1, got {top_faces}"
        assert bot_faces == 1, f"Bottom face count: expected 1, got {bot_faces}"
    
        # Check that the top edge (in Y direction) has the correct length
        # The top edge should be: rect_width - 2*cut_width = 0.563939 (approx)
        expected_top_edge = rect_width - 2 * cut_width
        assert abs(expected_top_edge - 0.563939) < TOL, \
            f"Top edge length: expected ~0.563939, got {expected_top_edge}"
    
        # Verify the solid is not inside a point that was cut (top-left corner)
        top_left_corner = cq.Vector(bb.xmin + 0.01, bb.ymax - 0.01, bb.zmin + extrude_depth/2)
        assert not result.val().isInside(top_left_corner), \
            "Top-left corner should have been cut off but point is inside solid"
    
        # Verify center of solid is inside
        center = cq.Vector(0, 0, extrude_depth / 2)
        assert result.val().isInside(center), \
            "Center of solid should be inside"
    
        print(f"All assertions passed!")
        print(f"  BBox: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00681547/gpt_generated.stl')
