# MEKANIVO Character Library

Repository permanen untuk source character asset yang dapat digunakan ulang di produksi MEKANIVO.

## Struktur
- `characters/`: paket source code tiap karakter.
- `standards/`: standar bersama untuk geometry, rigging, compatibility, dan QC.
- `templates/`: template paket karakter baru.
- `tests/`: checklist pengujian rig dan render.
- `library-index.json`: katalog karakter dan status kesiapan.

## Status penting
Repository ini baru berisi scaffold. Ucup dan Ebi belum memiliki source rig production-ready. Jangan menandai karakter sebagai production-ready sebelum source sesuai runtime Motion 2.9.2 dan lolos render test.

## Alur pemakaian
1. Existing character: sebutkan ID karakter; baca manifest dan source dari folder tersebut.
2. Character sheet baru: lampirkan sheet Flow; buat paket karakter baru.
3. Auto character: jika tidak ada ID atau sheet, buat karakter khusus scene bila memang diperlukan. Jangan otomatis menyimpan karakter figuran ke library permanen.

## Source runtime
Jangan mengasumsikan format SVG/JSX/Canvas atau menambahkan animation engine baru sebelum memeriksa implementasi rendering pada Motion 2.9.2. Compatibility ditentukan dari runtime yang benar-benar digunakan.
