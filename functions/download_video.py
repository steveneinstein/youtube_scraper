from pytube import YouTube
from pytube import YouTube, exceptions
from io import BytesIO
from flask import send_file



def download(videoId):

    link = f"https://www.youtube.com/watch?v={videoId}"
    filename = f"file_Id= {videoId}.mp4"
    buffer = BytesIO()
    youtubeObject = YouTube(link)

    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")

    youtubeObject.stream_to_buffer(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True,attachment_filename=filename)

