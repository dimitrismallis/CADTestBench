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
        # Parameters
        L = 80.0   # length (shared elongated edge direction, along X)
        W = 30.0   # width/depth of each slab
        T = 5.0    # thickness (marginal extrusion)
    
        # --- Build L-shape by extruding an L-shaped 2D profile along X ---
        # The L-shape cross section (in YZ plane):
        # Floor part: y from 0 to W, z from 0 to T  (area = W*T)
        # Wall part:  y from 0 to T, z from T to T+W (area = T*W)
        # They share only an edge at z=T, y=0..T (no area overlap)
        # Total cross-section area = 2*W*T
        #
        # Vertices going around the L-shape profile:
        # (y=0,z=0) -> (y=W,z=0) -> (y=W,z=T) -> (y=T,z=T) -> (y=T,z=T+W) -> (y=0,z=T+W) -> close
        # On YZ workplane: first coord = Y, second coord = Z
    
        result = (
            cq.Workplane("YZ")
            .moveTo(0, 0)
            .lineTo(W, 0)
            .lineTo(W, T)
            .lineTo(T, T)
            .lineTo(T, T + W)
            .lineTo(0, T + W)
            .close()
            .extrude(L)
        )
    
        # --- Final object verification ---
        TOL = 0.1
    
        bb = result.val().BoundingBox()
    
        # Overall bounding box dimension checks
        # X: extrusion direction (YZ plane extrudes along X), length = L
        # Y: width of the L (= W, the wider dimension)
        # Z: height of the L (= T + W)
        assert abs(bb.xlen - L) < TOL, \
            f"X length: expected {L!r}, got {bb.xlen!r}"
        assert abs(bb.ylen - W) < TOL, \
            f"Y length: expected {W!r}, got {bb.ylen!r}"
        assert abs(bb.zlen - (T + W)) < TOL, \
            f"Z length: expected {T + W!r}, got {bb.zlen!r}"
    
        # Bounding box extents
        assert abs(bb.ymin - 0.0) < TOL, f"ymin: expected 0, got {bb.ymin}"
        assert abs(bb.ymax - W) < TOL,   f"ymax: expected {W}, got {bb.ymax}"
        assert abs(bb.zmin - 0.0) < TOL, f"zmin: expected 0, got {bb.zmin}"
        assert abs(bb.zmax - (T + W)) < TOL, f"zmax: expected {T+W}, got {bb.zmax}"
    
        # Volume check:
        # Floor slab: W * T cross-section, Wall slab: T * W cross-section
        # They share only an edge (no area overlap), total area = 2 * W * T
        cross_section_area = 2.0 * W * T
        expected_vol = cross_section_area * L
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.2f}, got {actual_vol:.2f}"
    
        # Midpoint along extrusion axis for containment checks
        x_mid = (bb.xmin + bb.xmax) / 2.0
    
        # Check that a point in the "missing" quadrant of the L is NOT inside
        # (y > T and z > T puts us in the empty corner of the L)
        interior_empty = (x_mid, T + 5.0, T + 5.0)
        assert not result.val().isInside(interior_empty), \
            f"Point {interior_empty} should be outside the L-shape (empty corner)"
    
        # Check that a point in the floor slab IS inside
        # Floor: y in [0, W], z in [0, T]
        floor_point = (x_mid, W / 2.0, T / 2.0)
        assert result.val().isInside(floor_point), \
            f"Point {floor_point} should be inside the floor slab"
    
        # Check that a point in the wall slab IS inside
        # Wall: y in [0, T], z in [T, T+W]
        wall_point = (x_mid, T / 2.0, T + W / 2.0)
        assert result.val().isInside(wall_point), \
            f"Point {wall_point} should be inside the wall slab"
    
        # Planar face count = 8:
        # - 2 L-shaped end caps (at x=xmin and x=xmax), kept as single faces by OCCT
        # - 6 rectangular side faces (one per profile edge):
        #     bottom of floor (z=0), outer face of floor (y=W), step face (z=T, y=T..W),
        #     back face of wall (y=T), top face of wall (z=T+W), front face (y=0, full height)
        planar_faces = result.faces("%Plane").size()
        assert planar_faces == 8, \
            f"Planar faces: expected 8, got {planar_faces}"
    
        # No cylindrical faces (all faces are planar)
        cyl_faces = result.faces("%Cylinder").size()
        assert cyl_faces == 0, \
            f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        # Single solid
        assert result.solids().size() == 1, \
            f"Solids: expected 1, got {result.solids().size()}"
    
        # Symmetry: center of mass should be at x_mid (symmetric along extrusion axis)
        com = cq.Shape.centerOfMass(result.val())
        assert abs(com.x - x_mid) < TOL, \
            f"CoM X should be at {x_mid:.2f}, got {com.x:.4f}"
    
        # The two slabs are perpendicular: floor is horizontal (normal in Z),
        # wall is vertical (normal in Y). Verify via face selectors.
        # Bottom face of floor at z=0 (normal pointing -Z)
        bottom_faces = result.faces("<Z").size()
        assert bottom_faces >= 1, f"Expected at least 1 bottom face, got {bottom_faces}"
    
        # Top face of wall at z=T+W (normal pointing +Z)
        top_faces = result.faces(">Z").size()
        assert top_faces >= 1, f"Expected at least 1 top face, got {top_faces}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00002221/gpt_generated.stl')
