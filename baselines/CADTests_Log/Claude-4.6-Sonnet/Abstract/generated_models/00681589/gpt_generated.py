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
        outer_radius = 30.0       # outer tip radius
        base_inner_radius = 12.0  # base inner radius
        extrude_height = 10.0     # extrusion height
        num_points = 5
    
        # --- Step 1: Compute star vertices with slightly varying inner radii ---
        # Each inner vertex gets a slightly different radius to create different angles
        inner_radius_offsets = [0.0, 1.5, -1.0, 2.0, -0.5]  # per-valley variation
    
        vertices = []
        for i in range(num_points):
            # Outer tip angle (starting from top, going clockwise)
            outer_angle = math.radians(90 + i * 72)
            ox = outer_radius * math.cos(outer_angle)
            oy = outer_radius * math.sin(outer_angle)
            vertices.append((ox, oy))
    
            # Inner valley angle (halfway between outer tips)
            inner_angle = math.radians(90 + i * 72 + 36)
            r_inner = base_inner_radius + inner_radius_offsets[i]
            ix = r_inner * math.cos(inner_angle)
            iy = r_inner * math.sin(inner_angle)
            vertices.append((ix, iy))
    
        # --- Step 2: Build the star profile as a closed wire using Workplane ---
        # Use the fluent API to draw the star polygon
        star_wire = (
            cq.Workplane("XY")
            .moveTo(vertices[0][0], vertices[0][1])
        )
        for vx, vy in vertices[1:]:
            star_wire = star_wire.lineTo(vx, vy)
        star_wire = star_wire.close()
    
        # --- Step 3: Extrude the star profile ---
        result = star_wire.extrude(extrude_height)
    
        # --- Final object verification ---
        TOL = 0.5  # tolerance for geometric checks
    
        # Check bounding box: star fits within outer_radius circle
        bb = result.val().BoundingBox()
    
        # X and Y extents should be approximately 2 * outer_radius (diameter)
        assert bb.xlen <= 2 * outer_radius + TOL, \
            f"X extent too large: expected <= {2*outer_radius + TOL:.2f}, got {bb.xlen:.2f}"
        assert bb.ylen <= 2 * outer_radius + TOL, \
            f"Y extent too large: expected <= {2*outer_radius + TOL:.2f}, got {bb.ylen:.2f}"
    
        # Z extent should equal extrude height
        assert abs(bb.zlen - extrude_height) < TOL, \
            f"Z height: expected {extrude_height}, got {bb.zlen:.2f}"
    
        # The star should span close to the full outer radius in both X and Y
        assert bb.xlen > outer_radius, \
            f"X extent too small: expected > {outer_radius}, got {bb.xlen:.2f}"
        assert bb.ylen > outer_radius, \
            f"Y extent too small: expected > {outer_radius}, got {bb.ylen:.2f}"
    
        # Volume check: star area should be between inner circle and outer circle areas
        inner_area = math.pi * base_inner_radius**2
        outer_area = math.pi * outer_radius**2
        expected_vol_min = inner_area * extrude_height
        expected_vol_max = outer_area * extrude_height
        vol = result.val().Volume()
        assert vol > expected_vol_min, \
            f"Volume too small: expected > {expected_vol_min:.1f}, got {vol:.1f}"
        assert vol < expected_vol_max, \
            f"Volume too large: expected < {expected_vol_max:.1f}, got {vol:.1f}"
    
        # Face count: a 5-pointed star extruded should have:
        # - 1 top face, 1 bottom face (both star-shaped)
        # - 10 side faces (one per edge of the star polygon = 10 edges)
        # Total = 12 faces
        face_count = result.faces().size()
        assert face_count == 12, \
            f"Face count: expected 12, got {face_count}"
    
        # Check top and bottom faces exist
        top_faces = result.faces(">Z").size()
        bot_faces = result.faces("<Z").size()
        assert top_faces == 1, f"Top face count: expected 1, got {top_faces}"
        assert bot_faces == 1, f"Bottom face count: expected 1, got {bot_faces}"
    
        # Check the solid is centered roughly around Z=0 to Z=extrude_height
        assert abs(bb.zmin) < TOL, f"Z min: expected ~0, got {bb.zmin:.2f}"
        assert abs(bb.zmax - extrude_height) < TOL, f"Z max: expected ~{extrude_height}, got {bb.zmax:.2f}"
    
        # Check that a point at the center (0,0, height/2) is inside the solid
        center_point = (0, 0, extrude_height / 2)
        assert result.val().isInside(center_point), \
            f"Center point {center_point} should be inside the solid"
    
        # Check that a point far outside is NOT inside the solid
        outside_point = (outer_radius * 2, outer_radius * 2, extrude_height / 2)
        assert not result.val().isInside(outside_point), \
            f"Outside point {outside_point} should NOT be inside the solid"
    
        # Verify the star has 10 side edges parallel to Z (vertical edges at star corners)
        vertical_edges = result.edges("|Z").size()
        assert vertical_edges == 10, \
            f"Vertical edges: expected 10, got {vertical_edges}"
    
        print(f"✓ Star bounding box: {bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}")
        print(f"✓ Volume: {vol:.2f} mm³")
        print(f"✓ Face count: {face_count}")
        print(f"✓ Vertical edges: {vertical_edges}")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00681589/gpt_generated.stl')
