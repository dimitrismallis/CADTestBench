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
        hex_side = 1.47802       # side length of hexagon
        hex_height = 0.5         # extrusion height of hexagon
        cyl_diameter = 1.2       # cylinder diameter
        cyl_radius = cyl_diameter / 2.0  # 0.6
        cyl_height = hex_height / 2.0    # 0.25 (half of hex height)
    
        # --- Step 1: Create hexagonal prism ---
        # CadQuery's polygon uses the circumradius (distance from center to vertex).
        # For a regular hexagon, circumradius = side_length (they are equal).
        hex_prism = (
            cq.Workplane("XY")
            .polygon(6, hex_side * 2)   # polygon takes diameter (2 * circumradius)
            .extrude(hex_height)
        )
    
        # --- Step 2: Create cylinder on top of hexagonal prism ---
        # The cylinder is placed on the top face of the hex prism (z = hex_height)
        # and extruded upward by cyl_height
        result = (
            hex_prism
            .faces(">Z")
            .workplane()
            .circle(cyl_radius)
            .extrude(cyl_height)
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # Bounding box checks
        bb = result.val().BoundingBox()
    
        # For a regular hexagon with side length s, the flat-to-flat distance (width) = s * sqrt(3)
        # and the vertex-to-vertex distance = 2 * s
        hex_vertex_to_vertex = 2 * hex_side  # = 2 * 1.47802 = 2.95604
        hex_flat_to_flat = hex_side * math.sqrt(3)  # ≈ 2.5598
    
        # X and Y extents should be bounded by the hex vertex-to-vertex distance
        assert abs(bb.xlen - hex_vertex_to_vertex) < TOL, \
            f"BBox X: expected {hex_vertex_to_vertex:.5f}, got {bb.xlen:.5f}"
        assert abs(bb.ylen - hex_flat_to_flat) < TOL, \
            f"BBox Y: expected {hex_flat_to_flat:.5f}, got {bb.ylen:.5f}"
    
        # Total height = hex_height + cyl_height = 0.5 + 0.25 = 0.75
        total_height = hex_height + cyl_height
        assert abs(bb.zlen - total_height) < TOL, \
            f"BBox Z (total height): expected {total_height:.5f}, got {bb.zlen:.5f}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0.0, got {bb.zmin:.5f}"
        assert abs(bb.zmax - total_height) < TOL, f"Z max: expected {total_height:.5f}, got {bb.zmax:.5f}"
    
        # Volume check
        # Hexagon area = (3 * sqrt(3) / 2) * s^2
        hex_area = (3 * math.sqrt(3) / 2) * (hex_side ** 2)
        hex_vol = hex_area * hex_height
        cyl_vol = math.pi * (cyl_radius ** 2) * cyl_height
        expected_vol = hex_vol + cyl_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.5f}, got {actual_vol:.5f}"
    
        # Face count check:
        # Hex prism: 1 bottom + 6 sides + 1 top (but top is partially covered by cylinder) = 8 faces
        # However, the top of the hex prism is split: the cylinder base overlaps part of it.
        # Cylinder: 1 top circle + 1 curved side = 2 faces
        # The interface between cylinder base and hex top creates an annular ring on hex top
        # So: hex bottom (1) + hex sides (6) + hex top annular ring (1) + cyl curved (1) + cyl top (1) = 10 faces
        face_count = result.faces().size()
        assert face_count == 10, f"Face count: expected 10, got {face_count}"
    
        # Check cylindrical faces: curved side of cylinder = 1
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 1, f"Cylindrical faces: expected 1, got {cyl_faces}"
    
        # Check top face is at z = total_height
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - total_height) < TOL, \
            f"Top face Z center: expected {total_height:.5f}, got {top_face_z:.5f}"
    
        # Check bottom face is at z = 0
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z center: expected 0.0, got {bot_face_z:.5f}"
    
        # Check the model is centered at x=0, y=0
        center = cq.Shape.centerOfMass(result.val())
        assert abs(center.x) < TOL, f"Center X: expected 0.0, got {center.x:.5f}"
        assert abs(center.y) < TOL, f"Center Y: expected 0.0, got {center.y:.5f}"
    
        # Check circular edges (top of cylinder + bottom of cylinder interface)
        circ_edges = result.edges("%Circle").size()
        assert circ_edges >= 2, f"Circular edges: expected at least 2, got {circ_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00980651/gpt_generated.stl')
