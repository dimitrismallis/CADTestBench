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
        rect_w = 60.0    # rectangle width (X)
        rect_h = 40.0    # rectangle height (Y)
        tri_h  = 20.0    # triangle height above rectangle
        cut    = 10.0    # corner cutout size
        ext    = 5.0     # extrusion depth
    
        # --- Step 1: Define the 2D profile vertices ---
        # Shape: rectangle + triangle on top + corner cutouts at bottom
        # Vertices listed counterclockwise (CadQuery convention):
        #   (0, cut)         bottom-left after cutout
        #   (cut, 0)         bottom-left cutout diagonal end
        #   (rect_w-cut, 0)  bottom-right cutout diagonal start
        #   (rect_w, cut)    bottom-right after cutout
        #   (rect_w, rect_h) top-right of rectangle
        #   (rect_w/2, rect_h+tri_h)  triangle apex
        #   (0, rect_h)      top-left of rectangle
    
        pts = [
            (0,           cut),
            (cut,         0),
            (rect_w-cut,  0),
            (rect_w,      cut),
            (rect_w,      rect_h),
            (rect_w/2,    rect_h + tri_h),
            (0,           rect_h),
        ]
    
        # --- Step 2: Build the closed wire profile using lineTo ---
        wire = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .lineTo(pts[4][0], pts[4][1])
            .lineTo(pts[5][0], pts[5][1])
            .lineTo(pts[6][0], pts[6][1])
            .close()
        )
    
        # --- Step 3: Extrude the profile ---
        result = wire.extrude(ext)
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
        assert abs(bb.xlen - rect_w) < TOL, f"X extent: expected {rect_w}, got {bb.xlen}"
        assert abs(bb.ylen - (rect_h + tri_h)) < TOL, f"Y extent: expected {rect_h + tri_h}, got {bb.ylen}"
        assert abs(bb.zlen - ext) < TOL, f"Z extent (extrusion): expected {ext}, got {bb.zlen}"
    
        # Bounding box position
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.xmax - rect_w) < TOL, f"xmax: expected {rect_w}, got {bb.xmax}"
        assert abs(bb.ymax - (rect_h + tri_h)) < TOL, f"ymax: expected {rect_h + tri_h}, got {bb.ymax}"
        assert abs(bb.zmax - ext) < TOL, f"zmax: expected {ext}, got {bb.zmax}"
    
        # Volume check:
        # Full rectangle area = rect_w * rect_h = 60 * 40 = 2400
        # Triangle area = 0.5 * rect_w * tri_h = 0.5 * 60 * 20 = 600
        # Two corner cutouts (right triangles, legs = cut): 2 * 0.5 * cut * cut = cut^2 = 100
        # Net 2D area = 2400 + 600 - 100 = 2900
        rect_area   = rect_w * rect_h
        tri_area    = 0.5 * rect_w * tri_h
        cutout_area = 2 * (0.5 * cut * cut)
        net_area    = rect_area + tri_area - cutout_area
        expected_vol = net_area * ext
        actual_vol   = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Face count: 
        # Bottom face (1) + Top face (1) + 7 side faces (one per edge) = 9 total
        n_faces = result.faces().size()
        assert n_faces == 9, f"Face count: expected 9, got {n_faces}"
    
        # Edge count:
        # Top and bottom each have 7 edges = 14
        # 7 vertical side edges = 7
        # Total = 21
        n_edges = result.edges().size()
        assert n_edges == 21, f"Edge count: expected 21, got {n_edges}"
    
        # Vertex count: 7 top + 7 bottom = 14
        n_verts = result.vertices().size()
        assert n_verts == 14, f"Vertex count: expected 14, got {n_verts}"
    
        # Symmetry: center of mass should be at x = rect_w/2 (symmetric about x=30)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - rect_w / 2) < TOL, f"CoM X symmetry: expected {rect_w/2}, got {com.x}"
    
        # A point well inside the body should be inside
        interior = (rect_w/2, rect_h/2, ext/2)
        assert result.val().isInside(interior), \
            f"Interior point {interior} should be inside the solid"
    
        # A point just above the apex should be outside the solid
        above_apex = (rect_w/2, rect_h + tri_h + 1.0, ext/2)
        assert not result.val().isInside(above_apex), \
            f"Point above apex {above_apex} should be outside the solid"
    
        # Corner cutout check: the original bottom-left corner (0,0) should NOT be inside
        # Use a point clearly inside the cut triangle region
        corner_bl = (1.0, 1.0, ext/2)
        assert not result.val().isInside(corner_bl, tolerance=0.1), \
            f"Bottom-left corner region should be cut out"
    
        corner_br = (rect_w - 1.0, 1.0, ext/2)
        assert not result.val().isInside(corner_br, tolerance=0.1), \
            f"Bottom-right corner region should be cut out"
    
        # A point in the triangle region (above rectangle) should be inside
        tri_interior = (rect_w/2, rect_h + tri_h * 0.3, ext/2)
        assert result.val().isInside(tri_interior), \
            f"Triangle interior point {tri_interior} should be inside the solid"
    
        # A point outside the triangle (same height but far to the side) should be outside
        tri_outside = (rect_w * 0.95, rect_h + tri_h * 0.5, ext/2)
        assert not result.val().isInside(tri_outside), \
            f"Point outside triangle {tri_outside} should be outside the solid"
    
        print(f"All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f}")
        print(f"  Volume: {actual_vol:.2f} (expected {expected_vol:.2f})")
        print(f"  Faces: {n_faces}, Edges: {n_edges}, Vertices: {n_verts}")
        print(f"  Center of mass: ({com.x:.2f}, {com.y:.2f}, {com.z:.2f})")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997616/gpt_generated.stl')
