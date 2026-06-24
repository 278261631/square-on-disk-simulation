import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.widgets import Slider, Button

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

def disk_with_round_hole_path(R, offset, radius, angle, cx, cy):
    n = 80
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    circle = np.column_stack([cx + R * np.cos(theta), cy + R * np.sin(theta)])

    rot = np.array([[np.cos(angle), -np.sin(angle)],
                    [np.sin(angle),  np.cos(angle)]])
    sc = rot @ np.array(offset)
    sc_abs = np.array([cx, cy]) + sc

    m = 40
    t_inner = np.linspace(0, 2 * np.pi, m, endpoint=False)[::-1]
    inner = np.column_stack([sc_abs[0] + radius * np.cos(t_inner),
                             sc_abs[1] + radius * np.sin(t_inner)])
    inner = np.vstack([inner, inner[0]])

    verts = np.vstack([circle, inner])
    codes = [Path.MOVETO] + [Path.LINETO] * (n - 1) + [Path.MOVETO] + [Path.LINETO] * m
    return verts, codes

def point_in_square(px, py, cx, cy, angle, hs):
    dx = px - cx
    dy = py - cy
    c, s = np.cos(-angle), np.sin(-angle)
    rx = c * dx - s * dy
    ry = s * dx + c * dy
    return abs(rx) < hs and abs(ry) < hs

