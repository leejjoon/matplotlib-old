
import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid.axislines as axislines


def setup_axes(fig, rect):
    
    ax = axislines.Subplot(fig, rect)
    fig.add_subplot(ax)

    ax.set_yticks([0.2, 0.8])
    #ax.set_yticklabels(["short", "loooong"])
    ax.set_xticks([0.2, 0.8])
    #ax.set_xticklabels([r"$\frac{1}{2}\pi$", r"$\pi$"])

    return ax

fig = plt.figure(1, figsize=(6, 3))
fig.subplots_adjust(bottom=0.2)



ax = setup_axes(fig, 131)
for axis in ax.axis.values(): axis.major_ticks.set_tick_out(True)
#or you can simply do "ax.axis[:].major_ticks.set_tick_out(True)"




ax = setup_axes(fig, 132)
ax.axis["left"].set_axis_direction("right")
ax.axis["bottom"].set_axis_direction("top")
ax.axis["right"].set_axis_direction("left")
ax.axis["top"].set_axis_direction("bottom")

ax.axis["left"].major_ticklabels.set_pad(0)
ax.axis["bottom"].major_ticklabels.set_pad(10)



ax = setup_axes(fig, 133)
ax.axis["left"].set_axis_direction("right")
ax.axis[:].major_ticks.set_tick_out(True)

ax.axis["left"].label.set_text("Long Label Left")
ax.axis["bottom"].label.set_text("Label Bottom")
ax.axis["right"].label.set_text("Long Label Right")
ax.axis["right"].label.set_visible(True)
ax.axis["left"].label.set_pad(0)
ax.axis["bottom"].label.set_pad(10)

plt.show()
