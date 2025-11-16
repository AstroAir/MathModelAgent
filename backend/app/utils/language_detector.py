"""Language detection utility for automatic language identification"""

import re
from typing import Literal

def detect_language(text: str) -> Literal["zh", "en"]:
    """Detect language from text content
    
    Uses heuristics to determine if text is primarily Chinese or English:
    - Checks for Chinese characters (CJK Unified Ideographs)
    - Counts ratio of Chinese vs ASCII characters
    - Returns 'zh' for Chinese, 'en' for English
    
    Args:
        text: Input text to analyze
        
    Returns:
        'zh' for Chinese, 'en' for English
    """
    if not text or not text.strip():
        return "en"  # Default to English for empty text
    
    # Remove whitespace for analysis
    text_clean = text.strip()
    
    # Count Chinese characters (CJK Unified Ideographs range)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text_clean)
    chinese_count = len(chinese_chars)
    
    # Count English/ASCII letters
    english_chars = re.findall(r'[a-zA-Z]', text_clean)
    english_count = len(english_chars)
    
    # Count total characters (excluding whitespace and punctuation)
    total_chars = chinese_count + english_count
    
    if total_chars == 0:
        return "en"  # Default to English if no identifiable characters
    
    # Calculate Chinese character ratio
    chinese_ratio = chinese_count / total_chars
    
    # If more than 30% Chinese characters, consider it Chinese
    # This threshold works well for mixed content
    if chinese_ratio > 0.3:
        return "zh"
    else:
        return "en"


def detect_language_detailed(text: str) -> dict:
    """Detect language with detailed analysis
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with detection details including:
        - language: Detected language ('zh' or 'en')
        - confidence: Confidence score (0-1)
        - chinese_ratio: Ratio of Chinese characters
        - chinese_count: Number of Chinese characters
        - english_count: Number of English letters
    """
    if not text or not text.strip():
        return {
            "language": "en",
            "confidence": 0.5,
            "chinese_ratio": 0.0,
            "chinese_count": 0,
            "english_count": 0
        }
    
    text_clean = text.strip()
    
    # Count characters
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text_clean)
    chinese_count = len(chinese_chars)
    
    english_chars = re.findall(r'[a-zA-Z]', text_clean)
    english_count = len(english_chars)
    
    total_chars = chinese_count + english_count
    
    if total_chars == 0:
        return {
            "language": "en",
            "confidence": 0.5,
            "chinese_ratio": 0.0,
            "chinese_count": 0,
            "english_count": 0
        }
    
    chinese_ratio = chinese_count / total_chars
    
    # Determine language and confidence
    if chinese_ratio > 0.3:
        language = "zh"
        # Higher confidence as ratio increases
        confidence = min(0.6 + (chinese_ratio * 0.4), 1.0)
    else:
        language = "en"
        # Higher confidence as English ratio increases
        english_ratio = english_count / total_chars
        confidence = min(0.6 + (english_ratio * 0.4), 1.0)
    
    return {
        "language": language,
        "confidence": confidence,
        "chinese_ratio": chinese_ratio,
        "chinese_count": chinese_count,
        "english_count": english_count
    }


# Example usage and test cases
if __name__ == "__main__":
    test_cases = [
        ("这是一个中文问题，需要建立数学模型", "zh"),
        ("This is an English problem that requires mathematical modeling", "en"),
        ("Problem 1: 根据给定的数据建立模型", "zh"),  # Mixed but majority Chinese
        ("问题1: Build a model based on the given data", "zh"),  # Mixed but has Chinese
        ("Analyze the data and provide recommendations", "en"),
        ("", "en"),  # Empty defaults to English
    ]
    
    print("Language Detection Test Cases:")
    print("=" * 70)
    
    for text, expected in test_cases:
        detected = detect_language(text)
        detailed = detect_language_detailed(text)
        status = "✓" if detected == expected else "✗"
        
        print(f"\n{status} Text: {text[:50]}...")
        print(f"  Expected: {expected}, Detected: {detected}")
        print(f"  Confidence: {detailed['confidence']:.2%}")
        print(f"  Chinese ratio: {detailed['chinese_ratio']:.2%}")
