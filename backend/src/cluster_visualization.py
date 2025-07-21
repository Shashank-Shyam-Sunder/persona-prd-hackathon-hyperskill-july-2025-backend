# src/cluster_visualization.py

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
import umap
from .persona_config import PERSONA_TO_FOLDER

def get_visualization_path(persona: str, subreddit_filename: str) -> str:
    persona_folder = PERSONA_TO_FOLDER.get(persona)
    if not persona_folder:
        raise ValueError(f"Unknown persona '{persona}'")

    subreddit_folder = subreddit_filename.replace('.json', '')
    output_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "processed", persona_folder, subreddit_folder)
    )
    os.makedirs(output_folder, exist_ok=True)

    return os.path.join(output_folder, "cluster_visualization.html")

def check_visualization_exists(persona: str, subreddit_filename: str) -> bool:
    return os.path.exists(get_visualization_path(persona, subreddit_filename))

def reduce_to_2d(embeddings: np.ndarray, random_state: int = 42) -> np.ndarray:
    reducer = umap.UMAP(n_components=2, random_state=random_state)
    scaled_embeddings = StandardScaler().fit_transform(embeddings)
    return reducer.fit_transform(scaled_embeddings)

def create_interactive_plot(df: pd.DataFrame, embeddings_2d: np.ndarray, labels: np.ndarray) -> go.Figure:
    plot_df = pd.DataFrame({
        'x': embeddings_2d[:, 0],
        'y': embeddings_2d[:, 1],
        'cluster': labels,
        'post_id': df['post_id'],
        'title': df['title'].fillna("(No title)"),
        'text': df['selftext'].fillna("(No text content)")
    })

    plot_df['cluster'] = (plot_df['cluster'] + 1).astype(str)

    fig = px.scatter(
        plot_df,
        x='x',
        y='y',
        color='cluster',
        color_discrete_sequence=px.colors.qualitative.Safe,
        hover_data={'post_id': True, 'title': True, 'text': False},
        title='Interactive Cluster Visualization',
        labels={
            'x': 'UMAP Dimension 1',
            'y': 'UMAP Dimension 2',
            'cluster': 'Cluster'
        },
        category_orders={'cluster': sorted(plot_df['cluster'].unique(), key=lambda x: int(x))}
    )

    fig.update_traces(hovertemplate='<b>Post ID:</b> %{customdata[0]}<br><b>Title:</b> %{customdata[1]}<extra></extra>')

    fig.update_layout(
        clickmode='event',
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [{
                'label': 'Reset View',
                'method': 'relayout',
                'args': ['xaxis.range', None]
            }]
        }],
        annotations=[{
            'text': 'Click on a point to see post details',
            'showarrow': False,
            'x': 0.5,
            'y': 1.05,
            'xref': 'paper',
            'yref': 'paper',
            'font': {'size': 14}
        }],
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=800,
        newshape=dict(line_color='#009900'),
    )

    return fig

def save_visualization(fig: go.Figure, persona: str, subreddit_filename: str) -> str:
    output_path = get_visualization_path(persona, subreddit_filename)

    post_script = """
    const gd = document.querySelector('.plotly-graph-div');
    document.addEventListener('DOMContentLoaded', function() {
        gd.on('plotly_click', function(data) {
            const point = data.points[0];
            if (point.customdata && point.customdata.length >= 3) {
                const post_id = point.customdata[0];
                const title = point.customdata[1];
                const text = point.customdata[2] || '(No text content)';

                let modal = document.getElementById('post-modal');
                if (!modal) {
                    modal = document.createElement('div');
                    modal.id = 'post-modal';
                    modal.style = 'display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; overflow:auto; background-color:rgba(0,0,0,0.4);';

                    const modalContent = document.createElement('div');
                    modalContent.style = 'background:#fff; margin:10% auto; padding:20px; border:1px solid #888; width:80%; max-height:80%; overflow:auto; border-radius:5px;';

                    const closeBtn = document.createElement('span');
                    closeBtn.innerHTML = '&times;';
                    closeBtn.style = 'color:#aaa; float:right; font-size:28px; font-weight:bold; cursor:pointer;';
                    closeBtn.onclick = () => modal.style.display = 'none';

                    const modalTitle = document.createElement('h2');
                    modalTitle.id = 'modal-title';

                    const modalText = document.createElement('div');
                    modalText.id = 'modal-text';
                    modalText.style = 'white-space:pre-wrap; margin-top:15px;';

                    modalContent.appendChild(closeBtn);
                    modalContent.appendChild(modalTitle);
                    modalContent.appendChild(modalText);
                    modal.appendChild(modalContent);
                    document.body.appendChild(modal);

                    window.onclick = function(event) {
                        if (event.target == modal) modal.style.display = 'none';
                    };
                }

                document.getElementById('modal-title').textContent = "🧵 Post ID: " + post_id + " — " + title;
                document.getElementById('modal-text').textContent = "📄 Post Content: " + text;
                modal.style.display = 'block';
            }
        });
    });
    """

    html_content = fig.to_html(
        include_plotlyjs=True,
        full_html=True,
        include_mathjax=False,
        post_script=post_script
    )

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path

def load_or_generate_visualization(df: pd.DataFrame, embeddings: np.ndarray, labels: np.ndarray,
                                  persona: str, subreddit_filename: str) -> str:
    visualization_path = get_visualization_path(persona, subreddit_filename)

    if os.path.exists(visualization_path):
        print(f"✅ Loading cached cluster visualization for {persona} - {subreddit_filename}")
        return visualization_path
    else:
        print(f"🔄 No cached visualization found. Generating visualization for {persona} - {subreddit_filename}...")
        print("📊 Reducing embeddings to 2D for visualization...")
        embeddings_2d = reduce_to_2d(embeddings)

        print("🎨 Creating interactive cluster visualization...")
        fig = create_interactive_plot(df, embeddings_2d, labels)

        output_path = save_visualization(fig, persona, subreddit_filename)
        print(f"📁 Saved interactive visualization to: {output_path}")
        return output_path
