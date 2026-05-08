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
        extrude_length  = 0.75
        mid_length      = 0.234841
        bottom_length   = 0.11742
        mid_height      = 0.280088   # not directly used in vertex coords but defined
        top_height      = 0.204477
        bottom_height   = 0.279461
        mid_shift       = 0.004644
        bottom_shift    = 0.002349
    
        # --- Step 1: Compute pentagon vertices ---
        # Top vertex
        top       = (0,                                  top_height)
        # Middle left
        mid_left  = (-mid_length/2 + mid_shift,          0)
        # Bottom left
        bot_left  = (-bottom_length/2 + bottom_shift,   -bottom_height)
        # Bottom right
        bot_right = ( bottom_length/2 + bottom_shift,   -bottom_height)
        # Middle right
        mid_right = ( mid_length/2 + mid_shift,          0)
    
        # Order: top -> mid_right -> bot_right -> bot_left -> mid_left -> close
        pts = [top, mid_right, bot_right, bot_left, mid_left]
    
        # --- Step 2: Build the pentagon profile and extrude ---
        # Use moveTo + lineTo to draw the closed pentagon wire, then extrude
        result = (
            cq.Workplane("XY")
            .moveTo(*pts[0])
            .lineTo(*pts[1])
            .lineTo(*pts[2])
            .lineTo(*pts[3])
            .lineTo(*pts[4])
            .close()
            .extrude(extrude_length)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box X: from min(all x coords) to max(all x coords)
        all_x = [p[0] for p in pts]
        all_y = [p[1] for p in pts]
        expected_xmin = min(all_x)
        expected_xmax = max(all_x)
        expected_ymin = min(all_y)
        expected_ymax = max(all_y)
        expected_xlen = expected_xmax - expected_xmin
        expected_ylen = expected_ymax - expected_ymin
        expected_zlen = extrude_length
    
        assert abs(bb.xlen - expected_xlen) < TOL, \
            f"BBox X length: expected {expected_xlen:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - expected_ylen) < TOL, \
            f"BBox Y length: expected {expected_ylen:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z length: expected {expected_zlen:.6f}, got {bb.zlen:.6f}"
    
        # Z extents: extrude goes from 0 to extrude_length
        assert abs(bb.zmin - 0.0) < TOL, \
            f"BBox zmin: expected 0.0, got {bb.zmin:.6f}"
        assert abs(bb.zmax - extrude_length) < TOL, \
            f"BBox zmax: expected {extrude_length:.6f}, got {bb.zmax:.6f}"
    
        # Face count: a pentagonal prism has 7 faces (2 pentagons + 5 rectangles)
        n_faces = result.faces().size()
        assert n_faces == 7, f"Face count: expected 7, got {n_faces}"
    
        # Edge count: a pentagonal prism has 15 edges (5 top + 5 bottom + 5 vertical)
        n_edges = result.edges().size()
        assert n_edges == 15, f"Edge count: expected 15, got {n_edges}"
    
        # Vertex count: a pentagonal prism has 10 vertices
        n_verts = result.vertices().size()
        assert n_verts == 10, f"Vertex count: expected 10, got {n_verts}"
    
        # Volume: area of pentagon × extrude_length
        # Compute area using shoelace formula
        def shoelace(pts_list):
            n = len(pts_list)
            area = 0.0
            for i in range(n):
                x1, y1 = pts_list[i]
                x2, y2 = pts_list[(i+1) % n]
                area += x1 * y2 - x2 * y1
            return abs(area) / 2.0
    
        pent_area = shoelace(pts)
        expected_vol = pent_area * extrude_length
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Bottom edge length (shortest edge): distance between bot_left and bot_right
        bottom_edge_len = math.sqrt((bot_right[0] - bot_left[0])**2 + (bot_right[1] - bot_left[1])**2)
        expected_bottom_edge = bottom_length  # since both y coords are equal, it's just the x difference
        assert abs(bottom_edge_len - expected_bottom_edge) < TOL, \
            f"Bottom edge length: expected {expected_bottom_edge:.6f}, got {bottom_edge_len:.6f}"
    
        # Check the bottom edge is indeed the shortest horizontal edge
        # bot_left x = -bottom_length/2 + bottom_shift, bot_right x = bottom_length/2 + bottom_shift
        # difference = bottom_length = 0.11742
        computed_bottom = (bottom_length/2 + bottom_shift) - (-bottom_length/2 + bottom_shift)
        assert abs(computed_bottom - bottom_length) < TOL, \
            f"Bottom edge computed: expected {bottom_length:.6f}, got {computed_bottom:.6f}"
    
        # Planar faces: all 7 faces of a prism are planar
        n_planar = result.faces("%Plane").size()
        assert n_planar == 7, f"Planar face count: expected 7, got {n_planar}"
    
        print("All assertions passed!")
        print(f"  BBox: x=[{bb.xmin:.4f}, {bb.xmax:.4f}], y=[{bb.ymin:.4f}, {bb.ymax:.4f}], z=[{bb.zmin:.4f}, {bb.zmax:.4f}]")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {n_faces}, Edges: {n_edges}, Vertices: {n_verts}")
        print(f"  Bottom edge length: {bottom_edge_len:.6f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998398/gpt_generated.stl')
