import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIGMA_BASE_URL = "https://api.figma.com/v1"

def get_headers():
    """Helper to get Figma API headers."""
    api_key = os.getenv("FIGMA_API_KEY")
    if not api_key:
        raise ValueError("FIGMA_API_KEY not found in environment variables")
    return {"X-Figma-Token": api_key}

def get_file_nodes(file_key: str, node_ids: str) -> str:
    """
    Get specific nodes from a Figma file.
    
    Args:
        file_key: The key of the Figma file (from the URL).
        node_ids: Comma-separated list of node IDs (e.g., "1:2,3:4").
    """
    url = f"{FIGMA_BASE_URL}/files/{file_key}/nodes?ids={node_ids}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    
    return response.text

def get_file_structure(file_key: str, depth: int = 1) -> str:
    """
    Get the file structure (document tree) to find Node IDs.
    
    Args:
        file_key: The key of the Figma file.
        depth: How deep to traverse the tree (default 1 to list pages/top-level frames).
    """
    url = f"{FIGMA_BASE_URL}/files/{file_key}?depth={depth}"
    response = requests.get(url, headers=get_headers())
    
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    
    return response.text

def post_comment(file_key: str, message: str, node_id: str = None) -> str:
    """
    Post a comment to a Figma file.
    
    Args:
        file_key: The key of the Figma file.
        message: The text of the comment.
        node_id: Optional node ID to attach the comment to.
    """
    url = f"{FIGMA_BASE_URL}/files/{file_key}/comments"
    payload = {"message": message}
    if node_id:
        payload["client_meta"] = {"node_id": node_id}
        
    response = requests.post(url, headers=get_headers(), json=payload)
    
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    
    return f"Comment posted successfully: {response.json().get('id')}"
