import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
import os
from collections import defaultdict

# 1. CSV 파일에서 영상 ID와 날짜 불러오기
df = pd.read_csv("../data/hkwowtv_videos.csv")

# 2. 날짜별로 자막 저장할 딕셔너리
date_to_transcript = defaultdict(list)

# 3. 각 영상에 대해 transcript 가져오기
for idx, row in df.iterrows():
    video_id = row['video_id']
    date = row['published_at']
    try:
        # 한국어 자동 자막 또는 영어 자막 요청
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        text = " ".join([entry['text'] for entry in transcript])
        date_to_transcript[date].append(f"[{video_id}] {text}")
        print(f"✅ {date} - {video_id} 수집 성공")
    except Exception as e:
        print(f"❌ {video_id} 실패: {e}")

# 4. transcripts 폴더 없으면 생성
os.makedirs("../transcripts", exist_ok=True)

# 5. 날짜별로 txt 파일 저장
for date, texts in date_to_transcript.items():
    with open(f"../transcripts/{date}.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(texts))

print("✅ 모든 날짜별 스크립트 저장 완료")