# Ucup v0.4.1-draft — Chest logo correction

**Status: draft; belum di-approve, belum dipromosikan ke production library.**

Versi ini berbasis v0.4.0. Perubahan fungsionalnya hanya koreksi logo dada **“m.”** agar lebih dekat dengan logo pada reference sheet. Rig front, rig side, dan shared gait dipertahankan; preview walk dirender ulang dengan logo baru.

## Struktur
- `source/`: source rig, gait driver, logo vector, build scripts, metrics, validation report, dan reference sheet.
- `preview/`: logo comparison, rig/expression sheets, walk cycle sheet, dan video preview.
- `manifest.json`: perubahan, hasil pengukuran, status, dan unresolved issues.

## Regenerasi
Jalankan dari folder `source/`:

```bash
python3 build_walk.py
python3 build_logo_check.py
```

Kedua script menulis output ke `../rebuilt/` secara default. Atur `UCUP_OUT=/path` untuk mengganti lokasi output.

Dependensi: cairosvg, pillow, scipy, lxml, numpy, matplotlib, dan ffmpeg.

## Catatan validasi
- IoU bentuk huruf “m” terhadap mask reference: **0.9774**.
- Error pusat dot terhadap reference: sekitar **0.3 unit**; radius vector 76 vs hasil ukur 75.9.
- Validasi gait yang diwarisi dari v0.4: rig vs IK marker max 0.45 px; foot slide max 0.09 px/frame; front-vs-side ankle Y max 0.192 px; loop closure 0.
- Hasil ini berasal dari script/report proyek. Belum membuktikan kompatibilitas di runtime MEKANIVO Motion.

Lihat `manifest.json` dan `source/validation_report_v041.json` untuk detail dan batas validasi.
