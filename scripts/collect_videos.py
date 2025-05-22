import requests
import pandas as pd
import os
from datetime import datetime

# 발급받은 유효한 API 키
API_KEY = "AIzaSyCWM4vVPVWoWcbiqk_qU9JLdkAI8NAkqfg"

# 분석 대상 재생목록 ID
PLAYLIST_IDS = [
    "PLFJr7n9VNSFhJbk-vsVOBspiW2XNg3dNc",
    "PLFJr7n9VNSFjCCdlR5-Gq-yJmATQ_0NeG",
    "PLFJr7n9VNSFhYGhedWE9wGPq1AUUuwuYD"
]

# 설정
MAX_RESULTS = 50
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 5, 31)

def get_video_list_in_range(playlist_id):
    videos = []
    next_page_token = None
    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems?"
            f"part=snippet&playlistId={playlist_id}&maxResults={MAX_RESULTS}&key={API_KEY}"
        )
        if next_page_token:
            url += f"&pageToken={next_page_token}"
        response = requests.get(url).json()

        # API 오류 처리
        if "error" in response:
            print("API 오류:", response["error"])
            break

        items = response.get('items', [])
        if not items:
            break

        for item in items:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']
            title = snippet['title']
            published_at = snippet['publishedAt'][:10]  # YYYY-MM-DD
            pub_date = datetime.strptime(published_at, "%Y-%m-%d")

            # 날짜 필터
            if START_DATE <= pub_date <= END_DATE:
                print(f"✅ 수집됨: {published_at} - {title}")
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "published_at": published_at,
                    "playlist_id": playlist_id
                })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

# 실행
if __name__ == "__main__":
    all_videos = []
    for pid in PLAYLIST_IDS:
        all_videos.extend(get_video_list_in_range(pid))

    df = pd.DataFrame(all_videos)

    #  결과 폴더 생성
    os.makedirs("results", exist_ok=True)

    #  CSV 저장
    df.to_csv("results/lucky_tv_videos_2025.csv", index=False, encoding='utf-8-sig')
    print(f"\n🎉 총 {len(df)}개 영상 수집 완료! → results/lucky_tv_videos_2025.csv")