import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 1. Basic Line Plot
def basic_line_plot():
    data = np.arange(10)
    plt.figure()
    plt.plot(data)
    plt.title("Basic Line Plot")
    plt.xlabel("X-axis")
    plt.ylabel("Y-axis")
    # plt.show() # Uncomment to show

# 2. Figures and Subplots
def subplots_example():
    fig = plt.figure()

    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)

    ax1.hist(np.random.standard_normal(100), bins=20, color="black", alpha=0.3)
    ax2.scatter(np.arange(30), np.arange(30) + 3 * np.random.standard_normal(30))
    ax3.plot(np.random.standard_normal(50).cumsum(), color="black", linestyle="dashed")

    fig.tight_layout()
    # plt.show()

# 3. Colors, Markers, and Line Styles
def styling_example():
    plt.figure()
    data = np.random.standard_normal(30).cumsum()
    plt.plot(data, color="green", linestyle="dashed", marker="o", label="Default")
    plt.plot(data, color="red", drawstyle="steps-post", label="steps-post")
    plt.legend(loc="best")
    plt.title("Styling and Drawstyles")
    # plt.show()

# 4. Ticks, Labels, and Legends
def ticks_labels_example():
    fig, ax = plt.subplots()
    ax.plot(np.random.standard_normal(1000).cumsum())

    ticks = ax.set_xticks([0, 250, 500, 750, 1000])
    labels = ax.set_xticklabels(["one", "two", "three", "four", "five"], rotation=30, fontsize=8)

    ax.set_xlabel("Stages")
    ax.set_title("Customizing Ticks")
    # plt.show()

# 5. Annotations and Drawing on a Subplot
def annotations_example():
    fig, ax = plt.subplots()
    data = pd.Series(np.random.standard_normal(1000).cumsum())
    ax.plot(data)

    # Adding an arrow and text
    ax.annotate("Peak here", xy=(500, data[500]),
                xytext=(500, data[500] + 10),
                arrowprops=dict(facecolor="black", headwidth=4, width=2, headlength=4),
                horizontalalignment="left", verticalalignment="top")

    # Adding shapes
    rect = plt.Rectangle((200, -5), 100, 10, color="red", alpha=0.3)
    ax.add_patch(rect)
    # plt.show()

# 6. Bar Plots
def bar_plots_example():
    fig, axes = plt.subplots(2, 1)
    data = pd.Series(np.random.uniform(size=16), index=list("abcdefghijklmnop"))

    data.plot.bar(ax=axes[0], color="black", alpha=0.7)
    data.plot.barh(ax=axes[1], color="black", alpha=0.7)
    # plt.show()

# 7. Histograms and Density Plots
def hist_density_example():
    plt.figure()
    values = pd.Series(np.random.standard_normal(1000))
    values.hist(bins=100, alpha=0.3, color="gray", density=True)
    values.plot.density()
    # plt.show()

# 8. Scatter or Point Plots
def scatter_plots_example():
    plt.figure()
    x = np.arange(100)
    y = np.random.standard_normal(100)
    plt.scatter(x, y)
    plt.title("Scatter Plot")
    # plt.show()

# 9. Advanced Subplots with Shared Axes and Adjustments
def shared_axes_subplots_example():
    fig, axis = plt.subplots(2, 2, sharex=True, sharey=True)
    for i in range(2):
        for j in range(2):
            axis[i, j].hist(np.random.standard_normal(700), bins=50, color="orange", alpha=0.5)
    fig.subplots_adjust(wspace=0, hspace=0)
    plt.title("Shared Axes Histograms")
    # plt.show()

# 10. Pie Charts
def pie_chart_example():
    fig, ax = plt.subplots()
    ax.pie([10, 30, 50, 10], labels=["A", "B", "C", "D"], autopct="%1.1f%%", startangle=90)
    ax.set_title("Pie Chart Example")
    # plt.show()

# 11. Fill Between (Confidence Intervals / Area)
def fill_between_example():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.sin(x) + 0.5
    ax.plot(x, y1, color="blue", label="Sine")
    ax.fill_between(x, y1, y2, color="blue", alpha=0.2, label="Confidence Band")
    ax.legend(loc="upper right")
    ax.set_title("Fill Between Example")
    # plt.show()

# 12. Saving Figures to File
def saving_figures_example():
    plt.figure()
    plt.plot(np.random.standard_normal(50).cumsum())
    plt.title("Figure to Save")
    plt.savefig("sample_plot.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved figure as sample_plot.png")

if __name__ == "__main__":
    print("This file contains comprehensive matplotlib visualization examples.")
    # basic_line_plot()
    # subplots_example()
    # styling_example()
    # ticks_labels_example()
    # annotations_example()
    # bar_plots_example()
    # hist_density_example()
    # scatter_plots_example()
    # shared_axes_subplots_example()
    # pie_chart_example()
    # fill_between_example()
    # saving_figures_example()


