"""
Code structure visualization
"""

import json
from code_chunker import CodeChunker
from code_chunker.models import ChunkType
from pathlib import Path

def generate_mermaid_diagram(result):
    """Generate Mermaid diagram from parse result
    
    Args:
        result: Parse result
        
    Returns:
        Mermaid diagram code
    """
    lines = ["graph TD"]
    
    # Group by type
    by_type = {}
    for chunk in result.chunks:
        chunk_type = chunk.type.value
        if chunk_type not in by_type:
            by_type[chunk_type] = []
        by_type[chunk_type].append(chunk)
    
    # Generate nodes
    node_id = 0
    node_map = {}
    
    for chunk_type, chunks in by_type.items():
        for i, chunk in enumerate(chunks):
            node_id += 1
            chunk_id = f"{chunk_type}_{i}"
            node_map[chunk_id] = f"node{node_id}"
            label = f"{chunk.name or 'unnamed'}"
            lines.append(f"    node{node_id}[{label}]")
    
    # Analyze dependencies (simplified)
    for i, chunk in enumerate(result.chunks):
        chunk_id = f"{chunk.type.value}_{i}"
        if chunk.type.value == 'method' and chunk.metadata.get('class_name'):
            # Find parent class
            for j, class_chunk in enumerate(result.chunks):
                class_chunk_id = f"{class_chunk.type.value}_{j}"
                if class_chunk.type.value == 'class' and class_chunk.name == chunk.metadata['class_name']:
                    lines.append(f"    {node_map[class_chunk_id]} --> {node_map[chunk_id]}")
                    break
    
    # Styles
    lines.extend([
        "    classDef classStyle fill:#f9d71c,stroke:#333,stroke-width:2px;",
        "    classDef functionStyle fill:#7dd3c0,stroke:#333,stroke-width:2px;",
        "    classDef methodStyle fill:#93c5fd,stroke:#333,stroke-width:2px;"
    ])
    
    # Apply styles
    for chunk_type, chunks in by_type.items():
        if chunk_type == 'class':
            style = 'classStyle'
        elif chunk_type == 'function':
            style = 'functionStyle'
        elif chunk_type == 'method':
            style = 'methodStyle'
        else:
            continue
            
        node_ids = [node_map[f"{chunk_type}_{i}"] for i in range(len(chunks))]
        if node_ids:
            lines.append(f"    class {','.join(node_ids)} {style}")
    
    return '\n'.join(lines)

def create_visualization(file_path: str):
    """Create code structure visualization
    
    Args:
        file_path: Path to the file to visualize
        
    Returns:
        Path to the generated HTML file
    """
    chunker = CodeChunker()
    result = chunker.parse_file(file_path)
    
    # Generate Mermaid diagram
    mermaid_code = generate_mermaid_diagram(result)
    
    # Generate HTML
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Structure Visualization</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </head>
    <body>
        <h1>Code Structure: {file_name}</h1>
        <div class="mermaid">
{mermaid_code}
        </div>
        
        <h2>Statistics</h2>
        <ul>
            <li>Total chunks: {total_chunks}</li>
            <li>Functions: {functions}</li>
            <li>Classes: {classes}</li>
            <li>Methods: {methods}</li>
        </ul>
    </body>
    </html>
    """
    
    # Statistics
    stats = {
        'total_chunks': len(result.chunks),
        'functions': len([c for c in result.chunks if c.type == ChunkType.FUNCTION]),
        'classes': len([c for c in result.chunks if c.type == ChunkType.CLASS]),
        'methods': len([c for c in result.chunks if c.type == ChunkType.METHOD]),
    }
    
    html_content = html_template.format(
        file_name=Path(file_path).name,
        mermaid_code=mermaid_code,
        **stats
    )
    
    # Write HTML file
    output_file = f"{Path(file_path).stem}_structure.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Visualization created: {output_file}")
    
    return output_file

if __name__ == '__main__':
    # Test visualization
    import sys
    if len(sys.argv) > 1:
        create_visualization(sys.argv[1])
    else:
        print("Usage: python visualization.py <file_path>") 