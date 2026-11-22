# Character Asset Format

"Format asset" adalah bentuk source code dan struktur file untuk menyimpan desain, geometry, rig, dan perilaku karakter agar dapat dipanggil ulang. Ini bukan sekadar format gambar PNG.

## Runtime compatibility first
Format source final belum diputuskan. Periksa Motion Graphics 2.9.2 dan renderer aktual sebelum menghasilkan kode. Jangan menciptakan API atau dependency yang tidak didukung.

## Isi minimum paket karakter
- Manifest: ID, nama, tipe anatomi, versi, capability, status QC.
- Source geometry/design.
- Rig dan pivot/anchor.
- Behavior/action yang didukung.
- Preview image dan catatan pengujian.

File dapat digabung atau dipisah sesuai kompleksitas; jangan memecah file tanpa kebutuhan.
