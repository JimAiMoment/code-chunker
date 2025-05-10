"""
RAG (Retrieval-Augmented Generation) integration example
"""

from code_chunker import CodeChunker
from typing import List, Dict
import json

# Simulated vector store for demonstration
class SimpleVectorStore:
    """A simple vector store simulation"""
    
    def __init__(self):
        self.documents = []
    
    def add_document(self, doc_id: str, content: str, metadata: Dict):
        """Add a document to the store"""
        self.documents.append({
            'id': doc_id,
            'content': content,
            'metadata': metadata
        })
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simulate search (in real implementation, this would use embeddings)"""
        # This is a simplified search - in practice, you'd use vector similarity
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if query_lower in doc['content'].lower():
                results.append(doc)
        
        return results[:top_k]

def prepare_code_for_rag(code_path: str) -> List[Dict]:
    """Prepare code for RAG by chunking and creating metadata"""
    chunker = CodeChunker()
    
    # Parse the code file
    result = chunker.parse_file(code_path)
    
    # Create documents for vector store
    documents = []
    
    for i, chunk in enumerate(result.chunks):
        doc_id = f"{code_path}_chunk_{i}"
        
        # Create rich metadata
        metadata = {
            'file_path': result.file_path,
            'language': result.language,
            'chunk_type': chunk.type.value,
            'chunk_name': chunk.name,
            'start_line': chunk.start_line,
            'end_line': chunk.end_line,
            'confidence': chunk.confidence
        }
        
        # Add any custom metadata from the chunk
        if chunk.metadata:
            metadata.update(chunk.metadata)
        
        # Create a context-rich content
        content = f"""
File: {result.file_path}
Language: {result.language}
Type: {chunk.type.value}
Name: {chunk.name}
Lines: {chunk.start_line}-{chunk.end_line}

Code:
{chunk.code}
"""
        
        documents.append({
            'id': doc_id,
            'content': content,
            'metadata': metadata
        })
    
    return documents

def build_rag_context(query: str, vector_store: SimpleVectorStore) -> str:
    """Build context for RAG from search results"""
    # Search for relevant code chunks
    results = vector_store.search(query, top_k=3)
    
    if not results:
        return "No relevant code found."
    
    # Build context
    context_parts = []
    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        context_parts.append(f"""
Result {i}:
File: {metadata['file_path']}
Type: {metadata['chunk_type']} - {metadata['chunk_name']}
Lines: {metadata['start_line']}-{metadata['end_line']}

{result['content']}
""")
    
    return "\n".join(context_parts)

# Example usage
if __name__ == '__main__':
    # Initialize vector store
    vector_store = SimpleVectorStore()
    
    # Example: Index a Python file
    sample_code = """
class DocumentProcessor:
    def __init__(self, config):
        self.config = config
        self.embedder = None
    
    def process_document(self, document):
        '''Process a document and extract embeddings'''
        if not self.embedder:
            self.embedder = self._create_embedder()
        
        chunks = self._chunk_document(document)
        embeddings = [self.embedder.embed(chunk) for chunk in chunks]
        
        return {
            'chunks': chunks,
            'embeddings': embeddings
        }
    
    def _chunk_document(self, document):
        '''Split document into chunks'''
        # Simple chunking logic
        return document.split('\\n\\n')
    
    def _create_embedder(self):
        '''Create embedding model'''
        return SimpleEmbedder(self.config.get('model_name'))

class SimpleEmbedder:
    def __init__(self, model_name):
        self.model_name = model_name
    
    def embed(self, text):
        '''Generate embedding for text'''
        # Simulated embedding
        return [0.1] * 768  # Mock 768-dimensional vector
"""
    
    # Save sample code to a temporary file for demonstration
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(sample_code)
        temp_file = f.name
    
    try:
        # Prepare code for RAG
        documents = prepare_code_for_rag(temp_file)
        
        # Add documents to vector store
        for doc in documents:
            vector_store.add_document(
                doc['id'],
                doc['content'],
                doc['metadata']
            )
        
        # Example queries
        queries = [
            "How to create embeddings?",
            "What does process_document do?",
            "How to chunk documents?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 50)
            context = build_rag_context(query, vector_store)
            print(context)
            
            # In a real RAG system, you would now pass this context
            # along with the query to an LLM for generation
            
    finally:
        # Clean up
        os.unlink(temp_file)
    
    # Example: Analyzing a project for RAG
    print("\n\nProject Analysis for RAG:")
    print("=" * 50)
    
    # You would replace this with actual project path
    # project_documents = prepare_project_for_rag('/path/to/project')
    
    # Show statistics
    print(f"Total documents prepared: {len(vector_store.documents)}")
    
    # Group by type
    type_counts = {}
    for doc in vector_store.documents:
        chunk_type = doc['metadata']['chunk_type']
        type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
    
    print("\nDocument types:")
    for chunk_type, count in type_counts.items():
        print(f"  {chunk_type}: {count}")

def prepare_project_for_rag(project_path: str) -> List[Dict]:
    """Prepare an entire project for RAG"""
    chunker = CodeChunker()
    all_documents = []
    
    # Parse all files in the project
    results = chunker.parse_directory(project_path, recursive=True)
    
    for result in results:
        for i, chunk in enumerate(result.chunks):
            doc_id = f"{result.file_path}_chunk_{i}"
            
            metadata = {
                'file_path': result.file_path,
                'language': result.language,
                'chunk_type': chunk.type.value,
                'chunk_name': chunk.name,
                'start_line': chunk.start_line,
                'end_line': chunk.end_line,
                'confidence': chunk.confidence
            }
            
            content = f"""
File: {result.file_path}
Language: {result.language}
Type: {chunk.type.value}
Name: {chunk.name}

{chunk.code}
"""
            
            all_documents.append({
                'id': doc_id,
                'content': content,
                'metadata': metadata
            })
    
    return all_documents
