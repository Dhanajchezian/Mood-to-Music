import unittest
from text_mood_detector import detect_mood_from_text

class TestMoodDetection(unittest.TestCase):
    def test_happy_mood(self):
        """Test detection of happy mood through various expressions"""
        test_cases = [
            "I'm feeling amazing today!",
            "This is absolutely wonderful!",
            "I'm so thrilled with the results",
            "What a fantastic day!",
            "I'm overjoyed by this news"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "happy")

    def test_relaxed_mood(self):
        """Test detection of relaxed mood through various expressions"""
        test_cases = [
            "I'm feeling pretty good about this",
            "Everything is going smoothly",
            "I'm quite content with how things are",
            "Feeling calm and collected",
            "This is a pleasant situation"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "relaxed")

    def test_neutral_mood(self):
        """Test detection of neutral mood through various expressions"""
        test_cases = [
            "Just an average day",
            "Nothing special happening",
            "It's a typical situation",
            "Business as usual",
            "Neither good nor bad"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "neutral")

    def test_sad_mood(self):
        """Test detection of sad mood through various expressions"""
        test_cases = [
            "I can't stop crying",
            "I'm feeling down today",
            "This is so disappointing",
            "I'm really upset about this",
            "Feeling blue and lonely"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "sad")

    def test_anxious_mood(self):
        """Test detection of anxious mood through various expressions"""
        test_cases = [
            "I'm feeling very anxious about my exam tomorrow",
            "This situation is making me nervous",
            "I'm worried about the outcome",
            "I'm terrified of what might happen",
            "This is absolutely terrible"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "anxious")

    def test_excited_mood(self):
        """Test detection of excited mood through various expressions"""
        test_cases = [
            "I'm excited about the upcoming concert",
            "I'm so pumped for this event",
            "I'm thrilled about the opportunity",
            "I'm eager to get started",
            "I'm enthusiastic about the project"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "excited")

    def test_nostalgic_mood(self):
        """Test detection of nostalgic mood through various expressions"""
        test_cases = [
            "I feel nostalgic about my childhood",
            "Remembering the good old days",
            "I miss those times",
            "Looking back fondly on the past",
            "Those were the days"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "nostalgic")

    def test_romantic_mood(self):
        """Test detection of romantic mood through various expressions"""
        test_cases = [
            "I'm in a romantic mood this evening",
            "I'm feeling loving and affectionate",
            "I'm smitten with this person",
            "I'm enchanted by their presence",
            "I'm passionate about our relationship"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "romantic")

    def test_edge_cases(self):
        """Test edge cases and unusual inputs"""
        test_cases = [
            ("", "neutral"),  # Empty string
            ("   ", "neutral"),  # Whitespace only
            ("12345", "neutral"),  # Numbers only
            ("!@#$%", "neutral"),  # Special characters only
            ("I'm feeling happy and sad at the same time", "happy")  # Mixed emotions
        ]
        for text, expected in test_cases:
            self.assertEqual(detect_mood_from_text(text), expected)

    def test_case_insensitivity(self):
        """Test that mood detection is case insensitive"""
        test_cases = [
            "I'M FEELING HAPPY TODAY!",
            "i'm feeling happy today!",
            "I'm Feeling Happy Today!",
            "I'M FEELING HAPPY TODAY!"
        ]
        for text in test_cases:
            self.assertEqual(detect_mood_from_text(text), "happy")

if __name__ == '__main__':
    unittest.main() 