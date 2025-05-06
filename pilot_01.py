# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "numpy==2.2.5",
#     "plotly==6.0.1",
#     "sleap-io==0.2.0",
#     "av",
#     "opencv-python==4.11.0.86",
# ]
# ///

import marimo

__generated_with = "0.13.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.colors as pc
    import numpy as np
    import sleap_io as sio
    from pathlib import Path
    return Path, go, mo, np, pc, sio


@app.cell
def _(Path):
    # Download data if not already present

    def download_data(url, filename=None):
        from urllib.parse import unquote
        from urllib.request import urlretrieve

        # Get filename from URL
        if filename is None:
            filename = unquote(url.split("/")[-1])

        filename = Path(filename)

        if not filename.exists():
            # Download the file
            urlretrieve(url, filename)
            print("Downloaded:", filename)
        else:
            print("File already exists:", filename)

        return filename


    download_data("https://storage.googleapis.com/sleap-data/datasets/wang_4mice_john/clips/OFTsocial5mice-0000-00%4015488-18736.mp4")
    slp_path = download_data("https://storage.googleapis.com/sleap-data/datasets/wang_4mice_john/clips/OFTsocial5mice-0000-00%4015488-18736.slp")
    return (slp_path,)


@app.cell
def _(sio, slp_path):
    slp = sio.load_slp(slp_path)
    slp
    return (slp,)


@app.cell
def _(mo, slp):
    fidx = mo.ui.slider(start=0, stop=len(slp) - 1, label="Frame index", value=0, debounce=True, full_width=True, show_value=True)
    fidx
    return (fidx,)


@app.cell
def _(fidx, go, mo, np, pc, slp):
    @mo.cache
    def load_frame(fidx):
        lf = slp[fidx.value]
        img = lf.image

        return lf, img

    lf, img = load_frame(fidx)
    img = np.transpose(img, (1, 0, 2))
    img = np.repeat(img, 3, axis=-1)

    fig = go.Figure()
    fig.add_trace(go.Image(z=img))

    fig.update_layout(
        xaxis=dict(showticklabels=False, scaleanchor="y", range=[0, img.shape[1]]),
        yaxis=dict(showticklabels=False, range=[img.shape[0], 0]),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
    )

    cmap = pc.qualitative.Plotly

    for inst in lf:
        pts = inst.numpy()
        color_ind = slp.tracks.index(inst.track)
        color = cmap[color_ind % len(cmap)]

        for src, dst in inst.skeleton.edge_inds:
            y = [pts[src, 0], pts[dst, 0]]
            x = [pts[src, 1], pts[dst, 1]]

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color=color, width=1),
                showlegend=False
            ))

    # fig.show()
    mo.output.append(fig)
    return


@app.cell
def _(go, mo, np, pc, slp):
    def _():
        trx = slp.numpy(user_instances=True)

        n_frames, n_tracks, n_keypoints, _ = trx.shape
        cmap = pc.qualitative.Set2
        fig = go.Figure()

        for track in range(n_tracks):
            color = cmap[track % len(cmap)]

            for kp in range(n_keypoints):
                # Get (x, y) trajectory over time for this keypoint
                x = trx[:, track, kp, 0]
                y = trx[:, track, kp, 1]
                z = np.arange(n_frames)  # Time as z-axis

                fig.add_trace(go.Scatter3d(
                    x=x,
                    y=y,
                    z=z,
                    mode="lines",
                    line=dict(color=color, width=2),
                    name=f"Track {track}" if kp == 0 else None,  # Avoid duplicate legends
                    showlegend=(kp == 0)
                ))

        fig.update_layout(
            scene=dict(
                xaxis_title="X",
                yaxis_title="Y",
                zaxis_title="Frame (Time)",
                aspectmode="data"
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return mo.output.append(fig)


    _()
    return


if __name__ == "__main__":
    app.run()
