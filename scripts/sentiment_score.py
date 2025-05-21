import pandas as pd
from collections import Counter

# 1. 감성 사전 로딩
def load_sentiment_words():
    pos_words = pd.read_csv('../data/KOSELF_positive.csv', header=None)[0].tolist()
    neg_words = pd.read_csv('../data/KOSELF_negative.csv', header=None)[0].tolist()
    return set(pos_words), set(neg_words)

# 2. 자막 텍스트 로딩
def load_text(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

# 3. 디버깅 감성 분석
def calculate_opn_verbose(text, pos_words, neg_words):
    words = text.strip().split()
    total = len(words)

    matched_pos = [word for word in words if word in pos_words]
    matched_neg = [word for word in words if word in neg_words]

    pos_count = len(matched_pos)
    neg_count = len(matched_neg)

    # 디버깅 출력
    print("✅ 감성 디버깅 결과")
    print(f"총 단어 수: {total}")
    print(f"POS 매칭 단어 수: {pos_count} | 단어들: {Counter(matched_pos)}")
    print(f"NEG 매칭 단어 수: {neg_count} | 단어들: {Counter(matched_neg)}")

    opn = round((pos_count - neg_count) / total if total > 0 else 0.0, 4)
    print(f"\n🎯 OPN 계산식: ({pos_count} - {neg_count}) / {total} = {opn}")
    return opn

# 4. 실행
if __name__ == "__main__":
    transcript_path = '../youtube_texts/transcript1.txt'
    pos_lexicon, neg_lexicon = load_sentiment_words()
    text = load_text(transcript_path)
    score = calculate_opn_verbose(text, pos_lexicon, neg_lexicon)
    print(f"\n[Transcript1] 최종 OPN 감성 점수: {score}")