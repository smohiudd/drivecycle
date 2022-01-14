import matplotlib.pyplot as plt
from typing import Any, List

plt.style.use('ggplot')


def plot(v: Any,
         i: Any,
         savepath: str,
         labels: List[str] = ["velocity", "time"]) -> None:
    plt.rcParams['savefig.facecolor'] = 'white'
    plt.rcParams.update({'font.size': 14})
    plt.figure(figsize=(15, 8))
    plt.plot(i, v, color='#4b0082', linewidth=1.5)
    plt.xlabel(labels[1])
    plt.ylabel(labels[0])

    if savepath:
        plt.savefig(savepath, transparent=False, bbox_inches='tight')

    plt.show()


def plot_vt(tvq: Any, savepath: str) -> None:
    t = [i[0] for i in tvq]
    v = [i[1] for i in tvq]

    plot(v, t, savepath, labels=["velocity (m/s)", "time (s)"])


def plot_vd(tvq: Any, savepath: str) -> None:
    d = [i[2] for i in tvq]
    v = [i[1] for i in tvq]

    plot(v, d, savepath, labels=["velocity (m/s)", "distance (m)"])


def plot_dt(tvq: Any, savepath: str) -> None:
    d = [i[2] for i in tvq]
    t = [i[0] for i in tvq]

    plot(d, t, savepath, labels=["distance (m)", "time (s)"])
