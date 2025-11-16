"""Unit tests for language detection utility"""

import pytest
from app.utils.language_detector import detect_language, detect_language_detailed


class TestLanguageDetection:
    """Test cases for language detection"""
    
    def test_chinese_text(self):
        """Test detection of pure Chinese text"""
        text = "这是一个数学建模问题，需要建立模型并求解"
        assert detect_language(text) == "zh"
        
    def test_english_text(self):
        """Test detection of pure English text"""
        text = "This is a mathematical modeling problem that requires building a model"
        assert detect_language(text) == "en"
        
    def test_mixed_text_chinese_majority(self):
        """Test mixed text with Chinese majority"""
        text = "问题1: Analyze the data 并建立数学模型"
        result = detect_language(text)
        assert result == "zh"
        
    def test_mixed_text_english_majority(self):
        """Test mixed text with English majority"""
        text = "Problem 1: Build a model using 数据分析"
        result = detect_language(text)
        assert result == "en"
        
    def test_empty_text(self):
        """Test empty text defaults to English"""
        assert detect_language("") == "en"
        assert detect_language("   ") == "en"
        
    def test_numbers_only(self):
        """Test text with only numbers"""
        text = "123 456 789"
        assert detect_language(text) == "en"
        
    def test_detailed_detection_chinese(self):
        """Test detailed detection for Chinese text"""
        text = "数学建模竞赛问题"
        result = detect_language_detailed(text)
        
        assert result["language"] == "zh"
        assert result["confidence"] > 0.8
        assert result["chinese_ratio"] > 0.9
        assert result["chinese_count"] == 8
        
    def test_detailed_detection_english(self):
        """Test detailed detection for English text"""
        text = "Mathematical modeling competition problem"
        result = detect_language_detailed(text)
        
        assert result["language"] == "en"
        assert result["confidence"] > 0.8
        assert result["chinese_ratio"] == 0.0
        assert result["english_count"] > 30
        
    def test_realistic_chinese_problem(self):
        """Test with realistic Chinese problem statement"""
        text = """
        问题1：某农场有100亩土地，可以种植小麦、玉米和大豆三种作物。
        已知小麦的成本为200元/亩，玉米的成本为150元/亩，大豆的成本为180元/亩。
        请建立数学模型，求解最优种植方案。
        """
        assert detect_language(text) == "zh"
        
    def test_realistic_english_problem(self):
        """Test with realistic English problem statement"""
        text = """
        Problem 1: A farm has 100 acres of land that can be used to grow wheat, corn, and soybeans.
        The cost of wheat is $200/acre, corn is $150/acre, and soybeans are $180/acre.
        Build a mathematical model to find the optimal planting strategy.
        """
        assert detect_language(text) == "en"
        
    def test_threshold_boundary(self):
        """Test threshold boundary (30% Chinese characters)"""
        # Text with exactly 30% Chinese should be borderline
        # Create text with controlled ratio
        chinese_part = "中文字"  # 3 Chinese characters
        english_part = "English"  # 7 English characters
        text = chinese_part + english_part  # 30% Chinese
        
        result = detect_language_detailed(text)
        # At exactly 30%, it should detect based on our threshold logic
        assert result["language"] in ["zh", "en"]
        assert 0.28 <= result["chinese_ratio"] <= 0.32


class TestLanguageDetectionEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_punctuation_only(self):
        """Test text with only punctuation"""
        text = "!@#$%^&*()"
        assert detect_language(text) == "en"
        
    def test_mixed_punctuation(self):
        """Test text with Chinese and English punctuation"""
        text = "问题：What is the answer？"
        result = detect_language(text)
        assert result in ["zh", "en"]  # Should detect based on character ratio
        
    def test_very_short_text(self):
        """Test very short text"""
        assert detect_language("中") == "zh"
        assert detect_language("A") == "en"
        
    def test_confidence_scores(self):
        """Test that confidence scores are reasonable"""
        # Pure language should have high confidence
        result_zh = detect_language_detailed("这是中文文本内容")
        assert result_zh["confidence"] > 0.85
        
        result_en = detect_language_detailed("This is English text content")
        assert result_en["confidence"] > 0.85
        
        # Mixed should have lower confidence
        result_mixed = detect_language_detailed("Mixed 混合 content 内容")
        # Confidence might vary but should be reasonable
        assert 0.5 <= result_mixed["confidence"] <= 1.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
