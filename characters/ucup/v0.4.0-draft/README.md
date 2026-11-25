# Ucup v0.4.0-draft — Side-view rig + shared walk cycle

**Status: draft; belum di-approve atau dipromosikan ke library production.**

## Isi paket
- `source/`: rig profil, front rig, gait driver, build script, SVG, validation report, dan reference sheet.
- `preview/`: video walk side/front/sinkron, cycle sheet, rig sheet, expression sheet, dan consistency plot.
- `manifest.json`: perubahan, hasil verifikasi, dan unresolved issues.

## Regenerasi
Jalankan dari folder `source/`:

```bash
python3 build_walk.py
```

Dependensi: cairosvg, pillow, scipy, lxml, numpy, matplotlib, dan ffmpeg. Output default dibuat di folder `rebuilt/`; gunakan `UCUP_OUT=/path` untuk mengganti lokasi output.

## Pemakaian
- Side/profile: `S.svg_side(S.pose_from_gait(gait.state(t)))`
- Front: `R4.svg_doc(WF.front_pose(gait.state(t)))`

Kedua tampilan memakai satu state gait yang sama. Detail klaim dan batas validasi ada di `manifest.json` dan `source/validation_report_v04.json`.
