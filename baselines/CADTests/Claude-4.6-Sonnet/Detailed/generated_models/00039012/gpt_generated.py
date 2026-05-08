import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import cadquery as cq
    
    def create_cad() -> cq.Workplane:
        # Convert inches to working units (keeping inches as-is since CadQuery is unit-agnostic)
        # Dimensions from prompt:
        inner_d = 0.70248   # inner bore diameter (inches)
        inner_r = inner_d / 2.0
    
        flange_d = 0.825    # flange / outer diameter (inches)
        flange_r = flange_d / 2.0
    
        pipe_h   = 0.75     # total pipe height (inches)
        flange_h = 0.01125  # flange thickness (inches)
    
        # The pipe body outer diameter equals the flange outer diameter (0.825")
        # making a uniform hollow cylinder.  The "flange" is the thin bottom ring
        # described by the 0.01125" negative extrusion in the prompt.
        #
        # Construction:
        # Step 1 – Outer solid cylinder: d=0.825", h=0.75"  (positive extrusion)
        # Step 2 – Cut inner bore:       d=0.70248", h=0.75" (negative extrusion / cutThruAll)
        #
        # This yields a hollow pipe whose annular cross-section has:
        #   inner radius = 0.35124"
        #   outer radius = 0.4125"
        #   wall thickness = 0.4125 - 0.35124 = 0.06126"
        #
        # The bottom 0.01125" of this pipe is the "thin flange" region referenced
        # in the prompt (the outer circle negative extrusion height).
    
        # --- Step 1: Outer cylinder (pipe body + flange region) ---
        result = (
            cq.Workplane("XY")
            .circle(flange_r)
            .extrude(pipe_h)
        )
    
        # --- Step 2: Cut inner bore through full height ---
        result = (
            result
            .faces(">Z")
            .workplane()
            .circle(inner_r)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 1e-4
    
        solid = result.val()
        bb = solid.BoundingBox()
    
        # Bounding box checks
        assert abs(bb.xlen - flange_d) < TOL, \
            f"X extent: expected {flange_d}, got {bb.xlen}"
        assert abs(bb.ylen - flange_d) < TOL, \
            f"Y extent: expected {flange_d}, got {bb.ylen}"
        assert abs(bb.zlen - pipe_h) < TOL, \
            f"Z (height) extent: expected {pipe_h}, got {bb.zlen}"
    
        # Volume check: annular cylinder
        vol_outer = math.pi * flange_r**2 * pipe_h
        vol_inner = math.pi * inner_r**2 * pipe_h
        expected_vol = vol_outer - vol_inner
        actual_vol = solid.Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.01, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        # Should have exactly 3 faces: top annular ring, bottom annular ring, outer cylinder, inner cylinder
        # Actually: top flat annulus (1), bottom flat annulus (1), outer curved (1), inner curved (1) = 4 faces
        n_faces = result.faces().size()
        assert n_faces == 4, f"Face count: expected 4, got {n_faces}"
    
        # Cylindrical faces: outer wall + inner bore = 2
        n_cyl = result.faces("%Cylinder").size()
        assert n_cyl == 2, f"Cylindrical face count: expected 2, got {n_cyl}"
    
        # Planar faces: top + bottom = 2
        n_plane = result.faces("%Plane").size()
        assert n_plane == 2, f"Planar face count: expected 2, got {n_plane}"
    
        # Check the bore is actually hollow: a point on the axis inside the bore should NOT be inside the solid
        mid_z = pipe_h / 2.0
        bore_test_point = (0.0, 0.0, mid_z)  # on the axis, inside the bore
        assert not solid.isInside(bore_test_point), \
            "Bore test: axis point should be outside (hollow), but isInside returned True"
    
        # A point in the wall should be inside the solid
        wall_r = (inner_r + flange_r) / 2.0
        wall_test_point = (wall_r, 0.0, mid_z)
        assert solid.isInside(wall_test_point), \
            "Wall test: mid-wall point should be inside solid, but isInside returned False"
    
        # Center of mass should be at (0, 0, pipe_h/2) by symmetry
        com = cq.Shape.centerOfMass(solid)
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z - pipe_h / 2.0) < TOL, f"CoM Z: expected {pipe_h/2.0}, got {com.z}"
    
        # Circular edges: top outer, top inner, bottom outer, bottom inner = 4
        n_circ_edges = result.edges("%Circle").size()
        assert n_circ_edges == 4, f"Circular edge count: expected 4, got {n_circ_edges}"
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00039012/gpt_generated.stl')
