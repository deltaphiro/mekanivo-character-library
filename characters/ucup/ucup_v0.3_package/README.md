# Ucup v0.3.0-draft (belum di-approve, belum masuk library)

## Isi paket
- preview/    : MP4 motion test + semua sheet review (waist, silhouette, hat/hair, head/neck, articulation, contact sheet)
- source/     : kode sumber lengkap (rig, animasi, reel, build script, probe), ucup_rest_v03.svg, validation_report_v03.json, reference/
- manifest.json : status, perubahan, hasil ukur, daftar masalah yang belum beres
- previous_versions/ : source v0.1 dan v0.2 (bisa dipulihkan)

## Regenerasi (dari folder source/)
pip install cairosvg pillow scipy lxml numpy ; butuh ffmpeg di PATH
python3 build_reel3.py      # render motion test + contact sheet  -> ../rebuilt/preview
python3 build_v3_sheets.py  # semua sheet komparasi + metrik       -> ../rebuilt/preview
Output dir bisa diganti: UCUP_OUT=/path python3 build_reel3.py
Catatan: build_v3_sheets.py membandingkan dengan v0.2 dan memakai ucup_rig2.py + diag_v1.py (ikut di source/).

## File inti
ucup_rig3.py (rig v0.3) · anim3.py (IK + pose diagnostik) · reel3.py (timeline motion test) · hatprobe.py (probe rambut/topi)
ucup_rig.py + ucup_anim.py (wajah, topi, tangan, timeline dari v0.1 - tetap dipakai) · ucup_rig2.py (v0.2, untuk komparasi)
Konvensi: R/L = sisi layar. Sudut: abd keluar +, flex/wrist ke dalam +, head/torso searah jarum jam +.
