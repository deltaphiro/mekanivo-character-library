# Ucup v0.3.0-draft

**Status: draft — belum di-approve atau dipromosikan ke library production.**

## Paket
- `source/`: rig, animasi, timeline/reel, build scripts, probe, SVG, validation report, dan reference.
- `preview/`: motion test dan gambar review/QC.
- `previous_versions/`: source dan metadata v0.1/v0.2 untuk pembanding/rollback.
- `manifest.json`: perubahan, metrik, status, dan unresolved issues.

## Regenerasi preview
Jalankan dari folder `source/` (dependensi: cairosvg, pillow, scipy, lxml, numpy; ffmpeg tersedia di PATH):
```bash
python3 build_reel3.py
python3 build_v3_sheets.py
```
Build scripts menerima `UCUP_OUT=/path` untuk mengatur output.

## Batas status
Motion test yang ada bukan bukti kompatibilitas runtime. Integrasi ke MEKANIVO Motion, QC rig/pose, dan review unresolved issues tetap diperlukan sebelum approval.
