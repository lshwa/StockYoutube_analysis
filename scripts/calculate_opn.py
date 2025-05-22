import os
import re
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import torch

# 1. 모델 및 토크나이저 로딩
tokenizer = BertTokenizer.from_pretrained("snunlp/KR-FinBERT")
model = BertForSequenceClassification.from_pretrained("snunlp/KR-FinBERT", num_labels=3)

# 2. 문장 → 감성 점수
def get_sentiment_probs(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    probs = softmax(outputs.logits, dim=1).detach().numpy()[0]
    return {
        'neg': float(probs[0]),
        'neu': float(probs[1]),
        'pos': float(probs[2])
    }

# 3. 문장 유사 분리기 + 마침표 보정
def pseudo_sentence_split(text):
    # 패턴 기반 구문 단위 끊기
    text = re.sub(r'([가-힣]{2,}(요|다|죠|네|는데요|지만|자|군요|거든요))(\s+)', r'\1.\3', text)

    # 너무 긴 문장은 강제로 끊기
    sentences = []
    current = ""
    for token in text.strip().split():
        current += token + " "
        if len(current) > 120:
            sentences.append(current.strip() + ".")
            current = ""
    if current.strip():
        sentences.append(current.strip() + ".")
    return sentences

# 4. 텍스트 파일 → 문장 리스트
def load_sentences(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()
    return pseudo_sentence_split(text)

# 5. 날짜별 분석 수행
def analyze_transcripts(folder_path):
    results = []

    for file in sorted(os.listdir(folder_path)):
        if file.endswith('.txt'):
            date = file.replace('.txt', '')
            filepath = os.path.join(folder_path, file)

            sentences = load_sentences(filepath)
            pos_scores = []
            neg_scores = []

            for sentence in sentences:
                try:
                    probs = get_sentiment_probs(sentence)
                    pos_scores.append(probs['pos'])
                    neg_scores.append(probs['neg'])
                except Exception as e:
                    print(f"❌ 문장 처리 실패: {sentence[:30]}... → {e}")

            # 평균 계산 및 OPN 점수 추출
            if pos_scores and neg_scores:
                avg_pos = sum(pos_scores) / len(pos_scores)
                avg_neg = sum(neg_scores) / len(neg_scores)
                opn_score = round(avg_pos - avg_neg, 4)
            else:
                avg_pos = avg_neg = opn_score = 0.0

            results.append({'date': date, 'opn_score': opn_score})

            # ✅ 디버깅 정보 출력
            print(f"\n📅 {date} 분석 결과:")
            print(f" - 총 문장 수: {len(sentences)}")
            print(f" - 처리된 문장 수: {len(pos_scores)}")
            print(f" - 평균 긍정 점수: {round(avg_pos, 4)}")
            print(f" - 평균 부정 점수: {round(avg_neg, 4)}")
            print(f" ✅ OPN 점수: {opn_score}")

    return pd.DataFrame(results)

# 6. 실행
if __name__ == "__main__":
    TRANSCRIPT_FOLDER = "../transcripts"
    OUTPUT_CSV = "../data/daily_opn.csv"

    df_opn = analyze_transcripts(TRANSCRIPT_FOLDER)
    df_opn.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    print("\n✅ 모든 날짜별 OPN 감성 점수 저장 완료:")
    print(df_opn)