# Evaluation Report

## Summary
- Examples: 25
- Models: model_a, model_b

## Aggregate Statistics
| Metric | Mean | Median | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| bleu | 0.1532 | 0.0000 | 0.2877 | 0.0000 | 1.0000 |
| rouge_l | 0.5568 | 0.6000 | 0.4152 | 0.0000 | 1.0000 |
| faithfulness | 0.4943 | 0.4643 | 0.4153 | 0.0000 | 1.0000 |

## Insights
- Best average metric: **rouge_l** (0.5568)
- Lowest average metric: **bleu** (0.1532)

## Per-example (first 10)
### Query: What is the capital of France?
- Model: model_a
  - Prediction: Paris.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: Lyon.
  - bleu: 0.0
  - rouge_l: 0.0
  - faithfulness: 0.0

### Query: Summarize the attached paragraph about photosynthesis.
- Model: model_a
  - Prediction: Photosynthesis lets plants convert sunlight into energy.
  - bleu: 0.0728758069843786
  - rouge_l: 0.5333333333333333
  - faithfulness: 0.14285714285714285
- Model: model_b
  - Prediction: Plants use chlorophyll to make food from sunlight.
  - bleu: 0.04767707020457095
  - rouge_l: 0.125
  - faithfulness: 0.0

### Query: Who wrote 'Pride and Prejudice'?
- Model: model_a
  - Prediction: Jane Austen.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: Charlotte Bronte.
  - bleu: 0.0
  - rouge_l: 0.0
  - faithfulness: 0.0

### Query: Solve: What is 12 multiplied by 8?
- Model: model_a
  - Prediction: 96.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: 100.
  - bleu: 0.0
  - rouge_l: 0.0
  - faithfulness: 0.0

### Query: Explain the difference between TCP and UDP.
- Model: model_a
  - Prediction: TCP is reliable and connection-oriented; UDP is connectionless and faster.
  - bleu: 0.6132297420585353
  - rouge_l: 0.8181818181818182
  - faithfulness: 0.3333333333333333
- Model: model_b
  - Prediction: TCP is faster; UDP is reliable.
  - bleu: 0.17632778423526838
  - rouge_l: 0.4705882352941177
  - faithfulness: 0.6

### Query: List three symptoms of diabetes.
- Model: model_a
  - Prediction: Increased thirst, frequent urination, fatigue.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - faithfulness: 0.8
- Model: model_b
  - Prediction: Thirst, blurred vision, hair loss.
  - bleu: 0.07267884212102742
  - rouge_l: 0.20000000000000004
  - faithfulness: 0.2

### Query: Translate 'hello' to Spanish.
- Model: model_a
  - Prediction: Hola.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: Hola.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0

### Query: What year did the Berlin Wall fall?
- Model: model_a
  - Prediction: 1989.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: 1990.
  - bleu: 0.0
  - rouge_l: 0.0
  - faithfulness: 0.0

### Query: Give a brief recipe for scrambled eggs.
- Model: model_a
  - Prediction: Beat eggs and cook in butter until set.
  - bleu: 0.6606328636027612
  - rouge_l: 0.9333333333333333
  - faithfulness: 0.375
- Model: model_b
  - Prediction: Crack eggs and stir.
  - bleu: 0.057079690340587526
  - rouge_l: 0.18181818181818182
  - faithfulness: 0.5

### Query: What is the chemical symbol for Gold?
- Model: model_a
  - Prediction: Au.
  - bleu: 0.0
  - rouge_l: 1.0
  - faithfulness: 1.0
- Model: model_b
  - Prediction: Gd.
  - bleu: 0.0
  - rouge_l: 0.0
  - faithfulness: 0.0
