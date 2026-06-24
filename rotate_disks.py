import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.widgets import Slider

def disk_with_hole_path(R, offset, half_side, angle, cx, cy):
    n = 80
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    circle = np.column_stack([cx + R * np.cos(theta), cy + R * np.sin(theta)])

    rot = np.array([[np.cos(angle), -np.sin(angle)],
                    [np.sin(angle),  np.cos(angle)]])
    sc = rot @ np.array(offset)
    sc_abs = np.array([cx, cy]) + sc

    hs = half_side
    sq = np.array([[-hs, hs], [hs, hs], [hs, -hs], [-hs, -hs], [-hs, hs]])
    sq_rot = sq @ rot.T + sc_abs

    verts = np.vstack([circle, sq_rot])
    codes = [Path.MOVETO] + [Path.LINETO] * (n - 1) + [Path.MOVETO] + [Path.LINETO] * 4
    return verts, codes

def main():
    fig, ax = plt.subplots(figsize=(8, 6.5))
    fig.subplots_adjust(bottom=0.35)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')

    cx, cy = 0.0, 0.0

    dummy = Path([[0, 0]])
    patch_green = PathPatch(dummy, fc='#90EE90', ec='black', lw=1)
    patch_gray  = PathPatch(dummy, fc='#999999', ec='black', lw=1)
    ax.add_patch(patch_green)
    ax.add_patch(patch_gray)

    ax_s1 = fig.add_axes([0.2, 0.22, 0.6, 0.04])
    ax_s2 = fig.add_axes([0.2, 0.17, 0.6, 0.04])
    ax_d  = fig.add_axes([0.2, 0.11, 0.6, 0.04])
    ax_q  = fig.add_axes([0.2, 0.05, 0.6, 0.04])

    s_speed1 = Slider(ax_s1, 'Gray speed (RPM)', 0, 120, valinit=0, valfmt='%.1f', color='#999999')
    s_speed2 = Slider(ax_s2, 'Green speed (RPM)', 0, 120, valinit=10, valfmt='%.1f', color='#90EE90')
    s_diam   = Slider(ax_d,  'Diameter',  0.2, 2.0, valinit=2.0, valfmt='%.2f')
    s_side   = Slider(ax_q,  'Square side', 0.02, 0.6, valinit=0.6, valfmt='%.2f')

    angle1 = [0.0]
    angle2 = [0.0]

    def update(frame):
        R_cur = s_diam.val / 2
        hs_cur = s_side.val / 2
        dt = 0.03
        angle1[0] += s_speed1.val * (2 * np.pi) / 60 * dt
        angle2[0] += s_speed2.val * (2 * np.pi) / 60 * dt
        offset_cur = (0, R_cur * 0.44)

        v1, c1 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle1[0], cx, cy)
        v2, c2 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle2[0], cx, cy)
        patch_gray.set_path(Path(v1, c1))
        patch_green.set_path(Path(v2, c2))
        return patch_gray, patch_green

    ani = FuncAnimation(fig, update, interval=30, blit=True, cache_frame_data=False, save_count=300)

    def on_change(val):
        R_cur = s_diam.val / 2
        hs_cur = s_side.val / 2
        offset_cur = (0, R_cur * 0.44)
        v1, c1 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle1[0], cx, cy)
        v2, c2 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle2[0], cx, cy)
        patch_gray.set_path(Path(v1, c1))
        patch_green.set_path(Path(v2, c2))
        fig.canvas.draw_idle()

    s_diam.on_changed(on_change)
    s_side.on_changed(on_change)

    plt.show()

if __name__ == '__main__':
    main()
