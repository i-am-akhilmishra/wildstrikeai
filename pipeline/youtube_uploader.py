import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def get_credentials() -> Credentials:
    """Builds OAuth2 credentials from GitHub Secrets env vars."""
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())
    return creds


def upload_short(
    video_path: str,
    thumbnail_path: str = None,
    title: str = None,
    description: str = None,
    tags: list = None,
    mimetype: str = "video/quicktime",
) -> str:
    """
    Uploads video to YouTube and sets the custom thumbnail.
    Accepts trending tags list from trending_hashtags.py.
    Returns the YouTube video ID.
    """
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    if not title:
        title = "Wild Predator Strikes! \U0001f981 #Shorts #Wildlife #WildStrikeAI"

    if not description:
        description = (
            "Watch nature's most powerful predators in action!\n\n"
            "AI-generated wildlife narration by WildStrikeAI.\n\n"
            "#Shorts #Wildlife #Animals #Predator #NatureShorts "
            "#WildAnimals #Lion #Cheetah #Leopard #WildStrikeAI"
        )

    if not tags:
        tags = [
            "wildlife", "shorts", "animals", "predator",
            "nature", "WildStrikeAI", "lion", "cheetah",
            "leopard", "hunting", "wild",
        ]

    # YouTube allows max 30 tags
    tags = tags[:30]

    insert_request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "15",        # Pets & Animals
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        media_body=MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype=mimetype,
        ),
    )

    print("[YouTube] Starting upload...")
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"[YouTube] Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    if not video_id:
        raise RuntimeError(f"[YouTube] Upload failed — API response contained no video ID. Response: {response}")
    print(f"[YouTube] Upload complete! https://youtube.com/watch?v={video_id}")

    # Set custom thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg"),
            ).execute()
            print(f"[YouTube] Thumbnail set successfully.")
        except Exception as e:
            print(f"[YouTube] Thumbnail upload failed (may need verified channel): {e}")

    return video_id
