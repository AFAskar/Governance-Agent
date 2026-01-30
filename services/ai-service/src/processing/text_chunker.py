"""
Text Chunker Module
Chunks PDF text into manageable segments with overlap for vector database storage
"""

from typing import List, Dict, Optional
import re


def chunk_text(
    text: str, 
    chunk_size: int = 1500, 
    overlap: int = 200,
    framework_name: Optional[str] = None,
    preserve_sentences: bool = True
) -> List[Dict]:
    """
    Split long text into overlapping chunks that prefer paragraph or sentence boundaries.
    
    The function produces sequential text segments of up to `chunk_size` characters with `overlap` between adjacent segments. When `preserve_sentences` is True the function attempts to end chunks at paragraph breaks (double newlines) or sentence boundaries within a lookback window; resulting chunks that are mostly formatting artifacts are discarded.
    
    Parameters:
        text (str): Input text to split.
        chunk_size (int): Maximum number of characters per chunk (default 1500).
        overlap (int): Number of characters to overlap between consecutive chunks (default 200).
        framework_name (Optional[str]): Optional label included in each chunk's metadata; "unknown" if omitted.
        preserve_sentences (bool): If True, prefer paragraph or sentence boundaries when choosing chunk end positions.
    
    Returns:
        List[dict]: A list of chunk dictionaries. Each dictionary contains:
            - "text" (str): Chunk content.
            - "chunk_id" (int): Sequential chunk identifier.
            - "chunk_index" (int): Alias of chunk_id.
            - "framework_name" (str): Provided framework name or "unknown".
            - "metadata" (dict): Includes "start_char", "end_char", "length", "chunk_size", and "overlap".
    """
    if not text or len(text.strip()) == 0:
        return []
    
    chunks = []
    chunk_id = 0
    start = 0
    text_length = len(text)
    
    # Lookback window for finding sentence/paragraph boundaries (20% of chunk_size)
    lookback_window = max(200, int(chunk_size * 0.2))
    
    while start < text_length:
        # Calculate end position
        end = min(start + chunk_size, text_length)
        
        # Extract chunk text
        chunk_text_segment = text[start:end]
        
        # If preserving sentences and not at the end, try to break at semantic boundary
        if preserve_sentences and end < text_length:
            # Look for paragraph breaks first (double newlines)
            lookback_start = max(start, end - lookback_window)
            lookback_text = text[lookback_start:end]
            
            # Try paragraph breaks first (double newline or newline followed by section header)
            para_pattern = r'\n\s*\n+'
            para_breaks = list(re.finditer(para_pattern, lookback_text))
            
            if para_breaks:
                # Use the last paragraph break
                last_match = para_breaks[-1]
                end = lookback_start + last_match.end()
                chunk_text_segment = text[start:end]
            else:
                # Fall back to sentence endings
                # Improved sentence pattern: handles multiple punctuation and various newlines
                sentence_pattern = r'[.!?]+[\s\n]+|[.!?]+\n+'
                sentence_endings = list(re.finditer(sentence_pattern, lookback_text))
                
                if sentence_endings:
                    # Use the last sentence ending, but prefer those followed by uppercase
                    # (likely start of new sentence)
                    best_match = sentence_endings[-1]
                    
                    # Check if there's a better break (sentence followed by uppercase letter)
                    for match in reversed(sentence_endings):
                        match_end = lookback_start + match.end()
                        if match_end < text_length:
                            next_char = text[match_end:match_end+1].strip()
                            if next_char and next_char.isupper():
                                best_match = match
                                break
                    
                    end = lookback_start + best_match.end()
                    chunk_text_segment = text[start:end]
        
        # Clean up chunk text
        chunk_text_segment = chunk_text_segment.strip()
        
        # Filter out chunks that are mostly formatting artifacts
        if chunk_text_segment and _is_valid_chunk(chunk_text_segment):
            chunk_dict = {
                "text": chunk_text_segment,
                "chunk_id": chunk_id,
                "chunk_index": chunk_id,
                "framework_name": framework_name or "unknown",
                "metadata": {
                    "start_char": start,
                    "end_char": end,
                    "length": len(chunk_text_segment),
                    "chunk_size": chunk_size,
                    "overlap": overlap
                }
            }
            chunks.append(chunk_dict)
            chunk_id += 1
        
        # Move start position with overlap
        # Make sure we don't go backwards
        new_start = end - overlap if end < text_length else end
        start = max(start + 1, new_start)  # Ensure progress
        
        # Prevent infinite loop
        if start >= text_length:
            break
        if start == end - overlap and overlap == 0:
            start = end  # Force progress if no overlap
    
    return chunks


