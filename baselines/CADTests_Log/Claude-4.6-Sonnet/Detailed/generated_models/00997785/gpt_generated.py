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
        hex_side = 1.50001
        hex_height = 0.409382
        sq_side = 0.867904
        sq_height = 0.272921
    
        # --- Step 1: Draw and extrude the hexagonal base ---
        # polygon(6, diameter) uses circumradius = diameter/2 = side length for regular hex
        # CadQuery default orientation: flat top/bottom → xlen = 2*side, ylen = side*sqrt(3)
        hex_base = (
            cq.Workplane("XY")
            .polygon(6, 2 * hex_side)  # diameter = 2 * side length (circumradius = side)
            .extrude(hex_height)
        )
    
        # --- Step 2: Draw the square on top of the hexagon, rotated 45 degrees ---
        square_tier = (
            hex_base
            .faces(">Z")
            .workplane()
            .transformed(rotate=cq.Vector(0, 0, 45))
            .rect(sq_side, sq_side)
            .extrude(sq_height)
        )
    
        result = square_tier
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # CadQuery hexagon polygon(6, 2*s) default orientation:
        # flat edges top/bottom → xlen = 2*side (vertex-to-vertex), ylen = side*sqrt(3) (flat-to-flat)
        hex_xlen = 2 * hex_side          # vertex-to-vertex in X: 3.00002
        hex_ylen = hex_side * math.sqrt(3)  # flat-to-flat in Y: ~2.5981
    
        assert abs(bb.xlen - hex_xlen) < TOL, \
            f"BB xlen: expected ~{hex_xlen:.4f}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - hex_ylen) < TOL, \
            f"BB ylen: expected ~{hex_ylen:.4f}, got {bb.ylen:.4f}"
    
        # Total height = hex_height + sq_height
        total_height = hex_height + sq_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"BB zlen: expected ~{total_height:.4f}, got {bb.zlen:.4f}"
    
        # Volume check
        # Hexagon area = (3 * sqrt(3) / 2) * side^2
        hex_area = (3 * math.sqrt(3) / 2) * hex_side ** 2
        hex_vol = hex_area * hex_height
    
        # Square area = side^2
        sq_area = sq_side ** 2
        sq_vol = sq_area * sq_height
    
        expected_vol = hex_vol + sq_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.4f}, got {actual_vol:.4f}"
    
        # Face count check:
        # Hexagonal prism: 6 side faces + 1 bottom + 1 top (annular, with square hole) = 8
        # Square prism on top: 4 side faces + 1 top = 5
        # Total = 13 faces
        face_count = result.faces().size()
        print(f"Face count: {face_count}")
        assert face_count >= 12, f"Face count: expected >= 12, got {face_count}"
    
        # Check no cylindrical faces (no holes)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        # Check the bottom face is at z=0
        assert abs(bb.zmin) < TOL, f"Bottom z: expected 0, got {bb.zmin:.4f}"
    
        # Check top face is at correct height
        assert abs(bb.zmax - total_height) < TOL, \
            f"Top z: expected {total_height:.4f}, got {bb.zmax:.4f}"
    
        # Check center of mass is near x=0, y=0 (symmetric object)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x) < TOL, f"CoM x: expected ~0, got {com.x:.4f}"
        assert abs(com.y) < TOL, f"CoM y: expected ~0, got {com.y:.4f}"
    
        # Check the square tier top face exists at total_height
        top_faces = result.faces(">Z")
        assert top_faces.size() >= 1, "Should have at least one top face"
        top_bb = top_faces.val().BoundingBox()
        assert abs(top_bb.zmax - total_height) < TOL, \
            f"Top face z: expected {total_height:.4f}, got {top_bb.zmax:.4f}"
    
        # The square rotated 45° has diagonal = sq_side * sqrt(2)
        sq_diagonal = sq_side * math.sqrt(2)
        # The top face bounding box should be approximately sq_diagonal x sq_diagonal
        assert abs(top_bb.xlen - sq_diagonal) < TOL, \
            f"Top face xlen: expected ~{sq_diagonal:.4f}, got {top_bb.xlen:.4f}"
        assert abs(top_bb.ylen - sq_diagonal) < TOL, \
            f"Top face ylen: expected ~{sq_diagonal:.4f}, got {top_bb.ylen:.4f}"
    
        print("All assertions passed!")
        print(f"  Hex side: {hex_side}, Hex height: {hex_height}")
        print(f"  Square side: {sq_side}, Square height: {sq_height}")
        print(f"  Total height: {total_height:.6f}")
        print(f"  Volume: {actual_vol:.6f} (expected {expected_vol:.6f})")
        print(f"  Face count: {face_count}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00997785/gpt_generated.stl')