def point_in_circle(px, py, cx, cy, radius):
    return (px - cx) ** 2 + (py - cy) ** 2 < radius ** 2

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
    round_hole = [False]
    realtime_map = np.zeros((100, 100))
    cumulative_map = np.zeros((100, 100))

    dummy = Path([[0, 0]])
    patch_green = PathPatch(dummy, fc='#90EE90', ec='black', lw=1, zorder=1)
    patch_gray  = PathPatch(dummy, fc='#999999', ec='black', lw=1, zorder=2)
    ax.add_patch(patch_green)
    ax.add_patch(patch_gray)

    ax_rt = fig.add_axes([0.56, 0.58, 0.38, 0.34])
    ax_rt.set_title('Real-time exposure (green hole)', fontsize=9)
    img_rt = ax_rt.imshow(realtime_map, aspect='equal', cmap='hot',
                          vmin=0, vmax=1, interpolation='nearest',
                          origin='lower')
    ax_rt.set_xlabel('x')
    ax_rt.set_ylabel('y')

    ax_cu = fig.add_axes([0.56, 0.28, 0.38, 0.27])
    ax_cu.set_title('Cumulative exposure (green hole)', fontsize=9)
    img_cu = ax_cu.imshow(cumulative_map, aspect='equal', cmap='hot',
                          vmin=0, interpolation='nearest',
                          origin='lower')
    ax_cu.set_xlabel('x')
    ax_cu.set_ylabel('y')

    R = 1.0

    ax_a1  = fig.add_axes([0.20, 0.232, 0.60, 0.025])
    ax_a2  = fig.add_axes([0.20, 0.202, 0.60, 0.025])
    ax_s1  = fig.add_axes([0.20, 0.172, 0.60, 0.025])
    ax_s2  = fig.add_axes([0.20, 0.142, 0.60, 0.025])
    ax_qg  = fig.add_axes([0.20, 0.112, 0.60, 0.025])
    ax_q   = fig.add_axes([0.20, 0.082, 0.60, 0.025])
    ax_n   = fig.add_axes([0.20, 0.052, 0.60, 0.025])

    s_angle1 = Slider(ax_a1, 'Gray start angle (°)', 0, 360, valinit=180, valfmt='%.0f', color='#999999')
    s_angle2 = Slider(ax_a2, 'Green start angle (°)', 0, 360, valinit=0, valfmt='%.0f', color='#90EE90')
    s_speed1 = Slider(ax_s1, 'Gray speed (RPM)', 0, 120, valinit=10, valfmt='%.1f', color='#999999')
    s_speed2 = Slider(ax_s2, 'Green speed (RPM)', 0, 120, valinit=0, valfmt='%.1f', color='#90EE90')
    s_hole_gray  = Slider(ax_qg, 'Gray hole size', 0.02, 1.5, valinit=0.5, valfmt='%.2f')
    s_hole_green = Slider(ax_q,  'Green hole size', 0.02, 1.5, valinit=0.5, valfmt='%.2f')
    s_grid   = Slider(ax_n,  'Grid (N×N)', 2, 200, valinit=100, valfmt='%d', valstep=1)

    for s in [s_angle1, s_angle2, s_speed1, s_speed2, s_hole_gray, s_hole_green, s_grid]:
        s.valtext.set_fontsize(7)
        s.label.set_fontsize(7)

    angle1 = [0.0]
    angle2 = [0.0]
    paused = [False]

    ax_hole_label = fig.add_axes([0.53, 0.262, 0.20, 0.03])
    ax_hole_label.axis('off')
    hole_label = ax_hole_label.text(0, 0.5, 'Gray hole: Square', fontsize=8,
                                    fontfamily='monospace', verticalalignment='center')

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

    ax_btn1 = fig.add_axes([0.20, 0.262, 0.10, 0.03])
    ax_btn2 = fig.add_axes([0.315, 0.262, 0.10, 0.03])
    ax_btn3 = fig.add_axes([0.74, 0.262, 0.14, 0.03])
    btn_pause = Button(ax_btn1, 'Pause', color='lightgray', hovercolor='yellow')
    btn_reset = Button(ax_btn2, 'Reset', color='lightgray', hovercolor='orange')
    btn_hole  = Button(ax_btn3, 'Toggle', color='lightgray', hovercolor='cyan')

    def toggle_pause(event):
        if paused[0]:
            ani.resume()
            btn_pause.label.set_text('Pause')
            paused[0] = False
        else:
            ani.pause()
            btn_pause.label.set_text('Resume')
            paused[0] = True

    def rebuild_displays():
        n = N[0]
        hs_gray = s_hole_gray.val / 2
        hs_green = s_hole_green.val / 2
        offset_dist = R * 0.44
        offset_cur = (0, offset_dist)
        eff_a1 = angle1[0] + np.deg2rad(s_angle1.val)
        eff_a2 = angle2[0] + np.deg2rad(s_angle2.val)

        if round_hole[0]:
            v1, c1 = disk_with_round_hole_path(R, offset_cur, hs_gray, eff_a1, cx, cy)
        else:
            v1, c1 = disk_with_hole_path(R, offset_cur, hs_gray, eff_a1, cx, cy)
        v2, c2 = disk_with_hole_path(R, offset_cur, hs_green, eff_a2, cx, cy)
        patch_gray.set_path(Path(v1, c1))
        patch_green.set_path(Path(v2, c2))

        gx = cx + offset_dist * np.sin(eff_a2)
        gy = cy - offset_dist * np.cos(eff_a2)
        hx = cx + offset_dist * np.sin(eff_a1)
        hy = cy - offset_dist * np.cos(eff_a1)
        local_x = np.linspace(-hs_green, hs_green, n)
        local_y = np.linspace(-hs_green, hs_green, n)
        for ix in range(n):
            for iy in range(n):
                wx = gx + local_x[ix] * np.cos(eff_a2) - local_y[iy] * np.sin(eff_a2)
                wy = gy + local_x[ix] * np.sin(eff_a2) + local_y[iy] * np.cos(eff_a2)
                if round_hole[0]:
                    lit = point_in_circle(wx, wy, hx, hy, hs_gray)
                else:
                    lit = point_in_square(wx, wy, hx, hy, eff_a1, hs_gray)
                realtime_map[iy, ix] = 1.0 if lit else 0.0

    def do_reset(event):
        was_paused = paused[0]
        if not was_paused:
            ani.pause()
        angle1[0] = 0.0
        angle2[0] = 0.0
        cumulative_map[:] = 0
        img_cu.set_clim(vmin=0, vmax=1)
        rebuild_displays()
        img_rt.set_data(realtime_map[:N[0], :N[0]])
        img_cu.set_data(cumulative_map[:N[0], :N[0]])
        if not was_paused:
            ani.resume()

    def toggle_hole(event):
        round_hole[0] = not round_hole[0]
        hole_label.set_text(f'Gray hole: {"Round" if round_hole[0] else "Square"}')
        rebuild_displays()
        img_rt.set_data(realtime_map[:N[0], :N[0]])
        fig.canvas.draw_idle()

    btn_pause.on_clicked(toggle_pause)
    btn_reset.on_clicked(do_reset)
    btn_hole.on_clicked(toggle_hole)

    def update(frame):
        n = N[0]
        hs_gray = s_hole_gray.val / 2
        hs_green = s_hole_green.val / 2
        dt = 0.03
        angle1[0] += s_speed1.val * (2 * np.pi) / 60 * dt
        angle2[0] += s_speed2.val * (2 * np.pi) / 60 * dt
        eff_a1 = angle1[0] + np.deg2rad(s_angle1.val)
        eff_a2 = angle2[0] + np.deg2rad(s_angle2.val)
        offset_dist = R * 0.44
        offset_cur = (0, offset_dist)

        if round_hole[0]:
            v1, c1 = disk_with_round_hole_path(R, offset_cur, hs_gray, eff_a1, cx, cy)
        else:
            v1, c1 = disk_with_hole_path(R, offset_cur, hs_gray, eff_a1, cx, cy)
        v2, c2 = disk_with_hole_path(R, offset_cur, hs_green, eff_a2, cx, cy)
        patch_gray.set_path(Path(v1, c1))
        patch_green.set_path(Path(v2, c2))

        gx = cx + offset_dist * np.sin(eff_a2)
        gy = cy - offset_dist * np.cos(eff_a2)
        hx = cx + offset_dist * np.sin(eff_a1)
        hy = cy - offset_dist * np.cos(eff_a1)

        if n > realtime_map.shape[0]:
            realtime_map.resize((n, n))
            cumulative_map.resize((n, n))

        local_x = np.linspace(-hs_green, hs_green, n)
        local_y = np.linspace(-hs_green, hs_green, n)
        for ix in range(n):
            for iy in range(n):
                wx = gx + local_x[ix] * np.cos(eff_a2) - local_y[iy] * np.sin(eff_a2)
                wy = gy + local_x[ix] * np.sin(eff_a2) + local_y[iy] * np.cos(eff_a2)
                if round_hole[0]:
                    lit = point_in_circle(wx, wy, hx, hy, hs_gray)
                else:
                    lit = point_in_square(wx, wy, hx, hy, eff_a1, hs_gray)
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
        rebuild_displays()
        fig.canvas.draw_idle()

    s_hole_gray.on_changed(on_change)
    s_hole_green.on_changed(on_change)

    def on_angle_change(val):
        rebuild_displays()
        fig.canvas.draw_idle()

    s_angle1.on_changed(on_angle_change)
    s_angle2.on_changed(on_angle_change)

    plt.show()

if __name__ == '__main__':
    main()
