# Ucup v0.4.1-draft - perbaikan logo baju (belum di-approve, belum masuk library)
Hanya logo "m." yang diubah (front + side). Preview/walk dirender ulang dengan logo yang benar.
preview/logo_check.png = bukti: referensi vs logo lama vs baru, overlay, closeup dada front dan side.
source/ucup_logo.py = logo vektor. Regenerasi: cd source ; python3 build_walk.py ; python3 build_logo_check.py (UCUP_OUT=/path untuk ganti output)
Butuh: cairosvg, pillow, scipy, lxml, numpy, matplotlib, ffmpeg.
