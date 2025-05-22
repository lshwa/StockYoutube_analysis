import pandas as pd
from collections import Counter
import os

# 1. 감성 사전 로딩
def load_sentiment_words():
    pos_words = pd.read_csv('../data/KOSELF2_positive.csv', header=None)[0].tolist()
    neg_words = pd.read_csv('../data/KOSELF1_negative.csv', header=None)[0].tolist()
    return set(pos_words), set(neg_words)

# 2. 자막 텍스트 로딩
def load_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

# 3. OPN 계산 (디버깅 없음, 실 운영용)
def calculate_opn_score(text, pos_words, neg_words):
    words = text.strip().split()
    total = len(words)
    pos_count = sum(1 for word in words if word in pos_words)
    neg_count = sum(1 for word in words if word in neg_words)
    return round((pos_count - neg_count) / total if total > 0 else 0.0, 4)

# 4. 날짜별 텍스트 분석
def analyze_daily_transcripts(folder_path, pos_words, neg_words):
    results = []

    for file in sorted(os.listdir(folder_path)):
        if file.endswith('.txt'):
            date = file.replace('.txt', '')
            filepath = os.path.join(folder_path, file)
            text = load_text(filepath)
            opn_score = calculate_opn_score(text, pos_words, neg_words)
            results.append({'date': date, 'opn_score': opn_score})

    return pd.DataFrame(results)

# 5. 실행
if __name__ == "__main__":
    TRANSCRIPT_FOLDER = "../transcripts"
    OUTPUT_CSV = "../data/daily_opn.csv"

    pos_lexicon, neg_lexicon = load_sentiment_words()
    df_opn = analyze_daily_transcripts(TRANSCRIPT_FOLDER, pos_lexicon, neg_lexicon)
    df_opn.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    print("✅ 일별 OPN 감성 점수 저장 완료:")
    print(df_opn)