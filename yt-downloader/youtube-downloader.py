import yt_dlp
import sys

def download_video(url):
    """
    Downloads a YouTube video from the given URL in the highest quality using yt-dlp.
    """
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Fetching metadata for {url}")
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', None)
            print(f"Starting download: {video_title}")
            ydl.download([url])
            print(f"\nSuccessfully downloaded: {video_title}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        download_video(video_url)
    else:
        print("Please provide a YouTube URL as a command-line argument.")
        print("Example: python youtube-downloader.py <your-video-url>")