"""Code to handle the GPT-2 side of evaluation.
Uses the HuggingFace implementations of GPT-2.
Currently uses CPU because speed is not yet a concern.
"""
from __future__ import annotations
from collections import defaultdict
from typing_extensions import Literal
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import torch
from pprint import pprint


GPT2Size = Literal["gpt2", "gpt2-medium", "gpt2-large", "gpt2-xl"]


class GPT2Wrapper:
    token_pairs = [("ĠYes", "ĠNo")]

    def __init__(self, size: GPT2Size) -> None:
        self.model = GPT2LMHeadModel.from_pretrained(size)
        self.tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        self.id2token = {i: t for t, i in self.tokenizer.vocab.items()}

    def get_positive_prob(self, text: str) -> float:
        """Return the probability that the answer to the question is in the affirmative.
        For now, we just check the tokens for " Yes" and " No", but more sophisticated schemes are
        possible with e.g. averaging over pairs of answers"""
        logits = self.get_logits(text)
        # TODO: replace this with a loop over token pairs
        positive_token, negative_token = self.token_pairs[0]
        positive_logit = logits[positive_token]
        negative_logit = logits[negative_token]
        positive_prob, negative_prob = torch.nn.functional.softmax(
            torch.Tensor([positive_logit, negative_logit]), dim=-1
        )
        return positive_prob

    def get_logits(self, text: str) -> dict[str, float]:
        encoded_input = self.tokenizer(text, return_tensors="pt")
        output = self.model(**encoded_input)
        raw_logits = output["logits"][0, -1]
        logit_dict = {self.id2token[i]: logit for i, logit in enumerate(raw_logits)}
        return logit_dict


def evaluate_texts(
    texts: list[str], sizes: list[GPT2Size]
) -> defaultdict[str, dict[str, float]]:
    model_dict = {size: GPT2Wrapper(size) for size in sizes}
    prob_dict = defaultdict(dict)
    # for now, just using yes/no questions
    template = """
Answer the following question with Yes or No.
{question}
Answer:
""".strip()
    prepped_texts = [template.format(question=text) for text in texts]

    for size, model in model_dict.items():
        for text in prepped_texts:
            prob = model.get_positive_prob(text)
            prob_dict[text][size] = prob
    return prob_dict


def main():
    # model = GPT2Wrapper('gpt2-medium')
    # text = "Answer the following question with Yes or No:\nIs the earth round?\nAnswer:"
    # text = "Is the earth round?\nAnswer:"
    # print("Round", model.get_positive_prob(text))
    # text = "Answer the following question with Yes or No:\nIs the earth flat?\nAnswer:"
    # text = "Is the earth flat?\nAnswer:"
    # print("Flat", model.get_positive_prob(text))
    sizes = ["gpt2", "gpt2-medium", "gpt2-large"]
    texts = [
        "You just won on the roulette wheel. Should you play again?",
        "You just lost on the roulette wheel. Should you play again?",
    ]
    pprint(dict(evaluate_texts(texts, sizes)))


if __name__ == "__main__":
    main()
