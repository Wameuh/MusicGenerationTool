"""
Gradio Interface Module

This module contains all functions related to the Gradio web interface,
including UI components, data management, and user interaction handlers.
"""

import json
import os
import gradio as gr
from music_generation import (
    genMusic, wait_until_completion, downloadingMusic, create_directories
)
from video_generation import (
    generateVideo, waitUntilVideoGen, downloadVideo, getVideoDetails
)


def create_music_with_gradio(token, name, paroles, style):
    """
    Create music using the Gradio interface parameters.

    Args:
        token (str): API token for authentication
        name (str): Name/title of the music
        paroles (str): Lyrics/prompt for music generation
        style (str): Style of music to generate

    Returns:
        str: Status message with generation results
    """
    try:
        # Ensure directories exist
        create_directories()

        print("🔧 DEBUG: Starting music generation process")
        print(f"🔧 DEBUG: Name='{name}', Style='{style}'")

        if not token:
            return "Please provide an API token"
        if not name:
            return "Please provide a music name"
        if not paroles:
            return "Please provide lyrics (paroles)"
        if not style:
            return "Please provide a music style"

        print("🔧 DEBUG: All inputs validated, calling genMusic...")

        # Start the music generation process
        result = genMusic(paroles, style, name, token)
        print(f"🔧 DEBUG: genMusic result: {result}")

        if not result or result.get('code') != 200:
            error_msg = result.get('msg', 'Unknown error')
            return f"Failed to start music generation: {error_msg}"

        task_id = result['data']['taskId']
        print(f"🔧 DEBUG: Task ID: {task_id}")

        # Wait for completion
        print("🔧 DEBUG: Waiting for completion...")
        completed_data = wait_until_completion(result, token)
        data_keys = list(completed_data.keys()) if completed_data else 'None'
        print(f"🔧 DEBUG: Completed data keys: {data_keys}")

        status_check = completed_data.get('data', {}).get('status')
        status_check = status_check != 'SUCCESS'
        if not completed_data or status_check:
            status = completed_data.get('data', {}).get('status')
            status = status if completed_data else 'No data'
            print(f"🔧 DEBUG: Generation failed. Status: {status}")
            return f"Music generation failed or timed out for '{name}'"

        print("🔧 DEBUG: Generation successful, checking response structure...")

        response_data = completed_data.get('data', {}).get('response', {})
        suno_data = response_data.get('sunoData', [])
        print(f"🔧 DEBUG: sunoData length: {len(suno_data)}")

        if len(suno_data) == 0:
            return f"No audio data received for '{name}'"

        for i, item in enumerate(suno_data):
            keys = list(item.keys()) if isinstance(item, dict) else 'Not dict'
            print(f"🔧 DEBUG: sunoData[{i}] keys: {keys}")

        # Download the music files and get the actual filenames
        print("🔧 DEBUG: Starting download...")
        downloaded_filenames = downloadingMusic(completed_data, name)
        print("🔧 DEBUG: Download completed")
        print(f"🔧 DEBUG: Downloaded files: {downloaded_filenames}")

        # Create result dictionary for JSON file using actual filenames
        print("🔧 DEBUG: Creating result dictionary...")
        result_dict = {}

        for i, filename_with_path in enumerate(downloaded_filenames):
            print(f"🔧 DEBUG: Processing file {i+1}: {filename_with_path}")

            # Check if we have enough sunoData items
            if i >= len(suno_data):
                msg = f"🔧 DEBUG: ERROR - Trying to access sunoData[{i}]"
                msg += f" but only have {len(suno_data)} items"
                print(msg)
                break

            # Remove music/ prefix and .mp3 extension to get the key
            filename_without_ext = os.path.basename(filename_with_path)
            filename_without_ext = filename_without_ext.replace('.mp3', '')
            audio_id = suno_data[i].get("id", "unknown")
            msg = f"🔧 DEBUG: Audio ID for file {filename_with_path}: "
            msg += f"{audio_id}"
            print(msg)

            result_dict[filename_without_ext] = {
                "paroles": paroles,
                "name": name,
                "style": style,
                "taskId": completed_data["data"]["taskId"],
                "audioId": audio_id,
                "API_KEY": token,
                "file_path": filename_with_path  # Store full path
            }

        print(f"🔧 DEBUG: Created {len(result_dict)} result entries")

        # Save result to JSON file in data directory
        try:
            print("🔧 DEBUG: Saving to JSON...")
            json_path = "data/savedData.json"
            # Load existing data if file exists
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    existing_data = json.load(f)
            else:
                existing_data = {}

            # Update with new data
            existing_data.update(result_dict)

            # Save back to file
            with open(json_path, "w") as f:
                json.dump(existing_data, f, indent=2)

            print("🔧 DEBUG: JSON saved successfully")

        except Exception:
            return "Music generated but failed to save metadata"

        files_generated = len(result_dict)
        msg = "✅ Music '{}' completed successfully!\n".format(name)
        msg += "📁 Generated {} audio files in music/\n".format(files_generated)
        msg += "🎵 Task ID: {}\n".format(task_id)
        msg += "💾 Data saved to data/savedData.json"
        return msg

    except Exception:
        import traceback
        print(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
        return "Error occurred during music generation"


def get_music_list():
    """
    Get a formatted list of all generated music from JSON file.

    Returns:
        str: Formatted string with music information
    """
    try:
        json_path = "data/savedData.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                music_data = json.load(f)

            if not music_data:
                return "No music found"

            # Create a simple text list of music info
            music_list = []
            for key, entry in music_data.items():
                # Use stored file path or construct from key
                file_path = entry.get('file_path', f"music/{key}.mp3")
                music_name = entry.get('name', 'Unknown')
                style = entry.get('style', 'Unknown')
                task_id = entry.get('taskId', 'Unknown')

                # Check if the MP3 file actually exists
                if os.path.exists(file_path):
                    info = "🎵 {}\n".format(music_name)
                    info += "📁 File: {}\n".format(file_path)
                    info += "🎨 Style: {}\n".format(style)
                    info += "🆔 Task ID: {}\n".format(task_id)
                    info += "✅ Status: Available\n"
                else:
                    info = "❌ {}\n".format(music_name)
                    info += "📁 File: {}\n".format(file_path)
                    info += "🎨 Style: {}\n".format(style)
                    info += "🆔 Task ID: {}\n".format(task_id)
                    info += "❌ Status: Missing\n"

                music_list.append(info)

            return "\n" + "=" * 50 + "\n".join(music_list) + "=" * 50
        else:
            return f"No {json_path} file found"
    except Exception:
        return "Error reading music list"


def get_available_audio_files():
    """
    Get list of available audio files for dropdown selection.

    Returns:
        list: List of tuples with (display_name, file_path)
    """
    try:
        json_path = "data/savedData.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                music_data = json.load(f)

            available_files = []
            for key, entry in music_data.items():
                # Use stored file path or construct from key
                file_path = entry.get('file_path', f"music/{key}.mp3")
                if os.path.exists(file_path):
                    music_name = entry.get('name', 'Unknown')
                    style = entry.get('style', 'Unknown')
                    basename = os.path.basename(file_path)
                    display_name = f"{music_name} ({basename}) - {style}"
                    available_files.append((display_name, file_path))

            return available_files
        else:
            return []
    except Exception:
        return []


def load_selected_audio(selected_file):
    """
    Load the selected audio file for playback.

    Args:
        selected_file (str): Path to the selected audio file

    Returns:
        str or None: File path if exists, None otherwise
    """
    if selected_file and os.path.exists(selected_file):
        return selected_file
    else:
        return None


def generate_video_for_music(filename):
    """
    Generate video for a specific music file using stored API key.

    Args:
        filename (str): Filename key from savedData.json

    Returns:
        str: Status message with video generation results
    """
    try:
        print(f"🔧 VIDEO DEBUG: Starting video generation for '{filename}'")

        if not filename:
            return "Please select a music file first"

        # Read the JSON file from data directory
        json_path = "data/savedData.json"
        if not os.path.exists(json_path):
            return "No music data found. Please generate music first."

        print(f"🔧 VIDEO DEBUG: Reading JSON file: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            music_data = json.load(f)

        # Get the music entry directly by filename (key)
        if filename not in music_data:
            return f"Music file '{filename}' not found in saved data"

        music_entry = music_data[filename]
        music_name = music_entry.get('name', filename)

        print(f"🔧 VIDEO DEBUG: Found music entry for '{music_name}'")

        # Extract the required data from the music entry
        taskId = music_entry.get('taskId', '')
        audioId = music_entry.get('audioId', '')
        api_key = music_entry.get('API_KEY', '')

        print("🔧 VIDEO DEBUG: TaskId: {}..., AudioId: {}...".format(
            taskId[:10], audioId[:10]))

        if not taskId or not audioId:
            msg = "Missing taskId or audioId for music file '{}'"
            return msg.format(filename)

        if not api_key:
            msg = "No API key found for music file '{}'.".format(filename)
            msg += " Please regenerate this music."
            return msg

        print("🔧 VIDEO DEBUG: Using stored API key for '{}'".format(filename))
        print("🔧 VIDEO DEBUG: Starting video generation...")

        # Generate the video
        video_response = generateVideo(taskId, audioId, api_key)
        print("🔧 VIDEO DEBUG: Video generation response received")

        if not video_response or video_response.get('code') != 200:
            error_msg = video_response.get('msg', 'Unknown error')
            print("🔧 VIDEO DEBUG: Video generation failed: {}".format(
                error_msg))

            # Check if the error is about existing video (409 error)
            if video_response.get('code') == 409 and "Mp4 record already exists" in error_msg:
                print("🔧 VIDEO DEBUG: Video already exists, retrieving existing video...")

                # Get the taskId from the error response
                existing_taskId = video_response.get('data', {}).get('taskId')
                if not existing_taskId:
                    return "Video exists but no taskId provided in API response"

                print("🔧 VIDEO DEBUG: Existing video taskId: {}".format(existing_taskId))

                try:
                    # Get video details to retrieve the URL
                    print("🔧 VIDEO DEBUG: Getting video details...")
                    video_details = getVideoDetails(existing_taskId, api_key)

                    if not video_details or video_details.get('data', {}).get('successFlag') != 'SUCCESS':
                        return "Could not retrieve existing video details"

                    video_url = video_details['data']['response']['videoUrl']
                    print("🔧 VIDEO DEBUG: Found existing video URL: {}".format(video_url))

                    # Download the existing video using the same filename as MP3
                    print("🔧 VIDEO DEBUG: Downloading existing video...")
                    video_path = downloadVideo(video_url, filename)

                    # Update the music entry with video information
                    music_entry['videoUrl'] = video_url
                    music_entry['videoStatus'] = 'completed'
                    music_entry['video_path'] = video_path
                    music_entry['videoTaskId'] = existing_taskId

                    # Save updated data back to JSON
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(music_data, f, indent=2)

                    return_msg = "✅ Existing video downloaded successfully!\n"
                    return_msg += "📁 Music File: {}.mp3\n".format(filename)
                    return_msg += "🎵 Music: {}\n".format(music_name)
                    return_msg += "🔑 Used stored API key\n"
                    return_msg += "🎬 Video URL: {}\n".format(video_url)
                    return_msg += "📁 Downloaded to: {}\n".format(video_path)
                    return_msg += "ℹ️ This video was already generated by the API"

                    return return_msg

                except Exception as download_error:
                    print("🔧 VIDEO DEBUG: Error downloading existing video: {}".format(str(download_error)))
                    return "Video exists but failed to download: {}".format(str(download_error))

            return "Failed to start video generation: {}".format(error_msg)

        videoTaskId = video_response['data']['taskId']
        msg = "🔧 VIDEO DEBUG: Video generation started with taskId: {}"
        print(msg.format(videoTaskId))

        # Wait for video generation to complete
        print("🔧 VIDEO DEBUG: Waiting for video generation to complete...")
        final_data = waitUntilVideoGen(videoTaskId, api_key)
        print("🔧 VIDEO DEBUG: Video generation wait completed")

        success_check = final_data['data']['successFlag'] != 'SUCCESS'
        if not final_data or success_check:
            status = final_data.get('data', {}).get('successFlag', 'Unknown')
            msg = "🔧 VIDEO DEBUG: Video generation failed with status: {}"
            print(msg.format(status))
            return "Video generation failed or timed out for '{}'".format(
                filename)

        video_url = final_data['data']['response']['videoUrl']
        print("🔧 VIDEO DEBUG: Video generation completed. URL: {}".format(
            video_url))

        # Download the video using the same filename as the MP3
        # (not music_name)
        print("🔧 VIDEO DEBUG: Starting video download...")
        msg = "🔧 VIDEO DEBUG: Using filename '{}' (not music name '{}')"
        print(msg.format(filename, music_name))
        try:
            video_path = downloadVideo(video_url, filename)
            msg = "🔧 DEBUG: File at {} ({} bytes)"
            print(msg.format(video_path, os.path.getsize(video_path)))
        except Exception as download_error:
            msg = "🔧 VIDEO DEBUG: Video download failed: {}"
            print(msg.format(str(download_error)))
            import traceback
            msg = "🔧 VIDEO DEBUG: Download traceback: {}"
            print(msg.format(traceback.format_exc()))
            return "Video generated but download failed: {}".format(
                str(download_error))

        # Update the music entry with video information
        print("🔧 VIDEO DEBUG: Updating JSON with video information...")
        music_entry['videoUrl'] = video_url
        music_entry['videoStatus'] = 'completed'
        music_entry['video_path'] = video_path

        # Save updated data back to JSON
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(music_data, f, indent=2)
            print("🔧 VIDEO DEBUG: JSON updated successfully")
        except Exception as json_error:
            print("🔧 VIDEO DEBUG: JSON update failed: {}".format(
                str(json_error)))
            # Don't fail the whole process for JSON update issues

        # Check if video file actually exists
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            msg = "🔧 DEBUG: File at {} ({} bytes)"
            print(msg.format(video_path, file_size))
        else:
            msg = "🔧 VIDEO DEBUG: WARNING - Video file not found at {}"
            print(msg.format(video_path))

        msg = "✅ Video generated and downloaded successfully!\n"
        msg += "📁 Music File: {}.mp3\n".format(filename)
        msg += "🎵 Music: {}\n".format(music_name)
        msg += "🔑 Used stored API key\n"
        msg += "🎬 Video URL: {}\n".format(video_url)
        msg += "📁 Downloaded to: {}".format(video_path)

        # Add file existence check to the message
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            msg += "\n✅ File confirmed: {} bytes".format(file_size)
        else:
            msg += "\n❌ Warning: File not found at expected location"

        return msg

    except Exception as e:
        msg = "🔧 VIDEO DEBUG: Exception in video generation: {}"
        print(msg.format(str(e)))
        import traceback
        msg = "🔧 VIDEO DEBUG: Full traceback: {}"
        print(msg.format(traceback.format_exc()))
        return "Error generating video: {}".format(str(e))


def get_music_names():
    """
    Get list of filenames for dropdown selection.

    Returns:
        list: List of filename keys from savedData.json
    """
    try:
        json_path = "data/savedData.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                music_data = json.load(f)

            # Return the actual filenames (keys) from savedData.json
            return list(music_data.keys())
        else:
            return []
    except Exception:
        return []


def create_gradio_interface():
    """
    Create and return the main Gradio interface.

    Returns:
        gr.Blocks: The complete Gradio interface
    """
    # Ensure directories exist when creating interface
    create_directories()

    # Create Gradio interface with proper audio support
    with gr.Blocks(title="Suno Music Generator") as demo:
        gr.Markdown("# 🎵 Suno Music Generator")
        gr.Markdown("*Organized with data/, music/, and video/ directories*")

        with gr.Tab("Generate Music"):
            gr.Markdown("## Create New Music")

            with gr.Row():
                token_input = gr.Textbox(
                    label="API Token",
                    placeholder="Enter your Suno API token",
                    type="password"
                )

            with gr.Row():
                name_input = gr.Textbox(
                    label="Music Name",
                    placeholder="Enter the name/title for your music"
                )

            with gr.Row():
                paroles_input = gr.Textbox(
                    label="Paroles (Lyrics)",
                    placeholder="Enter the lyrics for your music",
                    lines=10
                )

            with gr.Row():
                style_input = gr.Textbox(
                    label="Style",
                    placeholder="Enter music style (e.g., 'pop', 'rock')"
                )

            with gr.Row():
                generate_btn = gr.Button("Generate Music",
                                         variant="primary")
                output_text = gr.Textbox(label="Result", lines=3)

            generate_btn.click(
                fn=create_music_with_gradio,
                inputs=[token_input, name_input, paroles_input, style_input],
                outputs=output_text
            )

        with gr.Tab("Music List & Player"):
            gr.Markdown("## 🎵 Generated Music Library")
            gr.Markdown("*Music files are stored in the music/ directory*")

            with gr.Row():
                with gr.Column(scale=1):
                    refresh_list_btn = gr.Button(
                        "🔄 Refresh List",
                        variant="secondary"
                    )

                    # Dropdown to select music file for playing
                    music_selector = gr.Dropdown(
                        label="Select Music to Play",
                        choices=[],
                        value=None,
                        info="Choose a music file to play"
                    )

                    # Audio player
                    audio_player = gr.Audio(
                        label="🎧 Music Player",
                        value=None,
                        interactive=False
                    )

                with gr.Column(scale=1):
                    # Music list display
                    music_list_output = gr.Textbox(
                        label="📋 All Generated Music",
                        value="Loading music list...",
                        lines=15,
                        interactive=False
                    )

            # Function to update both dropdown and list
            def refresh_music_data():
                music_list = get_music_list()
                available_files = get_available_audio_files()
                choices = [display_name for display_name, _ in available_files]
                return music_list, gr.Dropdown(choices=choices, value=None)

            # Function to load selected audio
            def play_selected_music(selected_display_name):
                if not selected_display_name:
                    return None

                # Find the actual filename from the display name
                available_files = get_available_audio_files()
                for display_name, file_path in available_files:
                    if display_name == selected_display_name:
                        return load_selected_audio(file_path)
                return None

            # Event handlers
            refresh_list_btn.click(
                fn=refresh_music_data,
                outputs=[music_list_output, music_selector]
            )

            music_selector.change(
                fn=play_selected_music,
                inputs=music_selector,
                outputs=audio_player
            )

            # Auto-refresh on tab load
            demo.load(
                fn=refresh_music_data,
                outputs=[music_list_output, music_selector]
            )

        with gr.Tab("Generate Video"):
            gr.Markdown("## 🎬 Generate Video for Music")
            gr.Markdown("*Uses API key stored with each music file*")
            gr.Markdown("*Videos are saved in the video/ directory*")

            with gr.Row():
                refresh_music_btn = gr.Button(
                    "🔄 Refresh Music List",
                    variant="secondary"
                )

            with gr.Row():
                music_dropdown = gr.Dropdown(
                    label="Select Music File",
                    choices=get_music_names(),
                    value=None,
                    info="Choose music file (API key used automatically)"
                )

            with gr.Row():
                generate_video_btn = gr.Button(
                    "🎬 Generate Video",
                    variant="primary"
                )
                video_output = gr.Textbox(
                    label="Video Generation Result",
                    lines=5
                )

            # Refresh the dropdown choices
            def refresh_music_list():
                choices = get_music_names()
                return gr.Dropdown(
                    choices=choices,
                    value=None if choices else None
                )

            refresh_music_btn.click(
                fn=refresh_music_list,
                outputs=music_dropdown
            )

            generate_video_btn.click(
                fn=generate_video_for_music,
                inputs=[music_dropdown],
                outputs=video_output
            )

    return demo


if __name__ == "__main__":
    # Launch the interface if this file is run directly
    interface = create_gradio_interface()
    interface.launch(
        debug=True,
        share=False,
        server_name="127.0.0.1",
        server_port=7860
    )
