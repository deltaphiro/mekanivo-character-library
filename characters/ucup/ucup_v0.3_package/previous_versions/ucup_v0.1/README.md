# Ucup v0.1.0-draft (belum di-approve)
Karakter MEKANIVO dibangun ulang sebagai SVG vektor prosedural (bukan crop dari sheet).

## Review dulu (folder preview/)
- ucup_motion_test.mp4 : 20 dtk, 30 fps. Idle, wave, explain, point, think->aha, thumbs+wink, recoil->shrug, hop.
- motion_contact_sheet.png, stress_test.png (ekstrem sendi), reference_comparison.png (jujur soal beda)
- expressions_sheet.png (REF vs NEW), hands_sheet.png, poses_sheet.png, rig_sheet.png, parts_sheet.png

## Source (folder source/)
- ucup_rest.svg : rest pose, id semantik (ucup-root > torso > head/arm > forearm > hand ; leg > shin > foot)
- ucup_rig.py : geometri + rig (character_svg(pose)). ucup_anim.py : IK, ekspresi, pose, timeline, secondary motion
- reel.py / build_reel.py / build_sheets.py : regenerasi semua preview
- states_library.json, validation_report.json
Regenerasi: python3 build_sheets.py && python3 build_reel.py (butuh cairosvg, pillow, lxml, ffmpeg)

## Pakai
from ucup_rig import svg_doc; svg_doc({'R_abd':60,'R_hand':'point'}) -> SVG string
Sudut: abd = keluar +, flex/wrist = ke dalam +, head/torso = searah jarum jam +. R/L = sisi layar.
