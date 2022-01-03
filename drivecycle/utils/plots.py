import matplotlib.pyplot as plt
from typing import Any, List


def plot(v: Any, i: Any, labels: List[str] = ["velocity", "time"]) -> None:
    plt.figure(figsize=(20, 5))
    plt.plot(i, v)
    plt.xlabel(labels[1])
    plt.ylabel(labels[0])
    plt.show()


def plot_vt(tvq: Any) -> None:
    t = [i[0] for i in tvq]
    v = [i[1] for i in tvq]

    plot(v, t, labels=["velocity", "time"])


def plot_vd(tvq: Any) -> None:
    d = [i[2] for i in tvq]
    v = [i[1] for i in tvq]

    plot(v, d, labels=["velocity", "distance"])


def plot_dt(tvq: Any) -> None:
    d = [i[2] for i in tvq]
    t = [i[0] for i in tvq]

    plot(d, t, labels=["distance", "time"])
