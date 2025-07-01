import textstat
import statistics
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List
import re

analyzer = SentimentIntensityAnalyzer()

def extract_features_from_emails(emails: List[str]) -> dict:
    all_sentences = []
    all_words = []
    polarities = []
    subjectivities = []
    passive_count = 0
    questions = 0

    for email in emails:
        sentences = sent_tokenize(email, language="english")
        all_sentences.extend(sentences)
        all_words.extend(word_tokenize(email))

        for sentence in sentences:
            vs = analyzer.polarity_scores(sentence)
            polarities.append(vs['compound'])
            subjectivities.append(vs['neu'])
            if sentence.strip().endswith('?'):
                questions += 1

        passive_count += len(re.findall(r"\b(is|was|were|are|been) [a-z]+ed\b", email))

    avg_sentence_len = sum(len(word_tokenize(s)) for s in all_sentences) / len(all_sentences) if all_sentences else 0
    reading_grade = textstat.flesch_kincaid_grade(' '.join(all_sentences))
    question_ratio = questions / len(all_sentences) if all_sentences else 0

    return {
        "avg_sentence_length": round(avg_sentence_len, 2),
        "reading_grade_level": round(reading_grade, 2),
        "passive_voice_ratio": round(passive_count / len(all_sentences), 3) if all_sentences else 0,
        "question_ratio": round(question_ratio, 3),
        "polarity_mean": round(statistics.mean(polarities), 3) if polarities else 0,
        "polarity_std": round(statistics.stdev(polarities), 3) if len(polarities) > 1 else 0,
        "subjectivity_mean": round(statistics.mean(subjectivities), 3) if subjectivities else 0
    }
