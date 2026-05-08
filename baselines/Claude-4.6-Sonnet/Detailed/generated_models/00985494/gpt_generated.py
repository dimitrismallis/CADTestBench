import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        base_len = 0.495408    # bottom length of trapezoid
        top_len  = 0.148743    # top length of trapezoid
        trap_h   = 0.233091    # height of trapezoid (in Z)
        width    = 0.744939    # extrusion width (in Y)
    
        # --- Step 1: Draw the isosceles trapezoid profile on the XZ plane ---
        # Vertices (centered about X=0):
        #   Bottom-left:  (-base_len/2, 0)
        #   Bottom-right: ( base_len/2, 0)
        #   Top-right:    ( top_len/2,  trap_h)
        #   Top-left:     (-top_len/2,  trap_h)
        # On XZ plane: x -> X, y -> Z
    
        half_base = base_len / 2.0
        half_top  = top_len  / 2.0
    
        trap_profile = (
            cq.Workplane("XZ")
            .moveTo(-half_base, 0)
            .lineTo( half_base, 0)
            .lineTo( half_top,  trap_h)
            .lineTo(-half_top,  trap_h)
            .close()
        )
    
        # --- Step 2: Extrude along Y (centered) ---
        # On XZ plane, extrude goes in Y direction
        # centered=True for the extrusion means it goes ±width/2 in Y
        result = trap_profile.extrude(width / 2.0, both=True)
    
        # --- Final object verification ---
        TOL = 1e-4
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - base_len) < TOL, \
            f"X length (base): expected {base_len}, got {bb.xlen}"
        assert abs(bb.ylen - width) < TOL, \
            f"Y length (width): expected {width}, got {bb.ylen}"
        assert abs(bb.zlen - trap_h) < TOL, \
            f"Z length (trap height): expected {trap_h}, got {bb.zlen}"
    
        # Centering checks
        center = result.val().Center()
        assert abs(center.x) < TOL, \
            f"Center X should be 0, got {center.x}"
        assert abs(center.y) < TOL, \
            f"Center Y should be 0, got {center.y}"
    
        # Volume check: trapezoid area * width
        trap_area = 0.5 * (base_len + top_len) * trap_h
        expected_vol = trap_area * width
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 1e-4, \
            f"Volume: expected {expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Face count: a trapezoid prism has 6 faces
        # (2 trapezoidal end faces + 4 rectangular side faces)
        face_count = result.faces().size()
        assert face_count == 6, \
            f"Face count: expected 6, got {face_count}"
    
        # Edge count: 12 edges for a prism with quadrilateral cross-section
        edge_count = result.edges().size()
        assert edge_count == 12, \
            f"Edge count: expected 12, got {edge_count}"
    
        # Vertex count: 8 vertices
        vertex_count = result.vertices().size()
        assert vertex_count == 8, \
            f"Vertex count: expected 8, got {vertex_count}"
    
        # Check that the bottom face is at Z=0 and top face at Z=trap_h
        assert abs(bb.zmin - 0.0) < TOL, \
            f"Z min should be 0, got {bb.zmin}"
        assert abs(bb.zmax - trap_h) < TOL, \
            f"Z max should be {trap_h}, got {bb.zmax}"
    
        # Check Y centering
        assert abs(bb.ymin + width/2) < TOL, \
            f"Y min should be {-width/2}, got {bb.ymin}"
        assert abs(bb.ymax - width/2) < TOL, \
            f"Y max should be {width/2}, got {bb.ymax}"
    
        # Check X centering
        assert abs(bb.xmin + base_len/2) < TOL, \
            f"X min should be {-base_len/2}, got {bb.xmin}"
        assert abs(bb.xmax - base_len/2) < TOL, \
            f"X max should be {base_len/2}, got {bb.xmax}"
    
        # Verify the top face is narrower than the bottom face
        # Top face (max Z) should have xlen = top_len
        top_face_bb = result.faces(">Z").val().BoundingBox()
        assert abs(top_face_bb.xlen - top_len) < TOL, \
            f"Top face X length: expected {top_len}, got {top_face_bb.xlen}"
    
        # Bottom face (min Z) should have xlen = base_len
        bot_face_bb = result.faces("<Z").val().BoundingBox()
        assert abs(bot_face_bb.xlen - base_len) < TOL, \
            f"Bottom face X length: expected {base_len}, got {bot_face_bb.xlen}"
    
        print("All assertions passed!")
        print(f"  Bounding box: {bb.xlen:.6f} x {bb.ylen:.6f} x {bb.zlen:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Faces: {face_count}, Edges: {edge_count}, Vertices: {vertex_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00985494/gpt_generated.stl')
