"""
Text Skill - Text processing and manipulation
"""

def count_words(text: str) -> int:
    """Count words in text"""
    return len(text.split())

def summarize(text: str, max_length: int = 100) -> str:
    """Create a summary of text"""
    sentences = text.split('. ')
    summary_sentences = []
    for sentence in sentences:
        if len('. '.join(summary_sentences)) + len(sentence) < max_length:
            summary_sentences.append(sentence)
        else:
            break
    return '. '.join(summary_sentences) + '.'

def extract_keywords(text: str) -> list:
    """Extract keywords from text"""
    words = text.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'be'}
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    return list(set(keywords))[:10]

SKILL_METADATA = {
    "name": "text_skill",
    "version": "1.0.0",
    "description": "Text processing and analysis utilities",
    "functions": ["count_words", "summarize", "extract_keywords"],
    "tags": ["nlp", "text", "processing"]
}
