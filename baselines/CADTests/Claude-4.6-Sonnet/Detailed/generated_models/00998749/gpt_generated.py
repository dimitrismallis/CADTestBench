import sys, os
import math
import numpy as np
import cadquery as cq

def create_cad()-> cq.Workplane:
    import sys, os
    import math
    import numpy as np
    import cadquery as cq
    from cadquery import selectors
    
    def create_cad() -> cq.Workplane:
        # --- Parameters ---
        inner_width = 0.382387
        inner_length = 0.721321
        outer_width = 0.440093
        wall_thickness = (outer_width - inner_width) / 2   # = 0.028853
        outer_length = inner_length + 2 * wall_thickness   # ≈ 0.779027
        base_depth = 0.143395
        wall_height = 0.131228
        total_height = base_depth + wall_height            # = 0.274623
        fillet_r = 0.017381
    
        inner_half_l = inner_length / 2   # 0.360661
        inner_half_w = inner_width / 2    # 0.191194
    
        # --- Step 1: Full solid box ---
        full_solid = (
            cq.Workplane("XY")
            .rect(outer_length, outer_width)
            .extrude(total_height)
        )
    
        # --- Step 2: Cut inner cavity from top ---
        result = (
            full_solid
            .faces(">Z")
            .workplane()
            .rect(inner_length, inner_width)
            .cutBlind(wall_height)
        )
    
        # --- Step 3: Fillet inner corner edges ---
        # From debug: inner corner edges at top of pocket have centers at
        # (±0.360661, ±0.191194, 0.274623) - these are the vertical pocket corner edges
        # Their center z=0.274623 suggests they span from z=base_depth to z=total_height
        # with center reported at z=total_height (possibly a CadQuery quirk for short edges
        # or the center is computed differently)
        # 
        # Use direct OCCT approach: iterate all edges, find ones at inner corner XY positions
        tol = 0.002
        corners = [
            ( inner_half_l,  inner_half_w),
            (-inner_half_l,  inner_half_w),
            ( inner_half_l, -inner_half_w),
            (-inner_half_l, -inner_half_w),
        ]
    
        # Find inner corner edges - check ALL edges, not just vertical ones
        # The inner corner edges have centers at (±inner_half_l, ±inner_half_w, any_z)
        inner_corner_edge_vals = []
        for edge in result.edges().vals():
            center = edge.Center()
            for cx, cy in corners:
                if abs(center.x - cx) < tol and abs(center.y - cy) < tol:
                    inner_corner_edge_vals.append(edge)
                    break
    
        print(f"Inner corner edges found: {len(inner_corner_edge_vals)}")
        for e in inner_corner_edge_vals:
            c = e.Center()
            print(f"  center=({c.x:.6f}, {c.y:.6f}, {c.z:.6f})")
    
        if len(inner_corner_edge_vals) >= 4:
            from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
            solid_shape = result.val()
            fillet_maker = BRepFilletAPI_MakeFillet(solid_shape.wrapped)
            for edge in inner_corner_edge_vals:
                fillet_maker.Add(fillet_r, edge.wrapped)
            fillet_maker.Build()
            if fillet_maker.IsDone():
                filleted_shape = cq.Shape(fillet_maker.Shape())
                result = cq.Workplane("XY").add(filleted_shape)
                print("Fillet applied via OCCT API")
            else:
                print("OCCT fillet failed, skipping")
        else:
            print(f"Only {len(inner_corner_edge_vals)} inner corner edges found, skipping fillet")
    
        # --- Step 4: Translate ---
        tx = outer_length / 2 - 0.030417
        ty = outer_width / 2 - 0.030417 + 0.001564
        tz = total_height / 2
        result = result.translate((tx, ty, tz))
    
        # --- Final object verification ---
        TOL = 0.01
        bb = result.val().BoundingBox()
    
        assert abs(bb.xlen - outer_length) < TOL, \
            f"X length: expected {outer_length:.6f}, got {bb.xlen:.6f}"
        assert abs(bb.ylen - outer_width) < TOL, \
            f"Y width: expected {outer_width:.6f}, got {bb.ylen:.6f}"
        assert abs(bb.zlen - total_height) < TOL, \
            f"Z height: expected {total_height:.6f}, got {bb.zlen:.6f}"
    
        full_vol = outer_length * outer_width * total_height
        cavity_vol = inner_length * inner_width * wall_height
        expected_vol = full_vol - cavity_vol
        actual_vol = result.val().Volume()
        assert abs(actual_vol - expected_vol) / expected_vol < 0.05, \
            f"Volume: expected ~{expected_vol:.6f}, got {actual_vol:.6f}"
    
        planar_faces = result.faces("%Plane").size()
        assert planar_faces >= 6, \
            f"Expected at least 6 planar faces, got {planar_faces}"
    
        # Verify inner cavity is hollow
        cavity_z = tz - total_height / 2 + base_depth + wall_height / 2
        cavity_point = (tx, ty, cavity_z)
        assert not result.val().isInside(cavity_point), \
            f"Point {cavity_point} should be in the cavity (not solid)"
    
        # Verify base is solid
        base_z = tz - total_height / 2 + base_depth / 2
        base_point = (tx, ty, base_z)
        assert result.val().isInside(base_point), \
            f"Point {base_point} should be inside the base solid"
    
        # Verify wall is solid
        wall_x = tx + inner_length / 2 + wall_thickness / 2
        wall_point = (wall_x, ty, cavity_z)
        if wall_x < tx + outer_length / 2:
            assert result.val().isInside(wall_point), \
                f"Point {wall_point} should be inside the wall solid"
    
        cyl_faces = result.faces("%Cylinder").size()
        print(f"Outer: {outer_length:.6f} x {outer_width:.6f} x {total_height:.6f}")
        print(f"Volume: {actual_vol:.6f} (expected ~{expected_vol:.6f})")
        print(f"BB: x=[{bb.xmin:.4f},{bb.xmax:.4f}] y=[{bb.ymin:.4f},{bb.ymax:.4f}] z=[{bb.zmin:.4f},{bb.zmax:.4f}]")
        print(f"Cyl faces: {cyl_faces}, Planar faces: {planar_faces}")
        print("All assertions passed!")
    
        return result
    
    final_result = create_cad()
    return final_result

final_result = create_cad()
cq.exporters.export(final_result, 'experiments/claude_react_cadtests_final_detailed_2/generation_20260227_130041/generated_models/00998749/gpt_generated.stl')
