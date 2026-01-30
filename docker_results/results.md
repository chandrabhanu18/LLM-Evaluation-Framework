# Evaluation Report

## Aggregate Statistics
### bleu
- mean: 0.5397
- median: 0.5000
- std: 0.3801
- min: 0.0257
- max: 1.0000

### rouge_l
- mean: 0.5568
- median: 0.6000
- std: 0.4152
- min: 0.0000
- max: 1.0000

### bertscore
- mean: 0.5000
- median: 0.5000
- std: 0.0000
- min: 0.5000
- max: 0.5000

### faithfulness
- mean: 0.4943
- median: 0.4643
- std: 0.4153
- min: 0.0000
- max: 1.0000

### context_relevancy
- mean: 0.8000
- median: 1.0000
- std: 0.4000
- min: 0.0000
- max: 1.0000

### answer_relevancy
- mean: 0.0086
- median: 0.0000
- std: 0.0444
- min: 0.0000
- max: 0.2857

## Per-example (first 10)
### Query: What is the capital of France?
- Model: model_a
  - Prediction: Paris.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Lyon.
  - bleu: 0.49999999999999994
  - rouge_l: 0.0
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Summarize the attached paragraph about photosynthesis.
- Model: model_a
  - Prediction: Photosynthesis lets plants convert sunlight into energy.
  - bleu: 0.0728758069843786
  - rouge_l: 0.5333333333333333
  - bertscore: 0.5
  - faithfulness: 0.14285714285714285
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Plants use chlorophyll to make food from sunlight.
  - bleu: 0.04767707020457095
  - rouge_l: 0.125
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Who wrote 'Pride and Prejudice'?
- Model: model_a
  - Prediction: Jane Austen.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Charlotte Bronte.
  - bleu: 0.27516060407455223
  - rouge_l: 0.0
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Solve: What is 12 multiplied by 8?
- Model: model_a
  - Prediction: 96.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: 100.
  - bleu: 0.49999999999999994
  - rouge_l: 0.0
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Explain the difference between TCP and UDP.
- Model: model_a
  - Prediction: TCP is reliable and connection-oriented; UDP is connectionless and faster.
  - bleu: 0.6132297420585353
  - rouge_l: 0.8181818181818182
  - bertscore: 0.5
  - faithfulness: 0.3333333333333333
  - context_relevancy: 1.0
  - answer_relevancy: 0.2857142857142857
- Model: model_b
  - Prediction: TCP is faster; UDP is reliable.
  - bleu: 0.17632778423526838
  - rouge_l: 0.4705882352941177
  - bertscore: 0.5
  - faithfulness: 0.6
  - context_relevancy: 1.0
  - answer_relevancy: 0.14285714285714285

### Query: List three symptoms of diabetes.
- Model: model_a
  - Prediction: Increased thirst, frequent urination, fatigue.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 0.8
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Thirst, blurred vision, hair loss.
  - bleu: 0.07267884212102742
  - rouge_l: 0.20000000000000004
  - bertscore: 0.5
  - faithfulness: 0.2
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Translate 'hello' to Spanish.
- Model: model_a
  - Prediction: Hola.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 0.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Hola.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 0.0
  - answer_relevancy: 0.0

### Query: What year did the Berlin Wall fall?
- Model: model_a
  - Prediction: 1989.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: 1990.
  - bleu: 0.49999999999999994
  - rouge_l: 0.0
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: Give a brief recipe for scrambled eggs.
- Model: model_a
  - Prediction: Beat eggs and cook in butter until set.
  - bleu: 0.6606328636027612
  - rouge_l: 0.9333333333333333
  - bertscore: 0.5
  - faithfulness: 0.375
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Crack eggs and stir.
  - bleu: 0.0570796903405875
  - rouge_l: 0.18181818181818182
  - bertscore: 0.5
  - faithfulness: 0.5
  - context_relevancy: 1.0
  - answer_relevancy: 0.0

### Query: What is the chemical symbol for Gold?
- Model: model_a
  - Prediction: Au.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 0.5
  - faithfulness: 1.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
- Model: model_b
  - Prediction: Gd.
  - bleu: 0.49999999999999994
  - rouge_l: 0.0
  - bertscore: 0.5
  - faithfulness: 0.0
  - context_relevancy: 1.0
  - answer_relevancy: 0.0
