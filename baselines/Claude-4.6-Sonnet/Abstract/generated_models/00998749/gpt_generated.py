import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        width          = 80.0   # box width (X)
        depth          = 40.0   # box depth (Y) — width = 2 × depth
        base_thickness = 3.0    # base plate thickness
        wall_thickness = 4.0    # wall thickness
        wall_height    = 20.0   # wall height above base
        fillet_r       = 1.5    # inner corner fillet radius
    
        inner_w = width - 2 * wall_thickness   # 72
        inner_d = depth - 2 * wall_thickness   # 32
    
        total_height = base_thickness + wall_height
    
        # --- Step 1: Base plate ---
        result = cq.Workplane("XY").rect(width, depth).extrude(base_thickness)
    
        # --- Step 2: Extrude full outer rectangle upward (wall height) ---
        result = result.faces(">Z").workplane().rect(width, depth).extrude(wall_height)
    
        # --- Step 3: Cut out the inner cavity (hollow the walls) ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .rect(inner_w, inner_d)
            .cutBlind(-wall_height)
        )
    
        # --- Step 4: Fillet all 4 inner vertical edges (inside corners of walls) ---
        # After the cavity cut, the inner vertical edges are at the 4 corners of
        # the inner rectangle: (±inner_w/2, ±inner_d/2) = (±36, ±16).
        #
        # The cavity floor face is at z = base_thickness (normal +Z, second from bottom).
        # Its 4 corner vertices connect to the 4 inner vertical edges going upward.
        #
        # Strategy: select the cavity floor face (">Z[-2]" = second face from top
        # sorted by Z, which is the cavity floor at z=base_thickness),
        # then get the edges of the inner wall faces that are |Z.
        #
        # Simpler: select all 4 inner wall faces via their shared edges with cavity floor.
        # The cavity floor face at z=base_thickness has edges |X and |Y (horizontal).
        # The inner wall faces share those edges.
        # 
        # Most direct: use the cavity floor face to find adjacent vertical edges.
        # The cavity floor face vertices are at (±36, ±16, 3).
        # The inner vertical edges go from z=3 to z=23 at those (x,y) positions.
        #
        # Use: select the cavity floor face, get its vertices, 
        # then select edges from those vertices that are |Z.
        # CadQuery doesn't have a direct "edges from vertices" selector,
        # but we can use the inner wall faces approach.
        #
        # Best working approach: select inner wall faces on both X sides,
        # collect their |Z edges, and fillet in one operation using the
        # solid's edge fillet via OCCT directly.
        #
        # Use cq.Shape fillet on specific edges:
    
        solid = result.val()
    
        # Find all edges that are |Z (vertical) and located at inner corners
        # Inner corner positions: x in {±36}, y in {±16}
        inner_x = inner_w / 2   # 36
        inner_y = inner_d / 2   # 16
    
        target_positions = [
            ( inner_x,  inner_y),
            ( inner_x, -inner_y),
            (-inner_x,  inner_y),
            (-inner_x, -inner_y),
        ]
    
        # Get all edges of the solid
        all_edges = solid.Edges()
    
        inner_vertical_edges = []
        for edge in all_edges:
            # Check if edge is vertical (parallel to Z)
            bb = edge.BoundingBox()
            # A vertical edge has negligible X and Y extent
            if bb.xlen < 0.1 and bb.ylen < 0.1:
                # Check if it's at an inner corner position
                cx = (bb.xmin + bb.xmax) / 2
                cy = (bb.ymin + bb.ymax) / 2
                for tx, ty in target_positions:
                    if abs(cx - tx) < 0.1 and abs(cy - ty) < 0.1:
                        inner_vertical_edges.append(edge)
                        break
    
        # Apply fillet to the 4 inner vertical edges using OCCT
        if inner_vertical_edges:
            filleted_solid = solid.fillet(fillet_r, inner_vertical_edges)
            result = cq.Workplane("XY").newObject([filleted_solid])
    
        # --- Final object verification ---
        TOL = 0.15
    
        bb = result.val().BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - width) < TOL, \
            f"X length: expected {width}, got {bb.xlen}"
        assert abs(bb.ylen - depth) < TOL, \
            f"Y length: expected {depth}, got {bb.ylen}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z length: expected {total_height}, got {bb.zlen}"
    
        # Width should be exactly 2x depth
        assert abs(bb.xlen - 2 * bb.ylen) < TOL, \
            f"Width should be 2x depth: xlen={bb.xlen}, ylen={bb.ylen}"
    
        # Volume check (approximate, accounting for fillet material removal):
        base_vol = width * depth * base_thickness
        outer_area = width * depth
        inner_area = inner_w * inner_d
        wall_vol = (outer_area - inner_area) * wall_height
        expected_vol = base_vol + wall_vol
        actual_vol = result.val().Volume()
        # Allow 5% tolerance for fillet material removal
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.1f}, got {actual_vol:.1f}"
    
        # The box should be open on top (hollow interior)
        solid_shape = result.val()
    
        # A point inside the cavity should NOT be inside the solid
        cavity_point = (0.0, 0.0, base_thickness + wall_height / 2)
        assert not solid_shape.isInside(cavity_point), \
            f"Cavity point {cavity_point} should be outside (hollow), but is inside"
    
        # Base center IS inside the solid
        base_center = (0.0, 0.0, base_thickness / 2)
        assert solid_shape.isInside(base_center), \
            f"Base center {base_center} should be inside the solid"
    
        # Wall material IS inside the solid
        wall_point = (width/2 - wall_thickness/2, 0.0, base_thickness + wall_height/2)
        assert solid_shape.isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid"
    
        # Check planar faces exist
        planar_count = result.faces("%Plane").size()
        assert planar_count >= 6, \
            f"Expected at least 6 planar faces, got {planar_count}"
    
        # Check there are cylindrical faces from the inner fillets (4 inner corners)
        cyl_count = result.faces("%Cylinder").size()
        assert cyl_count >= 4, \
            f"Expected at least 4 cylindrical faces (inner fillets), got {cyl_count}"
    
        # Check the top is open: top face should be a ring (wall top), not solid
        top_face_area = sum(f.Area() for f in result.faces(">Z").vals())
        full_top_area = width * depth
        ring_area = full_top_area - inner_w * inner_d
        assert top_face_area < full_top_area * 0.95, \
            f"Top face area {top_face_area:.1f} should be less than full area {full_top_area:.1f}"
        assert abs(top_face_area - ring_area) / ring_area < 0.05, \
            f"Top ring area: expected ~{ring_area:.1f}, got {top_face_area:.1f}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00998749/gpt_generated.stl')
