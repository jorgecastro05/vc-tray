"""Toggle recording of the voice changer's PipeWire sink.

Usage: vc-record [toggle|start|stop|status]
Bind `vc-record` to a global hotkey in KDE.
"""
import os
import shutil
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SINK = os.environ.get("VC_SINK", "voicechanger_out")
OUT_DIR = Path(os.environ.get("VC_OUT_DIR", Path.home() / "Recordings" / "voicechanger"))
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp"))
PIDFILE = RUNTIME / "vc_record.pid"


def recording_pid():
    """Return the PID of the running pw-record, or None (cleans stale files)."""
    try:
        pid = int(PIDFILE.read_text().strip())
        os.kill(pid, 0)
        # guard against PID reuse: make sure it's really pw-record
        if Path(f"/proc/{pid}/comm").read_text().strip() != "pw-record":
            raise ProcessLookupError
        return pid
    except (FileNotFoundError, ValueError, ProcessLookupError, PermissionError, OSError):
        PIDFILE.unlink(missing_ok=True)
        return None


def notify(msg):
    if shutil.which("notify-send"):
        subprocess.Popen(["notify-send", "-i", "audio-input-microphone", "Voice recording", msg])


def start():
    if recording_pid():
        return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"vc_{datetime.now():%Y-%m-%d_%H-%M-%S}.wav"
    proc = subprocess.Popen(
        ["pw-record", "--target", SINK, "-P", "stream.capture.sink=true",
         "--rate", "48000", "--channels", "2", str(out)],
        start_new_session=True,  # survive after this command exits
    )
    PIDFILE.write_text(str(proc.pid))
    notify(f"Started: {out.name}")


def stop():
    pid = recording_pid()
    if not pid:
        return
    os.kill(pid, signal.SIGINT)  # lets pw-record finalize the WAV header
    PIDFILE.unlink(missing_ok=True)
    notify("Stopped")


def main():
    if not shutil.which("pw-record"):
        sys.exit("pw-record not found (is PipeWire installed?)")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "toggle"
    if cmd == "toggle":
        stop() if recording_pid() else start()
    elif cmd == "start":
        start()
    elif cmd == "stop":
        stop()
    elif cmd == "status":
        print("recording" if recording_pid() else "idle")
    else:
        sys.exit("usage: vc-record [toggle|start|stop|status]")


if __name__ == "__main__":
    main()
