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
        side = 0.32592
        extrude_h = 0.023387
    
        # --- Step 1: Define the combined profile vertices ---
        # Square bottom-left at origin: (0,0), (side,0), (side,side), (0,side)
        # Triangle on top of square with right angle at (side, side):
        #   vertices: (0, side), (side, side), (side, 2*side)
        # Combined shape (square + triangle merged):
        #   (0, 0) -> (side, 0) -> (side, 2*side) -> (0, side) -> close
        # This is a quadrilateral (irregular rhombus)
    
        pts = [
            (0, 0),
            (side, 0),
            (side, 2 * side),
            (0, side),
        ]
    
        # --- Step 2: Create the 2D profile as a closed polygon ---
        result = (
            cq.Workplane("XY")
            .moveTo(pts[0][0], pts[0][1])
            .lineTo(pts[1][0], pts[1][1])
            .lineTo(pts[2][0], pts[2][1])
            .lineTo(pts[3][0], pts[3][1])
            .close()
            .extrude(extrude_h)
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - side) < TOL, f"X extent: expected {side}, got {bb.xlen}"
        assert abs(bb.ylen - 2 * side) < TOL, f"Y extent: expected {2*side}, got {bb.ylen}"
        assert abs(bb.zlen - extrude_h) < TOL, f"Z extent: expected {extrude_h}, got {bb.zlen}"
    
        # Bounding box origin checks
        assert abs(bb.xmin - 0) < TOL, f"xmin: expected 0, got {bb.xmin}"
        assert abs(bb.ymin - 0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.zmin - 0) < TOL, f"zmin: expected 0, got {bb.zmin}"
    
        # Volume check: area of quadrilateral * extrude_h
        # Quadrilateral vertices: (0,0), (side,0), (side,2*side), (0,side)
        # Area using shoelace formula:
        # A = 0.5 * |x0(y1-y3) + x1(y2-y0) + x2(y3-y1) + x3(y0-y2)|
        x = [0, side, side, 0]
        y = [0, 0, 2*side, side]
        n = len(x)
        area = 0.5 * abs(sum(x[i]*(y[(i+1)%n] - y[(i-1)%n]) for i in range(n)))
        expected_vol = area * extrude_h
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: 6 faces (2 flat end faces + 4 side faces for quadrilateral prism)
        face_count = result.faces().size()
        assert face_count == 6, f"Face count: expected 6, got {face_count}"
    
        # Edge count: 12 edges (4 top + 4 bottom + 4 vertical)
        edge_count = result.edges().size()
        assert edge_count == 12, f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, f"Vertex count: expected 8, got {vertex_count}"
    
        # Check the shape is a single solid
        solid_count = result.solids().size()
        assert solid_count == 1, f"Solid count: expected 1, got {solid_count}"
    
        # Check that the top face (max Z) is planar
        top_faces = result.faces(">Z")
        assert top_faces.size() == 1, f"Top face count: expected 1, got {top_faces.size()}"
    
        # Check the point (side/2, side/2, extrude_h/2) is inside the solid (center of square portion)
        center_pt = (side/2, side/2, extrude_h/2)
        assert result.val().isInside(center_pt), \
            f"Center point {center_pt} should be inside the solid"
    
        # Check that the point (side/2, 1.5*side, extrude_h/2) is inside (triangle portion center approx)
        # Triangle region: roughly around (side*0.75, side*1.25)
        tri_pt = (side * 0.8, side * 1.2, extrude_h / 2)
        assert result.val().isInside(tri_pt), \
            f"Triangle region point {tri_pt} should be inside the solid"
    
        print(f"All assertions passed!")
        print(f"Bounding box: {bb.xlen:.5f} x {bb.ylen:.5f} x {bb.zlen:.5f}")
        print(f"Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00672359/gpt_generated.stl')
