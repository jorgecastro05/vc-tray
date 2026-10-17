# vc-tray

Hotkey-driven recording of the `voicechanger_out` PipeWire sink, plus a tray indicator.

    uv tool install .
    vc-tray --install-autostart   # start the tray at login
    # bind `vc-record` to a global hotkey in KDE

Env vars: VC_SINK (default voicechanger_out), VC_OUT_DIR (default ~/Recordings/voicechanger).
