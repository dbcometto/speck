"""Run Speck"""
import multiprocessing
from speck.core.sim import run_sim
from speck.core.render import run_render

if __name__ == '__main__':
    snapshot_queue = multiprocessing.Queue(maxsize=10)
    command_queue  = multiprocessing.Queue()
    render_conn, sim_conn = multiprocessing.Pipe(duplex=True)

    sim_process = multiprocessing.Process(
        target=run_sim,
        args=(snapshot_queue, command_queue, sim_conn),
        daemon=True
    )
    sim_process.start()

    run_render(snapshot_queue, command_queue, render_conn)

    sim_process.terminate()
    sim_process.join()