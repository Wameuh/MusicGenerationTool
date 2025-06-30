"""
Video Generation Module

This module contains all functions related to video generation using the
Suno API, including video creation, status checking, downloading, and
video management.
"""

import json
import requests
import time
import os


def create_directories():
    """
    Create necessary directories for the application.
    """
    directories = ['data', 'music', 'video']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}/")
        else:
            print(f"📁 Directory already exists: {directory}/")


def generateVideo(taskId, audioId, api_key):
    """
    Generate video using the Suno API.

    Args:
        taskId (str): The task ID from music generation
        audioId (str): The audio ID from music generation
        api_key (str): The API key for authentication

    Returns:
        dict: Response from the API containing video task information
    """
    url = "https://apibox.erweima.ai/api/v1/mp4/generate"

    payload = json.dumps({
        "taskId": taskId,
        "audioId": audioId,
        "callBackUrl": "https://api.example.com/callback",
        "author": "Wameuh"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(json.dumps(response.json(), indent=2))
    return response.json()


def getVideoDetails(taskId, api_key):
    """
    Check the status and details of video generation.

    Args:
        taskId (str): The video task ID to check
        api_key (str): The API key for authentication

    Returns:
        dict: Current status and data of the video generation task
    """
    url = f"https://apibox.erweima.ai/api/v1/mp4/record-info?taskId={taskId}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(json.dumps(response.json(), indent=2))
    return response.json()


def waitUntilVideoGen(taskId, api_key):
    """
    Wait for video generation to complete.

    Args:
        taskId (str): The video task ID to monitor
        api_key (str): The API key for authentication

    Returns:
        dict: Completed video generation data
    """
    data = None
    while True:
        try:
            data = getVideoDetails(taskId, api_key)
            if data["data"]["successFlag"] == "SUCCESS":
                break
        except Exception:
            data = None
        time.sleep(5)
    return data


def downloadVideo(url, name):
    """
    Download video file from URL to video directory.
    Uses the same base name as the corresponding MP3 file.

    Args:
        url (str): The URL of the video to download
        name (str): The base name for the video file (same as MP3 filename)

    Returns:
        str: The actual path where the video was saved
    """
    # Ensure video directory exists
    create_directories()

    # Create video path with same name as MP3 file
    video_path = f"video/{name}.mp4"

    print(f"🎬 Downloading video from {url} to {video_path}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(video_path, "wb") as f:
            f.write(response.content)

        file_size = os.path.getsize(video_path)
        print(f"✅ Downloaded video to {video_path} ({file_size} bytes)")

        return video_path

    except Exception as e:
        print(f"❌ Error downloading video: {str(e)}")
        # Clean up partial file if it exists
        if os.path.exists(video_path):
            os.remove(video_path)
        raise


def generateVideoFromMusic(musicName, api_key):
    """
    Generate video from music using stored music data.

    Args:
        musicName (str): Name of the music to generate video for
        api_key (str): The API key for authentication

    Returns:
        dict or None: Video generation result or None if failed
    """
    try:
        # Ensure directories exist
        create_directories()

        # Read the JSON file from data directory
        json_path = "data/savedData.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            music_data = json.load(f)

        # Find the music entry by name
        music_entry = None
        for entry in music_data:
            if entry.get('name') == musicName:
                music_entry = entry
                break

        if not music_entry:
            print(f"Music '{musicName}' not found in {json_path}")
            return None

        # Extract the required data from the music entry
        taskId = music_entry.get('taskId', '')
        audioId = music_entry.get('audioId', '')

        if not taskId or not audioId:
            print(f"Missing taskId or audioId for music '{musicName}'")
            return None

        print(f"Generating video for music: {musicName}")
        print(f"TaskId: {taskId}, AudioId: {audioId}")

        # Generate the video
        video_response = generateVideo(taskId, audioId, api_key)

        if video_response and video_response.get('code') == 200:
            videoTaskId = video_response['data']['taskId']
            print(f"Video generation started with taskId: {videoTaskId}")

            # Update the JSON file with the taskId
            music_entry['videoTaskId'] = videoTaskId
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(music_data, f, indent=2, ensure_ascii=False)
            print(f"Updated {json_path} with taskId: {videoTaskId}")

            # Wait for video generation to complete
            print("Waiting for video generation to complete...")
            final_data = waitUntilVideoGen(videoTaskId, api_key)

            if final_data and final_data['data']['successFlag'] == 'SUCCESS':
                video_url = final_data['data']['response']['videoUrl']
                print("Video generation completed successfully!")
                print(f"Video URL: {video_url}")

                # Download the video and get the path
                video_path = downloadVideo(video_url, musicName)

                # Update the JSON file with the video info
                music_entry['videoUrl'] = video_url
                music_entry['videoStatus'] = 'completed'
                music_entry['video_path'] = video_path
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(music_data, f, indent=2, ensure_ascii=False)
                print(f"Updated {json_path} with video URL and status")

                print(f"Video generation and download completed for: "
                      f"{musicName}")
                return final_data
            else:
                print("Video generation failed or timed out")
                # Update status to failed
                music_entry['videoStatus'] = 'failed'
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(music_data, f, indent=2, ensure_ascii=False)
                return None
        else:
            print("Failed to start video generation")
            return None

    except FileNotFoundError:
        print(f"{json_path} file not found")
        return None
    except json.JSONDecodeError:
        print(f"Error reading {json_path} file")
        return None
    except Exception as e:
        print(f"Error during video generation: {str(e)}")
        return None
