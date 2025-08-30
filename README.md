# Deception Detection in Diplomacy

**Team:** PARADOX
**Challenge:** Esya '25 - IIIT Delhi
[cite_start]**Final Test Set Macro F1-Score:** 0.6407 [cite: 171]

---

## 1. Project Overview

This project presents our winning solution for the Deception Detection Challenge, hosted by IIIT Delhi as part of Esya '25. The goal was to create a **novel architecture** to identify deceptive messages in the strategic board game, Diplomacy.

[cite_start]Our final model, the **Context-Aware Multi-Vector Ensemble Framework (CMVEF)**, is a sophisticated machine learning pipeline that goes beyond simple text classification[cite: 108]. [cite_start]It operates on the principle that deception is revealed not just by a player's words, but by the context of the game, their strategic actions, their personal history, and their relationships with other players[cite: 109].

## 2. Our Approach: The CMVEF Pipeline

[cite_start]Instead of a single end-to-end model as initially proposed, our framework is a multi-stage process that systematically extracts and learns from diverse signals of deception[cite: 112].

### Key Innovations:

1.  [cite_start]**Data Augmentation via Strategic Commentary**: We created a `commentary.csv` file by translating raw, structured game moves into natural language summaries of each player's strategy for that turn[cite: 113, 114]. [cite_start]This provided a crucial textual counterpoint to the conversational messages, grounding the analysis in the game's reality[cite: 128, 129].

2.  [cite_start]**Rich, Multi-Faceted Feature Engineering**: We constructed a comprehensive feature set to give our models a 360-degree view of every message, including[cite: 116]:
    * [cite_start]**Semantic Vectors**: `Sentence-Transformer` embeddings for both messages and strategic commentary[cite: 136, 137].
    * [cite_start]**Lexical & Linguistic Cues**: TF-IDF vectors to capture keyword importance [cite: 142][cite_start], alongside rule-based features for promise-related words (e.g., "support", "I will") and linguistic hedges (e.g., "maybe")[cite: 144].
    * [cite_start]**Behavioral & Historical Analysis**: Features tracking a player's historical "lie rate" in previous seasons and their specific truthfulness history with the message's receiver[cite: 149].

3.  [cite_start]**Stacked Ensemble Modeling**: To tackle the severe class imbalance (~95% truthful messages)[cite: 153], we built a stacked ensemble:
    * [cite_start]**Base Models**: A **LightGBM** classifier (trained on SMOTEENN-resampled data) and a **PyTorch-based MLP** (using a Weighted Sampler and Focal Loss)[cite: 118].
    * [cite_start]**Meta-Model**: A **Logistic Regression** classifier trained on the predictions of the two base models, learning to weigh their outputs for the most accurate and robust final prediction[cite: 119, 166].

## 3. How to Run

The entire pipeline, from feature engineering to model training and evaluation, is contained within the provided Python notebook (`DeceptionDetection_PARADOX.pdf`).

To reproduce the results, run the cells in the notebook sequentially. [cite_start]Ensure that `train.csv`, `test.csv`, and the generated `commentary.csv` are in the same directory[cite: 208, 209, 210].
