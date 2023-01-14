import collections
from googleapiclient.discovery import build
collections.Callable = collections.abc.Callable
from bs4 import BeautifulSoup as bs
import requests
import re
import json
from urllib.request import urlopen as urReq
from flask import Flask, render_template, request  #obtains data from html form
import os
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("api")
youtube=build('youtube','v3',developerKey=api_key)
from functions import get_comments,download_video

app=Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("index1.html")

@app.route("/result2",methods=["POST","GET"])
def result2():
    try:
        output=request.form.to_dict()
        print(output)
        youtube_url= output["username"]
        print(youtube_url)
        videoCount=output["videoCountRequest"]
        response_website = urReq(youtube_url)
        data_yt = response_website.read().decode('utf-8')
        # getting youtube channel id
        soup = bs(requests.get(youtube_url, cookies={'CONSENT': 'YES+1'}).text, "html.parser")
        data = re.search(r"var ytInitialData = ({.*});", str(soup.prettify())).group(1)
        json_data = json.loads(data)
        channel_id = json_data['header']['c4TabbedHeaderRenderer']['channelId']

        def yt2_channel_stats(youtube, channel_id):  #channel stats using channel Id
            request = youtube.channels().list(
                part="snippet,contentDetails,statistics",
                id=channel_id)
            response = request.execute()  # this will save  in the form of dictionary
            data =      (response['items'][0]['snippet']['title'],
                        response['items'][0]['statistics']['subscriberCount'],
                        response['items'][0]['statistics']['viewCount'],
                        response['items'][0]['statistics']['videoCount'],
                        response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
            return data
        channel_stat = yt2_channel_stats(youtube, channel_id)
        #print(channel_stat)
        headings = ("channel name", "subscribers", "views", "videos", "playlist id")

        playlist_id=(channel_stat[4])
        #print(playlist_id)
        def get_vedio_id(youtube, playlist_id):
            request = youtube.playlistItems().list(  # playlistItems  s is there
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=videoCount)
            response = request.execute()
            items = []
            for i in range(len(response['items'])):
                items.append(response['items'][i]['contentDetails']['videoId'])

            return (items)
        video_ids = get_vedio_id(youtube, playlist_id)

        def title_wd_link(Title, video_Id):
            x =  f'''<a target=_blank   href=https://www.youtube.com/watch?v={video_Id}  >  {Title}  </a> '''

            return x

        def thumbnail_wd_link(Thumbnail):
            x = f'''<a> <img src = {Thumbnail} alt =thumbnail width=100% height=150 align =left/></a>'''
            return x

        def comments_link(video_Id,comment_count):
            x = f'''<a target=_blank   href=/comments?video_id={video_Id} > {comment_count} </a>'''
            return x

        def download_link(video_Id,download_text):
            y = f'''<a target=_blank   href=/download?video_id={video_Id}> {download_text} </a>'''
            return y

        def video_details(youtube, video_ids):
            all_video_stats = []
            j=0
            for i in range(0, 1):
                request = youtube.videos().list(  # playlistItems  s is there
                    part='snippet, statistics',
                    id=','.join(video_ids))
                response = request.execute()
                for video in response['items']:
                    j=j+1
                    sl_no=j
                    Title = video['snippet']['title']
                    video_Id = video['id']
                    Title = title_wd_link(Title, video_Id)
                    Thumbnail = video['snippet']['thumbnails']['default']['url']
                    snips = thumbnail_wd_link(Thumbnail)
                    comment_count=video['statistics']['commentCount']
                    comment_link=comments_link(video_Id,comment_count)
                    download_text="click here to download"
                    download=download_link(video_Id,download_text)
                    video_stats = (sl_no,Title, video['snippet']['publishedAt'], video['statistics']['viewCount'],video['statistics']['likeCount']
                                   ,comment_link,download, snips)
                    all_video_stats.append(video_stats)

            return all_video_stats

        vheading = ("Sl no","Title", "published_date", "views", "likes", "comment_number","download", "Thumbnails")
        vdata = video_details(youtube, video_ids)
        # print(vdata)
        vdata = tuple(vdata)
        # print(vdata)

    #print(links[1][1])
        return render_template("result.html",channel_stat=channel_stat,headings=headings,
                               vdata=vdata,vheading=vheading,render_links=True,bold_rows=True,justify='center',index_names=False)

    except Exception as e:
        print("please paste the proper URL")
        return render_template("error.html")



@app.route("/comments",methods=["POST","GET"])
def comments():
        comment_num=request.form.to_dict()
        print(comment_num)
        video_Id = request.args.get('video_id')
        commentCountRequest="10"
        cdata =get_comments.comments(youtube ,video_Id, commentCountRequest)
        cheading = ("comments","commenter")
        return render_template("cmtresult.html",vdata=cdata, vheading=cheading,video_Id=video_Id)

@app.route("/comments_count",methods=["POST","GET"])
def comments_count():
        comment_=request.form.to_dict()
        video_Id = comment_["video_id"]
        commentCountRequest=comment_["commentCountRequest"]
        cdata =get_comments.comments(youtube ,video_Id, commentCountRequest)
        cheading = ("Sl no","comments","commenter")
        return render_template("cmtresult.html",vdata=cdata, vheading=cheading,video_Id=video_Id)

@app.route("/download", methods = ["POST", "GET"])
def download():

    videoId = request.args.get('video_id')

    file = download_video.download(videoId)
    return file


if __name__=="__main__":
    app.run(debug=True,port=5002)

