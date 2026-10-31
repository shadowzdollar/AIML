import matplotlib.pyplot as plt

x = [1, 2, 3, 4, 5]
y = [2, 3, 6, 8, 10]

plt.plot(x, y)


plt.plot(x, y)

plt.annotate(
    "Important point",
    xy=(5, 10),
    xytext=(3, 7),
    arrowprops=dict(arrowstyle="->")
)

plt.show()
