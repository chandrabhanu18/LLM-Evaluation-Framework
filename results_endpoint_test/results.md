# Evaluation Report

## Summary
- Examples: 25
- Models: model_a, model_b

## Aggregate Statistics
| Metric | Mean | Median | Std | Min | Max |
|---|---:|---:|---:|---:|---:|
| bleu | 0.1532 | 0.0000 | 0.2877 | 0.0000 | 1.0000 |
| rouge_l | 0.5568 | 0.6000 | 0.4152 | 0.0000 | 1.0000 |
| bertscore | 0.8964 | 0.9336 | 0.1129 | 0.6478 | 1.0000 |
| faithfulness | 0.4943 | 0.4643 | 0.4153 | 0.0000 | 1.0000 |
| context_relevancy | 0.8587 | 0.8739 | 0.0644 | 0.7079 | 0.9410 |
| answer_relevancy | 0.7127 | 0.7191 | 0.0784 | 0.5308 | 0.8767 |

## Insights
- Best average metric: **bertscore** (0.8964)
- Lowest average metric: **bleu** (0.1532)

## Per-example (first 10)
### Query: What is the capital of France?
- Model: model_a
  - Prediction: Paris.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 0.9999999701976776
  - faithfulness: 1.0
  - context_relevancy: 0.9383200407028198
  - answer_relevancy: 0.7986495196819305
- Model: model_b
  - Prediction: Lyon.
  - bleu: 0.0
  - rouge_l: 0.0
  - bertscore: 0.7462687790393829
  - faithfulness: 0.0
  - context_relevancy: 0.9383200407028198
  - answer_relevancy: 0.6777411997318268

### Query: Summarize the attached paragraph about photosynthesis.
- Model: model_a
  - Prediction: Photosynthesis lets plants convert sunlight into energy.
  - bleu: 0.0728758069843786
  - rouge_l: 0.5333333333333333
  - bertscore: 0.9535990953445435
  - faithfulness: 0.14285714285714285
  - context_relevancy: 0.8251261115074158
  - answer_relevancy: 0.8307689428329468
- Model: model_b
  - Prediction: Plants use chlorophyll to make food from sunlight.
  - bleu: 0.04767707020457095
  - rouge_l: 0.125
  - bertscore: 0.8279350697994232
  - faithfulness: 0.0
  - context_relevancy: 0.8251261115074158
  - answer_relevancy: 0.775850772857666

### Query: Who wrote 'Pride and Prejudice'?
- Model: model_a
  - Prediction: Jane Austen.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 1.0000000596046448
  - faithfulness: 1.0
  - context_relevancy: 0.8739376068115234
  - answer_relevancy: 0.7228543162345886
- Model: model_b
  - Prediction: Charlotte Bronte.
  - bleu: 0.0
  - rouge_l: 0.0
  - bertscore: 0.7258471995592117
  - faithfulness: 0.0
  - context_relevancy: 0.8739376068115234
  - answer_relevancy: 0.5837693512439728

### Query: Solve: What is 12 multiplied by 8?
- Model: model_a
  - Prediction: 96.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 1.0000000596046448
  - faithfulness: 1.0
  - context_relevancy: 0.8164746165275574
  - answer_relevancy: 0.5974072590470314
- Model: model_b
  - Prediction: 100.
  - bleu: 0.0
  - rouge_l: 0.0
  - bertscore: 0.8263473212718964
  - faithfulness: 0.0
  - context_relevancy: 0.8164746165275574
  - answer_relevancy: 0.5722689628601074

### Query: Explain the difference between TCP and UDP.
- Model: model_a
  - Prediction: TCP is reliable and connection-oriented; UDP is connectionless and faster.
  - bleu: 0.6132297420585353
  - rouge_l: 0.8181818181818182
  - bertscore: 0.9968928098678589
  - faithfulness: 0.3333333333333333
  - context_relevancy: 0.8056675493717194
  - answer_relevancy: 0.8766981959342957
- Model: model_b
  - Prediction: TCP is faster; UDP is reliable.
  - bleu: 0.17632778423526838
  - rouge_l: 0.4705882352941177
  - bertscore: 0.9436421394348145
  - faithfulness: 0.6
  - context_relevancy: 0.8056675493717194
  - answer_relevancy: 0.8459572196006775

### Query: List three symptoms of diabetes.
- Model: model_a
  - Prediction: Increased thirst, frequent urination, fatigue.
  - bleu: 1.0000000000000004
  - rouge_l: 1.0
  - bertscore: 1.0
  - faithfulness: 0.8
  - context_relevancy: 0.8164111077785492
  - answer_relevancy: 0.8225733041763306
- Model: model_b
  - Prediction: Thirst, blurred vision, hair loss.
  - bleu: 0.07267884212102742
  - rouge_l: 0.20000000000000004
  - bertscore: 0.8856452405452728
  - faithfulness: 0.2
  - context_relevancy: 0.8164111077785492
  - answer_relevancy: 0.7975944876670837

### Query: Translate 'hello' to Spanish.
- Model: model_a
  - Prediction: Hola.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 1.0000000596046448
  - faithfulness: 1.0
  - context_relevancy: 0.9046818614006042
  - answer_relevancy: 0.6507211923599243
- Model: model_b
  - Prediction: Hola.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 1.0000000596046448
  - faithfulness: 1.0
  - context_relevancy: 0.9046818614006042
  - answer_relevancy: 0.6507211923599243

### Query: What year did the Berlin Wall fall?
- Model: model_a
  - Prediction: 1989.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 0.9999999701976776
  - faithfulness: 1.0
  - context_relevancy: 0.9118149280548096
  - answer_relevancy: 0.6646763682365417
- Model: model_b
  - Prediction: 1990.
  - bleu: 0.0
  - rouge_l: 0.0
  - bertscore: 0.9296927154064178
  - faithfulness: 0.0
  - context_relevancy: 0.9118149280548096
  - answer_relevancy: 0.6577059775590897

### Query: Give a brief recipe for scrambled eggs.
- Model: model_a
  - Prediction: Beat eggs and cook in butter until set.
  - bleu: 0.6606328636027612
  - rouge_l: 0.9333333333333333
  - bertscore: 0.9970886707305908
  - faithfulness: 0.375
  - context_relevancy: 0.7672450542449951
  - answer_relevancy: 0.7789331376552582
- Model: model_b
  - Prediction: Crack eggs and stir.
  - bleu: 0.057079690340587526
  - rouge_l: 0.18181818181818182
  - bertscore: 0.8506244719028473
  - faithfulness: 0.5
  - context_relevancy: 0.7672450542449951
  - answer_relevancy: 0.7988387942314148

### Query: What is the chemical symbol for Gold?
- Model: model_a
  - Prediction: Au.
  - bleu: 0.0
  - rouge_l: 1.0
  - bertscore: 1.0000001192092896
  - faithfulness: 1.0
  - context_relevancy: 0.9202361702919006
  - answer_relevancy: 0.5846036896109581
- Model: model_b
  - Prediction: Gd.
  - bleu: 0.0
  - rouge_l: 0.0
  - bertscore: 0.6477771997451782
  - faithfulness: 0.0
  - context_relevancy: 0.9202361702919006
  - answer_relevancy: 0.5596156604588032
