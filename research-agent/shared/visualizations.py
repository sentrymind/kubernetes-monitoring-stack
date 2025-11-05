"""
Visualization module for research papers
"""
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import networkx as nx
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from .models import Paper
from .analytics import ResearchAnalytics
from .utils import setup_logging

logger = setup_logging(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ResearchVisualizer:
    """Visualizer for research papers"""

    def __init__(self, output_dir: str = "visualizations"):
        """
        Initialize visualizer

        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_timeline(
        self,
        papers: List[Paper],
        title: str = "Publication Timeline"
    ) -> str:
        """
        Create publication timeline visualization

        Args:
            papers: List of papers
            title: Plot title

        Returns:
            Path to saved image
        """
        analytics = ResearchAnalytics(papers)
        timeline = analytics.get_publication_timeline()

        if not timeline:
            logger.warning("No timeline data available")
            return None

        # Create plotly figure
        years = sorted(timeline.keys())
        counts = [timeline[y] for y in years]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=years,
            y=counts,
            mode='lines+markers',
            name='Publications',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            hovermode='x unified',
            template='plotly_white'
        )

        # Save
        filename = f"timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)

        logger.info(f"Timeline saved to {filepath}")
        return filepath

    def plot_wordcloud(
        self,
        papers: List[Paper],
        title: str = "Keyword Cloud"
    ) -> str:
        """
        Create word cloud from keywords

        Args:
            papers: List of papers
            title: Plot title

        Returns:
            Path to saved image
        """
        analytics = ResearchAnalytics(papers)
        keywords = analytics.extract_trending_keywords(top_n=100)

        if not keywords:
            logger.warning("No keywords found")
            return None

        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(keywords)

        # Plot
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=20, pad=20)
        plt.tight_layout(pad=0)

        # Save
        filename = f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Word cloud saved to {filepath}")
        return filepath

    def plot_coauthor_network(
        self,
        papers: List[Paper],
        min_collaborations: int = 2,
        max_nodes: int = 50
    ) -> str:
        """
        Create co-author network visualization

        Args:
            papers: List of papers
            min_collaborations: Minimum collaborations to show edge
            max_nodes: Maximum number of nodes to display

        Returns:
            Path to saved image
        """
        analytics = ResearchAnalytics(papers)
        edges = analytics.get_coauthor_network()

        if not edges:
            logger.warning("No collaboration data available")
            return None

        # Filter by minimum collaborations
        edges = [(a1, a2, w) for a1, a2, w in edges if w >= min_collaborations]

        if not edges:
            logger.warning("No edges after filtering")
            return None

        # Create network graph
        G = nx.Graph()

        for author1, author2, weight in edges:
            G.add_edge(author1, author2, weight=weight)

        # Limit to top nodes by degree
        if len(G.nodes()) > max_nodes:
            top_nodes = sorted(
                G.degree(),
                key=lambda x: x[1],
                reverse=True
            )[:max_nodes]
            top_node_names = [n for n, _ in top_nodes]
            G = G.subgraph(top_node_names).copy()

        if len(G.nodes()) == 0:
            logger.warning("Network is empty after filtering")
            return None

        # Create layout
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Extract coordinates
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_x = []
        node_y = []
        node_text = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"{node}<br>Collaborations: {G.degree(node)}")
            node_size.append(G.degree(node) * 3 + 10)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[n.split()[-1] for n in G.nodes()],  # Show last name
            textposition="top center",
            hovertext=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=node_size,
                color=node_size,
                colorbar=dict(
                    thickness=15,
                    title='Collaborations',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2, color='white')
            )
        )

        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title='Co-Author Collaboration Network',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                template='plotly_white'
            )
        )

        # Save
        filename = f"coauthor_network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)

        logger.info(f"Co-author network saved to {filepath}")
        return filepath

    def plot_keyword_trends(
        self,
        papers: List[Paper],
        keywords: List[str] = None,
        top_n: int = 5
    ) -> str:
        """
        Plot keyword trends over time

        Args:
            papers: List of papers
            keywords: Specific keywords to track
            top_n: Number of top keywords if auto-detecting

        Returns:
            Path to saved image
        """
        analytics = ResearchAnalytics(papers)
        trends = analytics.get_keyword_trends_by_year(keywords=keywords, top_n=top_n)

        if not trends:
            logger.warning("No trend data available")
            return None

        fig = go.Figure()

        for keyword, yearly_counts in trends.items():
            if not yearly_counts:
                continue

            years = sorted(yearly_counts.keys())
            counts = [yearly_counts[y] for y in years]

            fig.add_trace(go.Scatter(
                x=years,
                y=counts,
                mode='lines+markers',
                name=keyword,
                hovertemplate=f'<b>{keyword}</b><br>Year: %{{x}}<br>Count: %{{y}}<extra></extra>'
            ))

        fig.update_layout(
            title='Keyword Trends Over Time',
            xaxis_title='Year',
            yaxis_title='Number of Papers',
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        # Save
        filename = f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)

        logger.info(f"Keyword trends saved to {filepath}")
        return filepath

    def plot_source_distribution(self, papers: List[Paper]) -> str:
        """
        Plot distribution of papers by source

        Args:
            papers: List of papers

        Returns:
            Path to saved image
        """
        analytics = ResearchAnalytics(papers)
        distribution = analytics.get_source_distribution()

        if not distribution:
            return None

        fig = go.Figure(data=[
            go.Pie(
                labels=list(distribution.keys()),
                values=list(distribution.values()),
                hole=0.3,
                marker=dict(colors=['#2E86AB', '#A23B72', '#F18F01'])
            )
        ])

        fig.update_layout(
            title='Papers by Source',
            template='plotly_white'
        )

        # Save
        filename = f"sources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        fig.write_html(filepath)

        logger.info(f"Source distribution saved to {filepath}")
        return filepath
