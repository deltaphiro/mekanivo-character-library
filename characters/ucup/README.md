# Ucup v0.4.0-draft - side-view rig + walk (belum di-approve, belum masuk library)

## Preview
walk_sync_side_front.mp4  : side (kiri) dan front (kanan), SATU gait, fase sama (loop 1.0 s x 4)
walk_side.mp4 / walk_front.mp4 : masing-masing, dengan lantai bergerak (side) untuk melihat kaki napak
walk_cycle_sheet.png      : 8 fase kunci, side di atas front di bawah
consistency_front_vs_side.png : tinggi pergelangan kaki dan hip, side vs front
side_rig_sheet.png        : skeleton, dimensi bersama, mapping parameter
side_expressions_sheet.png : ekspresi di profil

## Source (folder source/)
gait.py (driver jalan) · ucup_side.py (rig samping) · walk_front.py + ucup_rig4.py (front dari gait yang sama)
ucup_rig3.py/ucup_rig.py/ucup_anim.py (front rig v0.3, wajah, tangan, ekspresi) · build_walk.py · reference/ · validation_report_v04.json · ucup_side_rest.svg
Regenerasi: cd source ; python3 build_walk.py   (UCUP_OUT=/path untuk ganti output; butuh cairosvg, pillow, scipy, lxml, numpy, matplotlib, ffmpeg)
Pakai: S.svg_side(S.pose_from_gait(gait.state(t))) untuk side; R4.svg_doc(WF.front_pose(gait.state(t))) untuk front.
