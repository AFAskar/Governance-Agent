"""
Text Chunker Module
Chunks PDF text into manageable segments with overlap for vector database storage
"""

import re


def chunk_text(
    text: str,
    chunk_size: int = 1500,
    overlap: int = 200,
    framework_name: str | None = None,
    preserve_sentences: bool = True,
) -> list[dict]:
    """
    Split text into fixed-size chunks with overlap, preserving semantic boundaries.

    Improved version that:
    - Uses larger default chunk sizes (1500 chars) for better context
    - Preserves paragraph boundaries when possible
    - Filters out chunks that are mostly formatting artifacts
    - Better sentence boundary detection with larger lookback window

    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters (default: 1500)
        overlap: Number of characters to overlap between chunks (default: 200)
        framework_name: Optional framework name for metadata
        preserve_sentences: If True, try to break at sentence boundaries

    Returns:
        List of dictionaries, each containing:
        {
            "text": str,
            "chunk_id": int,
            "chunk_index": int,
            "framework_name": str,
            "metadata": dict
        }
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
            para_pattern = r"\n\s*\n+"
            para_breaks = list(re.finditer(para_pattern, lookback_text))

            if para_breaks:
                # Use the last paragraph break
                last_match = para_breaks[-1]
                end = lookback_start + last_match.end()
                chunk_text_segment = text[start:end]
            else:
                # Fall back to sentence endings
                # Improved sentence pattern: handles multiple punctuation and various newlines
                sentence_pattern = r"[.!?]+[\s\n]+|[.!?]+\n+"
                sentence_endings = list(re.finditer(sentence_pattern, lookback_text))

                if sentence_endings:
                    # Use the last sentence ending, but prefer those followed by uppercase
                    # (likely start of new sentence)
                    best_match = sentence_endings[-1]

                    # Check if there's a better break (sentence followed by uppercase letter)
                    for match in reversed(sentence_endings):
                        match_end = lookback_start + match.end()
                        if match_end < text_length:
                            next_char = text[match_end : match_end + 1].strip()
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
                    "overlap": overlap,
                },
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
    Check if a chunk is valid (not mostly formatting artifacts).

    Args:
        text: Chunk text to validate
        min_meaningful_chars: Minimum number of meaningful characters required

    Returns:
        True if chunk is valid, False if it's mostly formatting
    """
    if not text or len(text) < 20:
        return False

    # Remove common formatting patterns for analysis
    # Count non-whitespace, non-punctuation-only lines
    lines = text.split("\n")
    meaningful_lines = 0
    total_chars = 0
    meaningful_chars = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        total_chars += len(line)

        # Check if line is mostly dots/dashes (table of contents formatting)
        if re.match(r"^[.\-_\s]+$", stripped):
            continue

        # Check if line is mostly numbers/spaces (page numbers)
        if re.match(r"^\s*\d+\s*$", stripped) and len(stripped) < 10:
            continue

        # Count meaningful characters (letters, numbers, meaningful punctuation)
        meaningful = re.sub(r"[^\w\s]", "", stripped)
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
    text: str, sentences_per_chunk: int = 5, framework_name: str | None = None
) -> list[dict]:
    """
    Chunk text by sentences instead of fixed character size.

    Args:
        text: Text to chunk
        sentences_per_chunk: Number of sentences per chunk
        framework_name: Optional framework name for metadata

    Returns:
        List of chunk dictionaries
    """
    # Split into sentences
    sentence_pattern = r"[.!?]+\s+|[\n]{2,}"
    sentences = re.split(sentence_pattern, text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    chunk_id = 0

    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i : i + sentences_per_chunk]
        chunk_text_segment = " ".join(chunk_sentences)

        chunk_dict = {
            "text": chunk_text_segment,
            "chunk_id": chunk_id,
            "chunk_index": chunk_id,
            "framework_name": framework_name or "unknown",
            "metadata": {
                "sentence_start": i,
                "sentence_end": min(i + sentences_per_chunk, len(sentences)),
                "sentences_per_chunk": sentences_per_chunk,
                "length": len(chunk_text_segment),
            },
        }
        chunks.append(chunk_dict)
        chunk_id += 1

    return chunks
