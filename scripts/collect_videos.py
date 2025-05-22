import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# 사용자 설정
API_KEY = "Your_API_KEY"
USERNAME = "hkwowtv"
MAX_RESULTS = 50

# 최근 7일 기준 날짜 계산
CUTOFF_DATE = datetime.today() - timedelta(days=7)

# 사용자명 → channelId 조회
def get_channel_id_from_username(username):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={username}&key={API_KEY}"
    response = requests.get(url).json()
    print("채널 검색 응답 확인 완료")
    return response['items'][0]['snippet']['channelId']

# channelId → 업로드 playlistId 조회
def get_uploads_playlist_id(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={API_KEY}"
    response = requests.get(url).json()
    print("채널 상세 정보 조회 완료")
    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# playlistId → 영상 목록 수집
def get_video_list(playlist_id):
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

        # 예외적으로 quota 오류가 있으면 빠르게 종료
        if "error" in response:
            print("API 오류 발생:", response["error"])
            break

        items = response.get('items', [])
        if not items:
            print("더 이상 영상이 없습니다.")
            break

        for item in items:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']
            title = snippet['title']
            published_at = snippet['publishedAt'][:10]  # YYYY-MM-DD
            pub_date = datetime.strptime(published_at, "%Y-%m-%d")

            if pub_date < CUTOFF_DATE:
                print(f"{published_at} 영상은 일주일 이전이라 수집 중단")
                return videos  

            print(f"수집됨: {published_at} - {title}")
            videos.append({
                "video_id": video_id,
                "title": title,
                "published_at": published_at
            })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

# 실행
if __name__ == "__main__":
    try:
        channel_id = get_channel_id_from_username(USERNAME)
        playlist_id = get_uploads_playlist_id(channel_id)
        video_data = get_video_list(playlist_id)

        if video_data:
            os.makedirs("../data", exist_ok=True)  # ← 추가
            df = pd.DataFrame(video_data)
            df.to_csv("../data/hkwowtv_videos.csv", index=False, encoding='utf-8-sig')
            print(f"총 {len(df)}개의 영상을 수집하고 저장했습니다.")
        else:
            print("최근 7일 내 영상이 없습니다.")

    except Exception as e:
        print("오류 발생:", e)
