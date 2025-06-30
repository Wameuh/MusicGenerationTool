"""
Music Generation Module

This module contains all functions related to music generation using
the Suno API, including music creation, status checking, downloading,
and file management.
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


def genMusic(paroles, style, name, api_key):
    """
    Generate music using the Suno API.

    Args:
        paroles (str): The lyrics/prompt for music generation
        style (str): The style of music to generate
        name (str): The title/name of the music
        api_key (str): The API key for authentication

    Returns:
        dict: Response from the API containing task information
    """
    url = "https://apibox.erweima.ai/api/v1/generate"

    payload = json.dumps({
        "prompt": paroles,
        "style": style,
        "title": name,
        "customMode": True,
        "instrumental": False,
        "model": "V4_5",
        "negativeTags": "Pop, Electric, Piano",
        "callBackUrl": "https://api.example.com/callback"
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return response.json()


def getMusicGenStatus(id, api_key):
    """
    Check the status of music generation.

    Args:
        id (str): The task ID to check
        api_key (str): The API key for authentication

    Returns:
        dict: Current status and data of the music generation task
    """
    url = f"https://apibox.erweima.ai/api/v1/generate/record-info?taskId={id}"

    payload = ''
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(json.dumps(response.json(), indent=2))
    return response.json()


def getCredits(api_key):
    """
    Check the available credits for the API account.

    Args:
        api_key (str): The API key for authentication
    """
    url = "https://apibox.erweima.ai/api/v1/generate/credit"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def downloadingMusic(data, name):
    """
    Download music files from the generation response with proper indexing.

    Args:
        data (dict): The completed music generation response
        name (str): The base name for the files

    Returns:
        list: List of downloaded filenames with proper sequential indexing
    """
    # Ensure music directory exists
    create_directories()

    print(data["data"]["response"]["sunoData"][0]["sourceAudioUrl"])
    print(data["data"]["response"]["sunoData"][1]["sourceAudioUrl"])

    downloaded_files = []  # List to store downloaded filenames

    # Download first audio file
    url1 = data["data"]["response"]["sunoData"][0]["sourceAudioUrl"]
    response1 = requests.get(url1)

    # Check if file exists and find next available number for first file
    counter = 1
    filename1 = f"music/{name}_{counter}.mp3"
    while os.path.exists(filename1):
        counter += 1
        filename1 = f"music/{name}_{counter}.mp3"

    with open(filename1, "wb") as f:
        f.write(response1.content)
    print(f"Downloaded {filename1}")
    downloaded_files.append(filename1)

    # Check if file exists and find next available number for second file
    counter += 1
    filename2 = f"music/{name}_{counter}.mp3"
    while os.path.exists(filename2):
        counter += 1
        filename2 = f"music/{name}_{counter}.mp3"

    # Download second audio file
    url2 = data["data"]["response"]["sunoData"][1]["sourceAudioUrl"]
    response2 = requests.get(url2)
    with open(filename2, "wb") as f:
        f.write(response2.content)
    print(f"Downloaded {filename2}")
    downloaded_files.append(filename2)

    # Return the list of downloaded filenames
    return downloaded_files


def wait_until_completion(musicdata, api_key):
    """
    Wait for music generation to complete.

    Args:
        musicdata (dict): Initial response from music generation
        api_key (str): The API key for authentication

    Returns:
        dict: Completed music generation data
    """
    data = None
    while True:
        try:
            task_id = musicdata["data"]["taskId"]
            data = getMusicGenStatus(id=task_id, api_key=api_key)
            print(data["data"]["status"])
            if data["data"]["status"] == "SUCCESS":
                break
        except Exception:
            data = None
        time.sleep(5)
    return data


def generateAndDownloadMusic(paroles, style, api_key):
    """
    Complete workflow: generate music, wait for completion, and download files.

    Args:
        paroles (str): The lyrics/prompt for music generation
        style (str): The style of music to generate
        api_key (str): The API key for authentication

    Returns:
        dict: Dictionary containing file information and metadata
    """
    # Ensure directories exist
    create_directories()

    # Generate music using the existing function
    response = genMusic(paroles, style, style, api_key)

    # Wait for completion
    completed_data = wait_until_completion(response, api_key)

    # Download the music files and get the actual filenames
    downloaded_filenames = downloadingMusic(completed_data, style)

    # Create return dictionary with file information using actual filenames
    result = {}

    for i, filename_with_path in enumerate(downloaded_filenames):
        # Remove music/ prefix and .mp3 extension to get the key
        filename_without_ext = os.path.basename(filename_with_path)
        filename_without_ext = filename_without_ext.replace('.mp3', '')
        result[filename_without_ext] = {
            "paroles": paroles,
            "name": style,
            "taskId": completed_data["data"]["taskId"],
            "audioId": completed_data["data"]["response"]["sunoData"][i]["id"],
            "API_KEY": api_key,
            "file_path": filename_with_path  # Store full path
        }

    # Save result to JSON file in data directory
    try:
        json_path = "data/savedData.json"
        # Load existing data if file exists
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # Update with new data
        existing_data.update(result)

        # Save back to file
        with open(json_path, "w") as f:
            json.dump(existing_data, f, indent=2)

        print(f"Data saved to {json_path}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

    return result
