# Design review pictures

The design review PDF's screenshots and render pages (`shots/`, `r6/`), recovered on 2026-10-01 from the 264-page PDF
of 30/09 after the original image folder was lost. Build with an image folder holding these two folders plus a copy
of `Docs/ui-screens` as `ui/`:

    python Tools/docs/build_doc.py <game.json> <imgdir> <out.pdf>

`game.json` comes from the ExportGameDoc fixture (MB_EXPORT=<path>, run with -testFilter ExportGameDoc).
