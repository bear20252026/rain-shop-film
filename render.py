# Chunked, resumable renderer: python3 render.py sNN worker nworkers
# Each 10-second chunk is piped straight into ffmpeg (no PNG pile-up); finished chunks are skipped on restart.
import sys, os, subprocess, importlib, numpy as np, time, cv2
cv2.setNumThreads(1)
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from engine import FPS, OW, FH, make_vig

CH = 10.0
def chunk_dir(name): d = os.path.join(HERE, 'out', name); os.makedirs(d, exist_ok=True); return d

def render_chunk(scene, name, k, vig):
    d = chunk_dir(name); fn = os.path.join(d, f'c{k:04d}.mp4')
    if os.path.exists(fn): return False
    n0 = int(round(k * CH * FPS)); n1 = min(int(round(scene.dur * FPS)), int(round((k + 1) * CH * FPS)))
    if n1 <= n0: return False
    tmp = fn + '.part.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{FH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'fast', '-crf', '16', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(n0, n1):
        f = scene.full(i / FPS, vig)
        p.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    os.replace(tmp, fn)
    return True

if __name__ == '__main__':
    name = sys.argv[1]; wk = int(sys.argv[2]); nw = int(sys.argv[3])
    mod = importlib.import_module(name); scene = mod.scene; vig = make_vig()
    nch = int(np.ceil(scene.dur / CH))
    order = list(range(wk, nch, nw))
    for k in order:
        t0 = time.time()
        if render_chunk(scene, name, k, vig): print(f'{name} chunk {k}/{nch} {time.time() - t0:.0f}s', flush=True)
    print('done', name, wk, flush=True)
