import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import cadquery as cq
    import math
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        outer_size   = 100.0   # outer square side length (mm)
        inner_size   =  80.0   # inner square side length (mm) → 10 mm wall on each side
        frame_height =  10.0   # height / thickness of the frame (mm)
        wall         = (outer_size - inner_size) / 2.0   # = 10 mm
    
        # --- Step 1: Create the outer solid square box (centered at origin, spans Z=-5 to Z=+5) ---
        frame = cq.Workplane("XY").box(outer_size, outer_size, frame_height)
    
        # --- Step 2: Cut the inner square through the full height ---
        frame = (
            frame
            .faces(">Z").workplane()
            .rect(inner_size, inner_size)
            .cutThruAll()
        )
    
        # --- Final object verification ---
        TOL = 0.01
    
        # 2a. Bounding box
        bb = frame.val().BoundingBox()
        assert abs(bb.xlen - outer_size)   < TOL, f"X length: expected {outer_size}, got {bb.xlen}"
        assert abs(bb.ylen - outer_size)   < TOL, f"Y length: expected {outer_size}, got {bb.ylen}"
        assert abs(bb.zlen - frame_height) < TOL, f"Z length: expected {frame_height}, got {bb.zlen}"
    
        # 2b. Volume = outer_box − inner_cutout
        expected_vol = outer_size**2 * frame_height - inner_size**2 * frame_height
        actual_vol   = frame.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.001, \
            f"Volume: expected {expected_vol:.2f}, got {actual_vol:.2f}"
    
        # 2c. No cylindrical faces (pure square frame)
        cyl_faces = frame.faces("%Cylinder").size()
        assert cyl_faces == 0, f"Cylindrical faces: expected 0, got {cyl_faces}"
    
        # 2d. Face count:
        #   - 1 top ring face + 1 bottom ring face (planar, with hole)
        #   - 4 outer vertical faces + 4 inner vertical faces = 8
        #   Total planar faces = 10
        total_faces = frame.faces().size()
        assert total_faces == 10, f"Total faces: expected 10, got {total_faces}"
    
        # 2e. The center of the frame should be hollow (point inside the cutout is NOT inside the solid)
        # Box is centered at origin, so mid-height is Z=0
        center_point = (0.0, 0.0, 0.0)
        assert not frame.val().isInside(center_point), \
            f"Center point {center_point} should be outside (hollow), but isInside returned True"
    
        # 2f. A point in the wall material should be inside the solid
        # Wall spans from inner_size/2 to outer_size/2 in X; midpoint of wall at Z=0
        wall_mid_x = (inner_size / 2.0 + outer_size / 2.0) / 2.0  # = 45.0
        wall_point = (wall_mid_x, 0.0, 0.0)
        assert frame.val().isInside(wall_point), \
            f"Wall point {wall_point} should be inside the solid, but isInside returned False"
    
        # 2g. Symmetry: center of mass should be at (0, 0, 0) since box is centered at origin
        com = cq.Shape.centerOfMass(frame.val())
        assert abs(com.x) < TOL, f"CoM X: expected 0, got {com.x}"
        assert abs(com.y) < TOL, f"CoM Y: expected 0, got {com.y}"
        assert abs(com.z) < TOL, f"CoM Z: expected 0.0, got {com.z}"
    
        # 2h. Edges parallel to Z (vertical edges): 4 outer corners + 4 inner corners = 8
        z_edges = frame.edges("|Z").size()
        assert z_edges == 8, f"Vertical edges (|Z): expected 8, got {z_edges}"
    
        # 2i. Z extents: box centered at origin spans -frame_height/2 to +frame_height/2
        assert abs(bb.zmin - (-frame_height / 2.0)) < TOL, \
            f"Z min: expected {-frame_height/2.0}, got {bb.zmin}"
        assert abs(bb.zmax - ( frame_height / 2.0)) < TOL, \
            f"Z max: expected {frame_height/2.0}, got {bb.zmax}"
    
        return frame
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_abstract_2/generation_20260227_130157/generated_models/00038614/gpt_generated.stl')
