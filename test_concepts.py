from utils.concept_extractor import extract_topics

sample = """
Machine learning is a field of artificial intelligence that uses statistical techniques
to give computer systems the ability to "learn" from data without being explicitly programmed.
Key algorithms include linear regression, decision trees, clustering, and neural networks.
"""

topics = extract_topics(sample, top_n=5)
print("Extracted topics:", topics)
