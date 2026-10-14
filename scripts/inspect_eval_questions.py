
import pandas as pd

questions = pd.read_csv("data/evaluation/questions.csv")

print(f"Total questions: {len(questions)}")
print("\nQuestions by category:")
print(questions["category"].value_counts())

print("\nQuestions:")
for _, row in questions.iterrows():
    print(f"{row['id']}: {row['question']}")
