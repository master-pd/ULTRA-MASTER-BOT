"""
📊 DIAGRAM GENERATOR
Create diagrams from text automatically
"""

import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import networkx as nx
import plotly.graph_objects as go
from plotly.offline import plot
import html

class DiagramGenerator:
    def __init__(self):
        self.diagram_types = {
            "flowchart": self.create_flowchart,
            "pie_chart": self.create_pie_chart,
            "bar_chart": self.create_bar_chart,
            "mind_map": self.create_mindmap,
            "network": self.create_network,
            "timeline": self.create_timeline
        }
    
    def detect_diagram_type(self, text: str) -> str:
        """Detect appropriate diagram type from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["প্রক্রিয়া", "ধাপ", "সিকুয়েন্স", "ফ্লো", "process", "step", "sequence"]):
            return "flowchart"
        elif any(word in text_lower for word in ["শতকরা", "ভাগ", "অংশ", "percentage", "part", "share"]):
            return "pie_chart"
        elif any(word in text_lower for word in ["তুলনা", "পরিমাণ", "সংখ্যা", "comparison", "amount", "number"]):
            return "bar_chart"
        elif any(word in text_lower for word in ["ধারণা", "আইডিয়া", "মনের মানচিত্র", "idea", "concept", "mind"]):
            return "mind_map"
        elif any(word in text_lower for word in ["সম্পর্ক", "নেটওয়ার্ক", "কানেকশন", "relation", "network", "connection"]):
            return "network"
        elif any(word in text_lower for word in ["সময়", "ইতিহাস", "ক্রম", "time", "history", "chronology"]):
            return "timeline"
        else:
            return "mind_map"  # Default
    
    def extract_data_for_diagram(self, text: str, diagram_type: str) -> Dict:
        """Extract data from text for diagram"""
        # Simple extraction logic
        # In production, use NLP for better extraction
        
        words = text.split()
        keywords = [word for word in words if len(word) > 3][:10]
        
        data = {
            "title": " ".join(words[:5]),
            "labels": keywords[:5],
            "values": [len(word) * 10 for word in keywords[:5]],
            "connections": []
        }
        
        # Generate some random connections for network/mindmap
        if len(keywords) > 1:
            for i in range(len(keywords) - 1):
                data["connections"].append((keywords[i], keywords[i+1]))
        
        return data
    
    def create_flowchart(self, data: Dict) -> str:
        """Create flowchart diagram"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Simplified flowchart using boxes and arrows
        boxes = data["labels"]
        x_positions = range(len(boxes))
        
        for i, (box, x) in enumerate(zip(boxes, x_positions)):
            # Draw box
            rect = plt.Rectangle((x - 0.4, 0.6), 0.8, 0.3, 
                                fill=True, color='skyblue', edgecolor='navy', linewidth=2)
            ax.add_patch(rect)
            
            # Add text
            ax.text(x, 0.75, box, ha='center', va='center', 
                   fontsize=10, fontweight='bold', color='black')
            
            # Draw arrows
            if i < len(boxes) - 1:
                ax.arrow(x + 0.4, 0.75, 0.2, 0, 
                        head_width=0.05, head_length=0.05, 
                        fc='navy', ec='navy')
        
        ax.set_xlim(-0.5, len(boxes) - 0.5)
        ax.set_ylim(0, 1)
        ax.set_title(data.get("title", "Flowchart"), fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        # Convert to base64
        img_str = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def create_pie_chart(self, data: Dict) -> str:
        """Create pie chart"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = data["labels"]
        values = data["values"]
        
        # Colors
        colors = plt.cm.Set3(range(len(labels)))
        
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                         colors=colors, startangle=90)
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(data.get("title", "Pie Chart"), fontsize=14, fontweight='bold')
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        img_str = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def create_bar_chart(self, data: Dict) -> str:
        """Create bar chart"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = data["labels"]
        values = data["values"]
        
        bars = ax.bar(range(len(labels)), values, color='steelblue', edgecolor='navy')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom',
                   fontweight='bold')
        
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_title(data.get("title", "Bar Chart"), fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        img_str = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def create_mindmap(self, data: Dict) -> str:
        """Create mind map"""
        G = nx.Graph()
        
        # Add central node
        central = data.get("title", "Central Idea")
        G.add_node(central, size=3000, color='gold')
        
        # Add child nodes
        for i, label in enumerate(data["labels"]):
            G.add_node(label, size=1000, color='lightblue')
            G.add_edge(central, label)
        
        # Create connections
        for connection in data.get("connections", []):
            if connection[0] in G and connection[1] in G:
                G.add_edge(connection[0], connection[1])
        
        # Draw graph
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        node_colors = [G.nodes[n].get('color', 'lightblue') for n in G.nodes()]
        node_sizes = [G.nodes[n].get('size', 1000) for n in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        plt.title("Mind Map", fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Save to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        img_str = base64.b64encode(buffer.read()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def create_from_text(self, text: str) -> Dict:
        """Main function to create diagram from text"""
        diagram_type = self.detect_diagram_type(text)
        data = self.extract_data_for_diagram(text, diagram_type)
        
        # Generate diagram
        if diagram_type in self.diagram_types:
            diagram_image = self.diagram_types[diagram_type](data)
        else:
            diagram_image = self.create_mindmap(data)
        
        result = {
            "type": diagram_type,
            "title": data.get("title", "Diagram"),
            "data": data,
            "image_base64": diagram_image,
            "text": text,
            "timestamp": time.time(),
            "diagram_html": self.generate_html_diagram(diagram_type, data)
        }
        
        return result
    
    def generate_html_diagram(self, diagram_type: str, data: Dict) -> str:
        """Generate HTML for interactive diagram"""
        if diagram_type == "bar_chart":
            fig = go.Figure(data=[
                go.Bar(x=data["labels"], y=data["values"],
                      marker_color='royalblue')
            ])
            fig.update_layout(title=data.get("title", "Interactive Chart"))
            return plot(fig, output_type='div', include_plotlyjs=False)
        
        elif diagram_type == "pie_chart":
            fig = go.Figure(data=[
                go.Pie(labels=data["labels"], values=data["values"])
            ])
            fig.update_layout(title=data.get("title", "Interactive Pie Chart"))
            return plot(fig, output_type='div', include_plotlyjs=False)
        
        else:
            # Simple HTML table as fallback
            html_content = f"""
            <div class="diagram-container">
                <h3>{data.get('title', 'Diagram')}</h3>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #4CAF50; color: white;">
                        <th>Label</th>
                        <th>Value</th>
                    </tr>
            """
            
            for label, value in zip(data.get("labels", []), data.get("values", [])):
                html_content += f"""
                    <tr>
                        <td>{label}</td>
                        <td>{value}</td>
                    </tr>
                """
            
            html_content += "</table></div>"
            return html_content