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
        hex_radius = 15.0       # circumradius of hexagon (vertex to center)
        hex_height = 10.0       # extrusion height of hexagon
        sq_side    = 14.0       # side length of square
        sq_height  = 8.0        # extrusion height of square
        sq_angle   = 15.0       # rotation angle in degrees (avoids parallel to hex edges)
    
        # --- Step 1: Draw and extrude the hexagon base ---
        # A regular hexagon with 6 sides, circumradius = hex_radius
        # polygon(nSides, diameter) where diameter = 2 * circumradius
        hex_base = (
            cq.Workplane("XY")
            .polygon(6, 2 * hex_radius)
            .extrude(hex_height)
        )
    
        # --- Step 2: Draw and extrude the rotated square on top ---
        # Move to the top face of the hexagon, create a workplane there
        # Draw a square rotated by sq_angle degrees
        result = (
            hex_base
            .faces(">Z")
            .workplane()
            .transformed(rotate=cq.Vector(0, 0, sq_angle))
            .rect(sq_side, sq_side)
            .extrude(sq_height)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # --- Bounding box checks ---
        # The hexagon has circumradius 15, so its flat-to-flat (apothem) = 15 * cos(30°) ≈ 12.99
        # The square rotated 15° has diagonal = 14*sqrt(2) ≈ 19.8, half-diagonal ≈ 9.9
        # The hexagon dominates in XY: bounding box should be ~2*15 = 30 in X and Y
        hex_flat_to_flat = 2 * hex_radius * math.cos(math.radians(30))  # ≈ 25.98
        # Hexagon bounding box in X: 2 * hex_radius = 30 (vertex to vertex)
        # Hexagon bounding box in Y: flat-to-flat = hex_flat_to_flat ≈ 25.98
        # (default polygon orientation: flat top/bottom)
        # Actually CadQuery polygon starts with a vertex at top, so:
        # xlen = 2 * hex_radius * sin(60°) * 2 / 2... let's just check it's ~30
        assert abs(bb.xlen - 2 * hex_radius) < TOL, \
            f"BBox X: expected ~{2*hex_radius:.2f}, got {bb.xlen:.4f}"
        assert abs(bb.ylen - hex_flat_to_flat) < TOL or abs(bb.ylen - 2 * hex_radius) < TOL, \
            f"BBox Y: expected ~{hex_flat_to_flat:.2f} or {2*hex_radius:.2f}, got {bb.ylen:.4f}"
    
        # Total height = hex_height + sq_height
        expected_zlen = hex_height + sq_height
        assert abs(bb.zlen - expected_zlen) < TOL, \
            f"BBox Z: expected {expected_zlen}, got {bb.zlen:.4f}"
    
        # Z extents
        assert abs(bb.zmin - 0.0) < TOL, f"Z min: expected 0, got {bb.zmin:.4f}"
        assert abs(bb.zmax - expected_zlen) < TOL, f"Z max: expected {expected_zlen}, got {bb.zmax:.4f}"
    
        # --- Volume check ---
        # Hexagon area = (3*sqrt(3)/2) * r^2 where r = circumradius
        hex_area = (3 * math.sqrt(3) / 2) * (hex_radius ** 2)
        sq_area  = sq_side ** 2
        expected_vol = hex_area * hex_height + sq_area * sq_height
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # --- Face count check ---
        # Hexagon prism: 6 side faces + 1 bottom + 1 top (but top is partially covered by square)
        # Square prism: 4 side faces + 1 top
        # The interface between hex top and square bottom merges into the hex top face
        # with the square footprint cut out as a separate region
        # Total planar faces: 6 (hex sides) + 1 (hex bottom) + 1 (hex top annular ring) + 4 (sq sides) + 1 (sq top) = 13
        # But the hex top may be split into the annular region around the square
        # Let's just check we have more than 10 planar faces
        n_planar = result.faces("%Plane").size()
        assert n_planar >= 10, f"Expected >= 10 planar faces, got {n_planar}"
    
        # --- Check the object has exactly 1 solid ---
        n_solids = result.solids().size()
        assert n_solids == 1, f"Expected 1 solid, got {n_solids}"
    
        # --- Check center of mass is near Z-axis (symmetric) ---
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected ~0, got {com.x:.4f}"
        assert abs(com.y) < TOL, f"CoM Y: expected ~0, got {com.y:.4f}"
    
        # --- Check top face is at correct Z ---
        top_face_z = result.faces(">Z").val().Center().z
        assert abs(top_face_z - expected_zlen) < TOL, \
            f"Top face Z: expected {expected_zlen}, got {top_face_z:.4f}"
    
        # --- Check bottom face is at Z=0 ---
        bot_face_z = result.faces("<Z").val().Center().z
        assert abs(bot_face_z - 0.0) < TOL, \
            f"Bottom face Z: expected 0, got {bot_face_z:.4f}"
    
        # --- Check square is rotated (no edges parallel to hex edges) ---
        # Hex edges are at 0°, 60°, 120°, 180°, 240°, 300° from horizontal
        # Square rotated 15° has edges at 15°, 75°, 105°, 165° — none match hex angles
        # Verify by checking the square top face edges are not axis-aligned
        sq_top_edges = result.faces(">Z").edges().vals()
        for edge in sq_top_edges:
            start = edge.startPoint()
            end   = edge.endPoint()
            dx = end.x - start.x
            dy = end.y - start.y
            length = math.sqrt(dx**2 + dy**2)
            if length < TOL:
                continue
            angle_deg = math.degrees(math.atan2(dy, dx)) % 180
            # Should not be 0° or 90° (axis-aligned)
            assert abs(angle_deg) > 1.0 and abs(angle_deg - 90) > 1.0 and abs(angle_deg - 180) > 1.0, \
                f"Square edge appears axis-aligned at angle {angle_deg:.2f}°"
    
        print(f"All assertions passed!")
        print(f"  Hexagon: circumradius={hex_radius}, height={hex_height}")
        print(f"  Square:  side={sq_side}, rotation={sq_angle}°, height={sq_height}")
        print(f"  Total height: {expected_zlen}")
        print(f"  Volume: {actual_vol:.2f} mm³")
        print(f"  Planar faces: {n_planar}")
        print(f"  BBox: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00997785/gpt_generated.stl')
