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

def point_in_square(px, py, cx, cy, angle, hs):
    dx = px - cx
    dy = py - cy
    c, s = np.cos(-angle), np.sin(-angle)
    rx = c * dx - s * dy
    ry = s * dx + c * dy
    return abs(rx) < hs and abs(ry) < hs

def main():
    fig = plt.figure(figsize=(11, 7.5))
    fig.subplots_adjust(bottom=0.28, left=0.04, right=0.96)

    ax = fig.add_axes([0.04, 0.28, 0.45, 0.68])
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Concentric Disks', fontsize=10)

    cx, cy = 0.0, 0.0
    N = [100]
    realtime_map = np.zeros((100, 100))
    cumulative_map = np.zeros((100, 100))

    dummy = Path([[0, 0]])
    patch_green = PathPatch(dummy, fc='#90EE90', ec='black', lw=1, zorder=1)
    patch_gray  = PathPatch(dummy, fc='#999999', ec='black', lw=1, zorder=2)
    ax.add_patch(patch_green)
    ax.add_patch(patch_gray)

    ax_rt = fig.add_axes([0.56, 0.62, 0.38, 0.35])
    ax_rt.set_title('Real-time exposure (green hole)', fontsize=9)
    img_rt = ax_rt.imshow(realtime_map, aspect='equal', cmap='hot',
                          vmin=0, vmax=1, interpolation='nearest',
                          origin='lower')
    ax_rt.set_xlabel('x')
    ax_rt.set_ylabel('y')

    ax_cu = fig.add_axes([0.56, 0.12, 0.38, 0.35])
    ax_cu.set_title('Cumulative exposure (green hole)', fontsize=9)
    img_cu = ax_cu.imshow(cumulative_map, aspect='equal', cmap='hot',
                          vmin=0, interpolation='nearest',
                          origin='lower')
    ax_cu.set_xlabel('x')
    ax_cu.set_ylabel('y')

    ax_s1 = fig.add_axes([0.20, 0.22, 0.60, 0.03])
    ax_s2 = fig.add_axes([0.20, 0.18, 0.60, 0.03])
    ax_d  = fig.add_axes([0.20, 0.14, 0.60, 0.03])
    ax_q  = fig.add_axes([0.20, 0.10, 0.60, 0.03])
    ax_n  = fig.add_axes([0.20, 0.06, 0.60, 0.03])

    s_speed1 = Slider(ax_s1, 'Gray speed (RPM)', 0, 120, valinit=10, valfmt='%.1f', color='#999999')
    s_speed2 = Slider(ax_s2, 'Green speed (RPM)', 0, 120, valinit=0, valfmt='%.1f', color='#90EE90')
    s_diam   = Slider(ax_d,  'Diameter',  0.2, 2.0, valinit=2.0, valfmt='%.2f')
    s_side   = Slider(ax_q,  'Square side', 0.02, 0.6, valinit=0.6, valfmt='%.2f')
    s_grid   = Slider(ax_n,  'Grid (N×N)', 2, 200, valinit=100, valfmt='%d', valstep=1)

    for s in [s_speed1, s_speed2, s_diam, s_side, s_grid]:
        s.valtext.set_fontsize(8)
        s.label.set_fontsize(8)

    angle1 = [0.0]
    angle2 = [0.0]

    def rebuild_grids(n):
        realtime_map[:] = 0
        cumulative_map[:] = 0
        img_rt.set_data(realtime_map)
        img_cu.set_data(cumulative_map)
        img_rt.set_extent([-1, 1, -1, 1])
        img_cu.set_extent([-1, 1, -1, 1])
        ax_rt.set_xlim(-0.5, n - 0.5)
        ax_rt.set_ylim(-0.5, n - 0.5)
        ax_cu.set_xlim(-0.5, n - 0.5)
        ax_cu.set_ylim(-0.5, n - 0.5)

    def on_grid_change(val):
        n = int(s_grid.val)
        N[0] = n
        realtime_map[:] = 0
        cumulative_map[:] = 0
        img_rt.set_data(realtime_map[:n, :n])
        img_cu.set_data(cumulative_map[:n, :n])
        ax_rt.set_xlim(-0.5, n - 0.5)
        ax_rt.set_ylim(-0.5, n - 0.5)
        ax_cu.set_xlim(-0.5, n - 0.5)
        ax_cu.set_ylim(-0.5, n - 0.5)
        fig.canvas.draw_idle()

    s_grid.on_changed(on_grid_change)

    def update(frame):
        n = N[0]
        R_cur = s_diam.val / 2
        hs_cur = s_side.val / 2
        dt = 0.03
        angle1[0] += s_speed1.val * (2 * np.pi) / 60 * dt
        angle2[0] += s_speed2.val * (2 * np.pi) / 60 * dt
        offset_dist = R_cur * 0.44
        offset_cur = (0, offset_dist)

        v1, c1 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle1[0], cx, cy)
        v2, c2 = disk_with_hole_path(R_cur, offset_cur, hs_cur, angle2[0], cx, cy)
        patch_gray.set_path(Path(v1, c1))
        patch_green.set_path(Path(v2, c2))

        gx = cx + offset_dist * np.sin(angle2[0])
        gy = cy - offset_dist * np.cos(angle2[0])
        hx = cx + offset_dist * np.sin(angle1[0])
        hy = cy - offset_dist * np.cos(angle1[0])

        if n > realtime_map.shape[0]:
            realtime_map.resize((n, n))
            cumulative_map.resize((n, n))

        local_x = np.linspace(-hs_cur, hs_cur, n)
        local_y = np.linspace(-hs_cur, hs_cur, n)
        for ix in range(n):
            for iy in range(n):
                wx = gx + local_x[ix] * np.cos(angle2[0]) - local_y[iy] * np.sin(angle2[0])
                wy = gy + local_x[ix] * np.sin(angle2[0]) + local_y[iy] * np.cos(angle2[0])
                lit = point_in_square(wx, wy, hx, hy, angle1[0], hs_cur)
                realtime_map[iy, ix] = 1.0 if lit else 0.0
                if lit:
                    cumulative_map[iy, ix] += dt * 10

        img_rt.set_data(realtime_map[:n, :n])
        img_cu.set_data(cumulative_map[:n, :n])
        if img_cu.get_clim()[1] < cumulative_map.max() * 1.1:
            img_cu.set_clim(vmin=0, vmax=max(cumulative_map.max() * 1.1, 0.01))

        return patch_gray, patch_green, img_rt, img_cu

    ani = FuncAnimation(fig, update, interval=30, blit=True,
                        cache_frame_data=False, save_count=300)

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
