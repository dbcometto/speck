"""Render process"""
import pyglet
from speck.config import DT


def run_render(snapshot_queue, command_queue, request_conn):
    """Render process entry point — runs on main process"""
    from speck.renderer.windows.viewport import ViewportWindow

    latest_snapshot = {
        "entities":       {},
        "time":           0,
        "timewarp":       1,
        "last_sub_dt":    0,
        "last_sub_steps": 0,
    }

    windows = []
    main_window = ViewportWindow(
        snapshot_queue, request_conn, command_queue,
        windows, width=1800, height=900
    )

    def update(dt):
        nonlocal latest_snapshot
        snap = None
        while not snapshot_queue.empty():
            try:
                snap = snapshot_queue.get_nowait()
            except Exception:
                break
        if snap is not None:
            latest_snapshot = snap
        main_window.set_snapshot(latest_snapshot)

    pyglet.clock.schedule_interval(update, DT)

    try:
        pyglet.app.run()
    except KeyboardInterrupt:
        pyglet.app.exit()