def _is_valid_chunk(text: str, min_meaningful_chars: int = 100) -> bool:
    """
    Determine whether a text chunk contains sufficient meaningful content versus formatting artifacts.
    
    Accepts a chunk only if it has at least one meaningful line, the ratio of meaningful characters to total characters is at least 0.3, and the total meaningful characters are at least min_meaningful_chars. Chunks shorter than 20 characters are rejected.
    
    Parameters:
        text: Chunk text to evaluate.
        min_meaningful_chars: Minimum count of meaningful characters required for acceptance.
    
    Returns:
        True if the chunk is considered meaningful, False otherwise.
    """
    if not text or len(text) < 20:
        return False
    
    # Remove common formatting patterns for analysis
    # Count non-whitespace, non-punctuation-only lines
    lines = text.split('\n')
    meaningful_lines = 0
    total_chars = 0
    meaningful_chars = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        total_chars += len(line)
        
        # Check if line is mostly dots/dashes (table of contents formatting)
        if re.match(r'^[.\-_\s]+$', stripped):
            continue
        
        # Check if line is mostly numbers/spaces (page numbers)
        if re.match(r'^\s*\d+\s*$', stripped) and len(stripped) < 10:
            continue
        
        # Count meaningful characters (letters, numbers, meaningful punctuation)
        meaningful = re.sub(r'[^\w\s]', '', stripped)
        if len(meaningful.strip()) > 5:
            meaningful_lines += 1
            meaningful_chars += len(meaningful)
    
    # Reject if too many formatting-only lines
    if meaningful_lines == 0:
        return False
    
    # Reject if meaningful content is too low
    meaningful_ratio = meaningful_chars / max(total_chars, 1)
    if meaningful_ratio < 0.3:  # Less than 30% meaningful content
        return False
    
    # Reject if chunk is too short after filtering
    if meaningful_chars < min_meaningful_chars:
        return False
    
    return True

# not used anymore
def chunk_text_by_sentences(
    text: str,
    sentences_per_chunk: int = 5,
    framework_name: Optional[str] = None
) -> List[Dict]:
    """
    Split text into chunks where each chunk contains a fixed number of sentences.
    
    Sentences are detected by runs of sentence-ending punctuation followed by whitespace (e.g., ". ", "! ", "? ") or by double newlines; empty fragments are ignored.
    
    Parameters:
        text (str): Input text to split.
        sentences_per_chunk (int): Number of sentences to include in each chunk.
        framework_name (Optional[str]): Optional label stored in each chunk's `framework_name` field; defaults to `"unknown"` when not provided.
    
    Returns:
        List[Dict]: A list of chunk dictionaries. Each dictionary contains:
            - text: chunk text (joined sentences).
            - chunk_id: numeric chunk identifier.
            - chunk_index: numeric chunk index (same as `chunk_id`).
            - framework_name: provided framework name or `"unknown"`.
            - metadata: dict with `sentence_start`, `sentence_end`, `sentences_per_chunk`, and `length` (character count of the chunk text).
    """
    # Split into sentences
    sentence_pattern = r'[.!?]+\s+|[\n]{2,}'
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    chunks = []
    chunk_id = 0
    
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk_text_segment = ' '.join(chunk_sentences)
        
        chunk_dict = {
            "text": chunk_text_segment,
            "chunk_id": chunk_id,
            "chunk_index": chunk_id,
            "framework_name": framework_name or "unknown",
            "metadata": {
                "sentence_start": i,
                "sentence_end": min(i + sentences_per_chunk, len(sentences)),
                "sentences_per_chunk": sentences_per_chunk,
                "length": len(chunk_text_segment)
            }
        }
        chunks.append(chunk_dict)
        chunk_id += 1
    
    return chunks