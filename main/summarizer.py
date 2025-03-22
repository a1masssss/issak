from transformers import pipeline

import torch
device = torch.device("mps")

summarizer = pipeline(
    "summarization", model="facebook/bart-large-cnn", torch_dtype=torch.float32, device=device
)


def generate_summary(text):
    """Функция для генерации краткого пересказа текста"""
    summary = summarizer(text, max_length=300, min_length=100, do_sample=False)
    return summary[0]["summary_text"]
