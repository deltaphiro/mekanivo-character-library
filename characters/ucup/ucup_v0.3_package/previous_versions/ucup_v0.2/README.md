# Ucup v0.2.0-draft — structural revision (belum di-approve)
v0.1 utuh di ../ucup_v0.1/ (bisa dipulihkan). v0.2 hanya mengubah konstruksi, bukan identitas.

Review (preview/): diag_before_after.png, diag_v02_closeups.png, diag_v02_all10.png, construction_comparison.png,
stress_test_v02.png, ucup_v02_motion_test.mp4, v02_motion_contact_sheet.png
Source (source/): ucup_rig2.py (rig), anim2.py (IK + 10 pose diagnostik), reel2.py (motion test), ucup_rest_v02.svg,
validation_report_v02.json. ucup_rig.py/ucup_anim.py = dependensi v0.1 (wajah, topi, tangan, timeline).
Parameter baru: twist, bend, squat, hip, R_fwd/L_fwd, R_z/L_z, arm_top, R_sh/L_sh, R_fold/L_fold.
Regenerasi: python3 build_reel2.py && python3 build_v2_sheets.py (dari folder source; butuh cairosvg, pillow, scipy, lxml, ffmpeg)
