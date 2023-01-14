from googleapiclient.discovery import build


youtube = build('youtube', 'v3', developerKey=api_key)


def comments(youtube, video_Id, commentCountRequest):
    all_comment_stats = []
    i=0
    request = youtube.commentThreads().list(part="snippet", videoId=video_Id, maxResults= commentCountRequest)
    response = request.execute()
    for video in response['items']:
        i=i+1
        sl_no=i
        comment_stats = (i,video['snippet']['topLevelComment']['snippet']['textDisplay'],
                         video['snippet']['topLevelComment']['snippet']['authorDisplayName'])
        all_comment_stats.append(comment_stats)
    return all_comment_stats


