# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair==5.5.0",
#     "marimo",
#     "nbformat==5.10.4",
#     "numpy==2.2.5",
#     "openai==1.77.0",
#     "plotly==6.0.1",
#     "sleap-io==0.2.0",
# ]
# ///

import marimo

__generated_with = "0.13.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
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
    img = np.repeat(img, 3, axis=-1)

    fig = go.Figure()
    fig.add_trace(go.Image(z=img))

    fig.update_layout(
        xaxis=dict(showticklabels=False, range=[0, img.shape[1]]),
        yaxis=dict(showticklabels=False, scaleanchor="y", range=[0, img.shape[0]]),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    cmap = pc.qualitative.Plotly

    for inst in lf:
        pts = inst.numpy()
        color_ind = slp.tracks.index(inst.track)
        color = cmap[color_ind % len(cmap)]

        for src, dst in inst.skeleton.edge_inds:
            x = [pts[src, 0], pts[dst, 0]]
            y = [pts[src, 1], pts[dst, 1]]

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(color=color, width=1),
                showlegend=False
            ))

    # mo.output.append(fig.show())
    mo.output.append(fig)
    return


if __name__ == "__main__":
    app.run()
