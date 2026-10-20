"""
youtube_uploader.py - Resumable YouTube Data API v3 Video & Shorts Publisher
Automates:
- Resumable chunked upload of 1080p long-form video essays (100MB - 2GB+)
- Setting titles, rich descriptions, tags, category, and privacy status
- Custom 1997 found footage thumbnail setting
- Uploading chapter cuts with #Shorts metadata
- Persistent OAuth2 token storage in token.json (login once, perpetual refresh)
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

PUBLISHERS_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(PUBLISHERS_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(PUBLISHERS_DIR, "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def is_youtube_configured() -> bool:
    """Checks if credentials or client_secret exists."""
    return os.path.exists(TOKEN_FILE) or os.path.exists(CLIENT_SECRETS_FILE)

def get_authenticated_service():
    """Authenticates via OAuth2 and returns the YouTube API service object."""
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Could not load token.json: {e}")
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Token refresh failed ({e}), initiating fresh auth flow...")
                creds = None
                
        if not creds:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                raise FileNotFoundError(
                    f"Missing '{CLIENT_SECRETS_FILE}'.\n"
                    f"Please download your OAuth 2.0 client_secret.json from Google Cloud Console "
                    f"and place it into: {PUBLISHERS_DIR}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds)

def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: List[str] = None,
    category_id: str = "24",  # 24 = Entertainment, 27 = Education, 1 = Film & Animation
    privacy_status: str = "unlisted",  # 'public', 'unlisted', 'private'
    thumbnail_path: str = None,
    progress_callback = None
) -> Dict[str, Any]:
    """
    Executes a robust resumable video upload to YouTube.
    Returns: {"video_id": str, "url": str, "title": str}
    """
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
        
    youtube = get_authenticated_service()
    
    body = {
        "snippet": {
            "title": title[:100],  # YouTube title max 100 chars
            "description": description[:5000],
            "tags": tags or ["horror", "urban legends", "documentary", "dark science"],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }
    
    # 8MB chunk size for resilient uploads
    chunk_size = 1024 * 1024 * 8
    media = MediaFileUpload(video_path, chunksize=chunk_size, resumable=True, mimetype="video/mp4")
    
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    print(f"\n[YOUTUBE UPLOADER] Starting Resumable Upload:")
    print(f" File: {os.path.basename(video_path)} ({os.path.getsize(video_path)/1024/1024:.1f} MB)")
    print(f" Title: '{title}' | Privacy: {privacy_status.upper()}")
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  [UPLOAD PROGRESS] {pct}% uploaded...", flush=True)
            if progress_callback:
                progress_callback(pct)
                
    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"\n✅ [YOUTUBE UPLOAD COMPLETE] Video Live: {video_url}")
    
    # Upload custom thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            print(f"[YOUTUBE UPLOADER] Setting custom thumbnail from {os.path.basename(thumbnail_path)}...")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            ).execute()
            print(f"✅ Thumbnail updated successfully!")
        except Exception as te:
            print(f"⚠️ Warning: Could not set thumbnail: {te}")
            
    return {
        "video_id": video_id,
        "url": video_url,
        "title": title,
        "privacy": privacy_status
    }

def upload_chapter_as_short(
    chapter_path: str,
    chapter_title: str,
    parent_topic: str,
    thumbnail_path: str = None,
    privacy_status: str = "unlisted"
) -> Dict[str, Any]:
    """Uploads an individual chapter cut as a YouTube Short."""
    short_title = f"{chapter_title} #Shorts"[:100]
    description = (
        f"From the full documentary: '{parent_topic}'.\n\n"
        f"Watch the full 11-minute deep-dive on our channel.\n\n"
        f"#Shorts #Horror #UrbanLegends #AnalogHorror #ScaryStories"
    )
    tags = ["Shorts", "horror", "urban legends", "creepy", "dark folklore"]
    return upload_video(
        video_path=chapter_path,
        title=short_title,
        description=description,
        tags=tags,
        category_id="24",
        privacy_status=privacy_status,
        thumbnail_path=thumbnail_path
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="YouTube Studio Auto-Publisher")
    parser.add_argument("--auth", action="store_true", help="Initiate OAuth2 login flow")
    parser.add_argument("--upload", type=str, help="Path to video file to upload")
    parser.add_argument("--title", type=str, default="Top 5 Scariest Japanese Urban Legends Explained", help="Video title")
    parser.add_argument("--privacy", type=str, default="unlisted", help="Video privacy (public, unlisted, private)")
    args = parser.parse_args()

    if args.auth or not os.path.exists(TOKEN_FILE):
        try:
            print("🔑 Connecting to YouTube Data API v3...")
            svc = get_authenticated_service()
            print("✅ YouTube Account Connected Successfully!")
        except Exception as e:
            print(f"❌ YouTube Auth Notice: {e}")
            
    if args.upload:
        upload_video(args.upload, args.title, "Uploaded via Autonomous Studio Pipeline", privacy_status=args.privacy)
