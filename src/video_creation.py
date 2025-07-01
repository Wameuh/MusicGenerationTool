"""
Video creation module for generating MP4 videos with timestamped lyrics.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
import requests
from moviepy import AudioFileClip, ImageClip, CompositeVideoClip, TextClip


def get_timestamped_lyrics(api_key: str, task_id: str, audio_id: str,
                           music_index: int = 0) -> Optional[Dict]:
    """
    Fetch timestamped lyrics from Suno API

    Args:
        api_key: Suno API key
        task_id: Task ID from music generation
        audio_id: Audio ID from music generation
        music_index: Music index (default 0)

    Returns:
        Dictionary containing timestamped lyrics or None if failed
    """
    url = "https://apibox.erweima.ai/api/v1/generate/get-timestamped-lyrics"

    payload = json.dumps({
        "taskId": task_id,
        "audioId": audio_id,
        "musicIndex": music_index
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    try:
        print(f"🎵 Fetching timestamped lyrics for audio_id: {audio_id}")
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

        result = response.json()
        print("✅ Successfully fetched timestamped lyrics")
        return result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching timestamped lyrics: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing lyrics response: {e}")
        return None


def save_timestamp_data_to_json(music_filename: str,
                                timestamp_data: Dict) -> bool:
    """
    Save timestamped lyrics data to the JSON file for future use

    Args:
        music_filename: Name of the music file
        timestamp_data: Timestamped lyrics data from API

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        data_file = os.path.join("data", "savedData.json")

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Load existing data
        saved_data = {}
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

        # Add timestamp data to the music entry
        if music_filename not in saved_data:
            saved_data[music_filename] = {}

        saved_data[music_filename]['timestamped_lyrics'] = timestamp_data

        # Save back to file
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(saved_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved timestamped lyrics for {music_filename}")
        return True

    except Exception as e:
        print(f"❌ Error saving timestamp data: {e}")
        return False


def get_cached_timestamp_data(music_filename: str) -> Optional[Dict]:
    """
    Get cached timestamped lyrics data from JSON file

    Args:
        music_filename: Name of the music file

    Returns:
        Cached timestamp data or None if not found
    """
    try:
        data_file = os.path.join("data", "savedData.json")
        if not os.path.exists(data_file):
            return None

        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        if music_filename in saved_data:
            timestamp_data = saved_data[music_filename].get(
                'timestamped_lyrics'
            )
            if timestamp_data:
                print(f"📦 Found cached timestamped lyrics for "
                      f"{music_filename}")
                return timestamp_data

        return None

    except Exception as e:
        print(f"❌ Error reading cached timestamp data: {e}")
        return None


def get_timestamped_lyrics_with_cache(
    music_filename: str,
    api_key: str,
    task_id: str,
    audio_id: str,
    music_index: int = 0
) -> Optional[Dict]:
    """
    Get timestamped lyrics with caching - check cache first, then API

    Args:
        music_filename: Name of the music file
        api_key: Suno API key
        task_id: Task ID from music generation
        audio_id: Audio ID from music generation
        music_index: Music index (default 0)

    Returns:
        Dictionary containing timestamped lyrics or None if failed
    """
    # First, try to get cached data
    cached_data = get_cached_timestamp_data(music_filename)
    if cached_data:
        # Validate cached data
        if (cached_data.get('data') and
                cached_data.get('data', {}).get('alignedWords')):
            print(f"🚀 Using cached timestamped lyrics for {music_filename}")
            return cached_data
        elif cached_data.get('data') is None and cached_data.get('msg'):
            # Cached error (like insufficient credits) - try API again
            print(f"🔄 Cached data shows error, retrying API for "
                  f"{music_filename}")
        else:
            print(f"⚠️ Cached data incomplete, fetching fresh data for "
                  f"{music_filename}")

    # If no valid cache, fetch from API
    print(f"🌐 Fetching fresh timestamped lyrics for {music_filename}")
    fresh_data = get_timestamped_lyrics(api_key, task_id, audio_id,
                                        music_index)

    if fresh_data:
        # Save to cache for future use
        save_timestamp_data_to_json(music_filename, fresh_data)

    return fresh_data


def parse_lyrics_timing(
    lyrics_data: Dict,
    original_lyrics: str = None
) -> List[Tuple[float, float, str]]:
    """
    Parse lyrics timing data from Suno API response into line-based segments
    with improved structural marker filtering and word-to-line matching

    Args:
        lyrics_data: API response containing aligned words
        original_lyrics: Original lyrics text to preserve line structure

    Returns:
        List of tuples: (start_time, end_time, text_line)
    """
    try:
        # Check if API returned an error or insufficient credits
        if not lyrics_data or lyrics_data.get('data') is None:
            error_msg = (lyrics_data.get('msg', 'Unknown error')
                         if lyrics_data else 'No data received')
            print(f"❌ API Error: {error_msg}")

            # Fallback: create segments from original lyrics if available
            if original_lyrics:
                print("🔄 Falling back to original lyrics without timing...")
                lines = [line.strip() for line in original_lyrics.split('\n')
                         if line.strip()]

                # Filter out structural markers
                structural_markers = [
                    'intro', 'couplet', 'verse', 'chorus', 'refrain', 'bridge',
                    'outro', 'pre-chorus', 'post-chorus', 'interlude'
                ]

                lyrics_lines = []
                for line in lines:
                    line_lower = line.lower().strip()
                    is_structural = any(
                        line_lower.startswith(marker)
                        for marker in structural_markers
                    )
                    if not is_structural and len(line.strip()) > 3:
                        lyrics_lines.append(line.strip())

                if lyrics_lines:
                    # Create estimated timing (3 seconds per line)
                    segments = []
                    for i, line in enumerate(lyrics_lines):
                        start_time = float(i * 3)
                        end_time = float((i + 1) * 3)
                        segments.append((start_time, end_time, line))
                        print(f"📝 Line {i+1}: {start_time:.1f}s-"
                              f"{end_time:.1f}s (estimated)")

                    print(f"📝 Created {len(segments)} estimated segments "
                          f"from original lyrics")
                    return segments

            print("❌ No fallback lyrics available")
            return []

        aligned_words = lyrics_data.get('data', {}).get('alignedWords', [])
        if not aligned_words:
            print("❌ No alignedWords found in lyrics data")
            return []

        print(f"📝 Processing {len(aligned_words)} aligned words")

        # Filter out structural markers and clean up words
        structural_markers = [
            'intro', 'couplet', 'verse', 'chorus', 'refrain', 'bridge',
            'outro', 'pre-chorus', 'post-chorus', 'interlude'
        ]

        clean_words = []
        for word_data in aligned_words:
            if not word_data.get('success', True):
                continue

            word_text = word_data.get('word', '').strip()
            if not word_text:
                continue

            # Remove newlines and clean up
            word_text = word_text.replace('\n', ' ').strip()

            # Check if it's a structural marker
            word_lower = word_text.lower().strip()
            is_structural = any(
                word_lower.startswith(marker) or word_lower == marker
                for marker in structural_markers
            )

            # Skip structural markers and very short/empty words
            if not is_structural and len(word_text) > 0:
                start_s = word_data.get('startS', 0)
                end_s = word_data.get('endS', 0)

                clean_words.append({
                    'word': word_text,
                    'start': float(start_s),
                    'end': float(end_s)
                })

        if not clean_words:
            print("❌ No valid words found after filtering")
            return []

        print(f"📝 Cleaned to {len(clean_words)} valid words")

        # Get original lyrics and split into lines
        if not original_lyrics:
            original_lyrics = lyrics_data.get('data', {}).get('lyrics', '')

        if not original_lyrics:
            print("❌ No original lyrics available")
            return []

        # Clean and parse original lyrics into actual lyric lines
        lyrics_lines = []
        for line in original_lyrics.split('\n'):
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()
            is_structural = any(
                line_lower.startswith(marker) or line_lower == marker
                for marker in structural_markers
            )

            if not is_structural and len(line) > 3:
                lyrics_lines.append(line)

        if not lyrics_lines:
            print("❌ No lyric lines found after filtering")
            return []

        print(f"📝 Found {len(lyrics_lines)} lyric lines")

        # Smart word-to-line matching
        segments = []
        word_index = 0

        for line_idx, line_text in enumerate(lyrics_lines):
            # Find words that belong to this line by text matching
            line_words = []
            line_words_text = line_text.lower().split()

            # Look for matching words in sequence
            temp_word_index = word_index
            matched_words = 0

            while (temp_word_index < len(clean_words) and
                   matched_words < len(line_words_text)):
                word_obj = clean_words[temp_word_index]
                word_text = word_obj['word'].lower().strip('.,!?;:')

                # Check if this word matches any word in the line
                for line_word in line_words_text[matched_words:]:
                    if (word_text in line_word or line_word in word_text or
                            word_text == line_word):
                        line_words.append(word_obj)
                        matched_words += 1
                        break

                temp_word_index += 1

                # Prevent infinite loop
                if temp_word_index - word_index > len(line_words_text) * 3:
                    break

            # If we didn't find enough matches, use sequential distribution
            if len(line_words) < len(line_words_text) * 0.3:
                # Fall back to sequential word distribution
                words_per_line = max(1, len(clean_words) // len(lyrics_lines))
                remaining_words = len(clean_words) % len(lyrics_lines)

                words_for_this_line = words_per_line
                if line_idx < remaining_words:
                    words_for_this_line += 1

                line_words = clean_words[
                    word_index:word_index + words_for_this_line
                ]
                word_index += words_for_this_line
            else:
                # Use matched words and advance index
                word_index = temp_word_index

            if line_words:
                start_time = line_words[0]['start']
                end_time = line_words[-1]['end']

                # Ensure minimum duration of 2 seconds
                if end_time - start_time < 2.0:
                    end_time = start_time + 2.0

                segments.append((start_time, end_time, line_text))

                word_preview = ', '.join([w['word'] for w in line_words[:3]])
                if len(line_words) > 3:
                    word_preview += '...'
                print(f"📝 Line {line_idx+1}: {start_time:.1f}s-"
                      f"{end_time:.1f}s ({len(line_words)} words: "
                      f"{word_preview})")
            else:
                # Fallback timing
                if segments:
                    start_time = segments[-1][1]
                else:
                    start_time = float(line_idx * 3)
                end_time = start_time + 3.0

                segments.append((start_time, end_time, line_text))
                print(f"📝 Line {line_idx+1}: {start_time:.1f}s-"
                      f"{end_time:.1f}s (estimated)")

        print(f"📝 Created {len(segments)} line segments with improved "
              f"matching")
        return segments

    except Exception as e:
        print(f"❌ Error parsing lyrics timing: {e}")
        import traceback
        traceback.print_exc()
        return []


def calculate_720p_dimensions(original_width: int,
                              original_height: int) -> tuple:
    """
    Calculate video dimensions capped at 720p while preserving aspect ratio

    Args:
        original_width: Original image width
        original_height: Original image height

    Returns:
        Tuple of (width, height) for 720p-capped video
    """
    # Maximum dimensions for 720p
    max_height = 720
    max_width = 1280  # Standard 16:9 width for 720p

    # If image is already smaller than 720p, keep original size
    if original_height <= max_height and original_width <= max_width:
        return (original_width, original_height)

    # Calculate aspect ratio
    aspect_ratio = original_width / original_height

    # Scale based on which dimension exceeds the limit more
    if original_height > max_height:
        # Scale by height
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
    else:
        # Scale by width
        new_width = max_width
        new_height = int(new_width / aspect_ratio)

    # Ensure we don't exceed either limit
    if new_width > max_width:
        new_width = max_width
        new_height = int(new_width / aspect_ratio)

    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    # Ensure dimensions are even (required for some codecs)
    new_width = new_width if new_width % 2 == 0 else new_width - 1
    new_height = new_height if new_height % 2 == 0 else new_height - 1

    return (new_width, new_height)


def wrap_text_intelligently(
    text: str, max_chars_per_line: int = 50
) -> List[str]:
    """
    Split text into 1-2 lines intelligently based on word boundaries

    Args:
        text: Text to wrap
        max_chars_per_line: Maximum characters per line

    Returns:
        List of lines (1-2 lines maximum)
    """
    if len(text) <= max_chars_per_line:
        return [text]

    # Try to split at a natural break point
    words = text.split()
    if len(words) <= 1:
        return [text[:max_chars_per_line], text[max_chars_per_line:]]

    # Find the best split point around the middle
    mid_point = len(text) // 2
    best_split = len(words) // 2

    # Look for a split point close to the middle
    current_length = 0
    for i, word in enumerate(words):
        current_length += len(word) + (1 if i > 0 else 0)  # +1 for space
        if current_length >= mid_point:
            best_split = i
            break

    # Create two lines
    line1 = ' '.join(words[:best_split])
    line2 = ' '.join(words[best_split:])

    # If second line is too long, truncate first line a bit more
    if len(line2) > max_chars_per_line and best_split > 1:
        best_split -= 1
        line1 = ' '.join(words[:best_split])
        line2 = ' '.join(words[best_split:])

    return [line1, line2] if line2 else [line1]


def create_video_with_lyrics(
    audio_file: str,
    background_image: str,
    lyrics_segments: List[Tuple[float, float, str]],
    output_path: str,
    font_size: int = 48,
    font_color: str = 'white',
    stroke_color: str = 'black',
    stroke_width: int = 2,
    status_callback=None
) -> bool:
    """
    Create a video with background image and synchronized lyrics

    Features:
    - Synchronized text display with fade effects
    - Improved text wrapping and encoding handling
    - Centered positioning with smooth transitions

    Args:
        audio_file: Path to the MP3 audio file
        background_image: Path to the background image
        lyrics_segments: List of (start_time, end_time, text) tuples
        output_path: Output video file path
        font_size: Font size for lyrics
        font_color: Font color for lyrics
        stroke_color: Stroke color for text outline
        stroke_width: Stroke width for text outline
        status_callback: Optional callback function for status updates

    Returns:
        True if successful, False otherwise
    """
    try:
        if status_callback:
            status_callback("🎬 Starting synchronized video creation...")
        print(f"🎬 Creating synchronized video: {output_path}")

        # Load audio clip
        if status_callback:
            status_callback("🎵 Loading audio file...")
        audio_clip = AudioFileClip(audio_file)
        duration = audio_clip.duration
        print(f"🎵 Audio duration: {duration:.2f} seconds")

        # Prepare background image and get its dimensions
        if status_callback:
            status_callback("🖼️ Analyzing background image...")

        # Create temporary image clip to get original dimensions
        temp_bg_clip = ImageClip(background_image)
        original_size = temp_bg_clip.size  # (width, height)
        temp_bg_clip.close()

        # Calculate optimal video size (720p with aspect ratio preserved)
        video_size = calculate_720p_dimensions(original_size[0],
                                               original_size[1])

        print(f"🖼️ Original: {original_size[0]}x{original_size[1]}px")
        print(f"🖼️ Optimized: {video_size[0]}x{video_size[1]}px")
        if status_callback:
            status_callback(f"🖼️ Video: {video_size[0]}x{video_size[1]}px")

        # Create background clip
        background_clip = ImageClip(background_image, duration=duration)
        if video_size != original_size:
            background_clip = background_clip.resized(video_size)

        # Scale font size for video resolution
        scaled_font_size = int(font_size * (video_size[1] / 1080))
        print(f"📝 Font size: {scaled_font_size}px")
        if status_callback:
            status_callback(f"📝 Font size: {scaled_font_size}px")

        # Calculate text wrapping
        max_chars_per_line = int(video_size[0] / (scaled_font_size * 0.6))
        max_chars_per_line = max(30, min(max_chars_per_line, 60))
        print(f"📝 Max chars per line: {max_chars_per_line}")

        # Create synchronized lyrics system
        if status_callback:
            status_callback("📝 Creating synchronized lyrics...")

        all_text_clips = []

        for segment_idx, (start_time, end_time, text) in enumerate(
                lyrics_segments):
            if start_time >= duration:
                continue

            actual_end_time = min(end_time, duration)
            segment_duration = actual_end_time - start_time

            # Fix text encoding
            try:
                display_text = fix_double_utf8_encoding(text)
                if isinstance(display_text, str):
                    display_text = display_text.encode('utf-8').decode('utf-8')
                else:
                    display_text = str(display_text)
            except (UnicodeEncodeError, UnicodeDecodeError):
                display_text = text.replace('é', 'e').replace(
                    'è', 'e').replace('à', 'a').replace('ç', 'c')

            # Wrap text intelligently
            current_lines = wrap_text_intelligently(
                display_text, max_chars_per_line
            )
            current_text = '\n'.join(current_lines)

            # Create CURRENT text clip only (simplified)
            if current_text.strip():
                # Create simple centered text with fade effects
                text_clip = TextClip(
                    font="arial",
                    text=current_text,
                    font_size=scaled_font_size,
                    color=font_color,
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                    text_align='center'
                ).with_start(start_time).with_duration(segment_duration)

                # Position at center
                center_y = int(video_size[1] * 0.75)
                text_clip = text_clip.with_position(('center', center_y))

                # Add smooth fade effects
                from moviepy.video.fx import FadeIn, FadeOut
                fade_time = min(0.5, segment_duration / 4)
                text_clip = text_clip.with_effects([
                    FadeIn(fade_time),
                    FadeOut(fade_time)
                ])

                all_text_clips.append(text_clip)

        print(f"📝 Created {len(all_text_clips)} synchronized text clips")

        # Compose final video
        if status_callback:
            status_callback("🎬 Composing synchronized video...")
        final_video = CompositeVideoClip([background_clip] + all_text_clips)
        final_video = final_video.with_audio(audio_clip)

        # Render video with GPU acceleration
        if status_callback:
            status_callback("💾 Rendering synchronized video...")
        print("💾 Writing synchronized video...")

        gpu_success = False
        audio_params = ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                        '-ac', '2']

        try:
            # Try NVIDIA GPU first
            if status_callback:
                status_callback("🚀 Trying NVIDIA GPU...")
            final_video.write_videofile(
                output_path,
                fps=24,
                threads=64,
                codec='h264_nvenc',
                audio_codec='aac',
                ffmpeg_params=[
                    '-preset', 'medium',
                    '-profile:v', 'high',
                    '-level:v', '4.1',
                    '-crf', '20',
                    '-maxrate', '5M',
                    '-bufsize', '10M'
                ] + audio_params
            )
            gpu_success = True
            if status_callback:
                status_callback("✅ NVIDIA GPU success!")

        except Exception as nvidia_error:
            print(f"⚠️ NVIDIA failed: {nvidia_error}")

            try:
                # Try AMD GPU
                if status_callback:
                    status_callback("🚀 Trying AMD GPU...")
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    threads=64,
                    codec='h264_amf',
                    audio_codec='aac',
                    ffmpeg_params=[
                        '-quality', 'quality',
                        '-rc', 'cqp',
                        '-qp_i', '20',
                        '-qp_p', '22',
                        '-profile:v', 'high'
                    ] + audio_params
                )
                gpu_success = True
                if status_callback:
                    status_callback("✅ AMD GPU success!")

            except Exception:
                gpu_success = False

        # CPU fallback
        if not gpu_success:
            if status_callback:
                status_callback("⚠️ Using CPU encoding...")
            final_video.write_videofile(
                output_path,
                fps=24,
                threads=16,
                codec='libx264',
                audio_codec='aac',
                ffmpeg_params=[
                    '-preset', 'medium',
                    '-crf', '20',
                    '-profile:v', 'high',
                    '-level:v', '4.1',
                    '-movflags', '+faststart'
                ] + audio_params
            )
            if status_callback:
                status_callback("✅ CPU encoding done!")

        # Cleanup
        if status_callback:
            status_callback("🧹 Cleaning up...")
        audio_clip.close()
        background_clip.close()
        final_video.close()
        for clip in all_text_clips:
            if hasattr(clip, 'close'):
                clip.close()

        if status_callback:
            status_callback("✅ Synchronized video created!")
        print(f"✅ Synchronized video created: {output_path}")
        return True

    except Exception as e:
        if status_callback:
            status_callback(f"❌ Error: {str(e)}")
        print(f"❌ Error creating synchronized video: {e}")
        return False


def get_music_info_for_video_creation(music_filename: str) -> Optional[Dict]:
    """
    Get music information including API key, task_id, and audio_id
    for video creation

    Args:
        music_filename: The music file name (e.g., "Orolunga_1.mp3")

    Returns:
        Dictionary with music info or None if not found
    """
    try:
        data_file = os.path.join("data", "savedData.json")
        if not os.path.exists(data_file):
            print(f"❌ Data file not found: {data_file}")
            return None

        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        if music_filename in saved_data:
            music_info = saved_data[music_filename]
            required_fields = ['API_KEY', 'taskId', 'audioId']

            if all(field in music_info for field in required_fields):
                return music_info
            else:
                missing_fields = [field for field in required_fields
                                  if field not in music_info]
                print(f"❌ Missing required fields for {music_filename}: "
                      f"{missing_fields}")
                return None
        else:
            print(f"❌ Music file not found in saved data: {music_filename}")
            return None

    except Exception as e:
        print(f"❌ Error reading music info: {e}")
        return None


def create_video_workflow(
    music_filename: str,
    background_image_path: str,
    output_filename: str = None,
    status_callback=None
) -> Tuple[bool, str]:
    """
    Complete workflow to create a video with lyrics overlay

    Args:
        music_filename: Name of the music file (e.g., "Orolunga_1.mp3")
        background_image_path: Path to the background image
        output_filename: Custom output filename (optional)
        status_callback: Optional callback function for status updates

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        if status_callback:
            status_callback("🔍 Getting music information...")

        # Get music information
        music_info = get_music_info_for_video_creation(music_filename)
        if not music_info:
            return False, (
                f"Could not get music information for {music_filename}"
            )

        # Construct paths
        # Add .mp3 extension if not already present
        if not music_filename.endswith('.mp3'):
            audio_file_path = os.path.join("music", f"{music_filename}.mp3")
        else:
            audio_file_path = os.path.join("music", music_filename)
        if not os.path.exists(audio_file_path):
            return False, f"Audio file not found: {audio_file_path}"

        if not os.path.exists(background_image_path):
            return False, (
                f"Background image not found: {background_image_path}"
            )

        # Generate output filename
        if not output_filename:
            base_name = os.path.splitext(music_filename)[0]
            output_filename = f"{base_name}_lyrics_video.mp4"

        output_path = os.path.join("video", output_filename)

        # Ensure video directory exists
        os.makedirs("video", exist_ok=True)

        # Fetch timestamped lyrics
        if status_callback:
            status_callback(f"🎵 Fetching lyrics for {music_filename}...")
        print(f"🎵 Fetching lyrics for {music_filename}")
        lyrics_data = get_timestamped_lyrics_with_cache(
            music_filename,
            music_info['API_KEY'],
            music_info['taskId'],
            music_info['audioId']
        )

        if not lyrics_data:
            return False, "Failed to fetch timestamped lyrics from Suno API"

        # Parse lyrics timing
        if status_callback:
            status_callback("🔍 Parsing lyrics timing...")

        # Get original lyrics from saved data for better line structure
        original_lyrics = music_info.get('paroles', '')
        # Fix double UTF-8 encoding issues
        original_lyrics = fix_double_utf8_encoding(original_lyrics)
        lyrics_segments = parse_lyrics_timing(lyrics_data, original_lyrics)
        if not lyrics_segments:
            return False, "No valid lyrics segments found"

        # Create the video (this will handle progress from 0.1 to 1.0)
        success = create_video_with_lyrics(
            audio_file=audio_file_path,
            background_image=background_image_path,
            lyrics_segments=lyrics_segments,
            output_path=output_path,
            status_callback=status_callback
        )

        if success:
            return True, f"Video created successfully: {output_path}"
        else:
            return False, "Failed to create video"

    except Exception as e:
        if status_callback:
            status_callback(f"❌ Error: {str(e)}")
        return False, f"Error in video creation workflow: {e}"


def get_available_music_files() -> List[str]:
    """
    Get list of available music files for video creation

    Returns:
        List of music filenames
    """
    try:
        data_file = os.path.join("data", "savedData.json")
        if not os.path.exists(data_file):
            return []

        with open(data_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        # Filter files that have required fields for video creation
        available_files = []
        required_fields = ['API_KEY', 'taskId', 'audioId']

        for filename, info in saved_data.items():
            if all(field in info for field in required_fields):
                # Check if the actual music file exists
                # Add .mp3 extension if not already present
                if not filename.endswith('.mp3'):
                    music_path = os.path.join("music", f"{filename}.mp3")
                else:
                    music_path = os.path.join("music", filename)
                if os.path.exists(music_path):
                    available_files.append(filename)

        return sorted(available_files)

    except Exception as e:
        print(f"❌ Error getting available music files: {e}")
        return []


# Video creation interface function for Gradio
def create_video_gradio_interface(music_file: str, background_image):
    """
    Gradio interface function for creating videos with lyrics overlay

    Args:
        music_file: Selected music file name
        background_image: Uploaded background image

    Returns:
        Generator yielding (status_message, video_file_path) tuples
    """
    if not music_file:
        yield "❌ Please select a music file", None
        return

    if background_image is None:
        yield "❌ Please upload a background image", None
        return

    try:
        # Set up status message collection
        status_messages = []
        created_video_path = None

        def status_callback(message):
            status_messages.append(message)
            print(message)

        # Start video creation with real-time updates
        status_callback("🚀 Starting video creation process...")
        yield "\n".join(status_messages), None

        # Get music information
        status_callback("🔍 Getting music information...")
        yield "\n".join(status_messages), None

        # Get music info
        music_info = get_music_info_for_video_creation(music_file)
        if not music_info:
            status_callback(
                f"❌ Could not get music information for {music_file}"
            )
            yield "\n".join(status_messages), None
            return

        # Validate paths
        if not music_file.endswith('.mp3'):
            audio_file_path = os.path.join("music", f"{music_file}.mp3")
        else:
            audio_file_path = os.path.join("music", music_file)

        if not os.path.exists(audio_file_path):
            status_callback(f"❌ Audio file not found: {audio_file_path}")
            yield "\n".join(status_messages), None
            return

        if not os.path.exists(background_image.name):
            status_callback(
                f"❌ Background image not found: {background_image.name}"
            )
            yield "\n".join(status_messages), None
            return

        # Fetch lyrics
        status_callback(f"🎵 Fetching lyrics for {music_file}...")
        yield "\n".join(status_messages), None

        lyrics_data = get_timestamped_lyrics_with_cache(
            music_file,
            music_info['API_KEY'],
            music_info['taskId'],
            music_info['audioId']
        )

        if not lyrics_data:
            status_callback(
                "❌ Failed to fetch timestamped lyrics from Suno API"
            )
            yield "\n".join(status_messages), None
            return

        # Parse lyrics
        status_callback("🔍 Parsing lyrics timing...")
        yield "\n".join(status_messages), None

        original_lyrics = music_info.get('paroles', '')
        # Fix double UTF-8 encoding issues
        original_lyrics = fix_double_utf8_encoding(original_lyrics)
        lyrics_segments = parse_lyrics_timing(lyrics_data, original_lyrics)
        if not lyrics_segments:
            status_callback("❌ No valid lyrics segments found")
            yield "\n".join(status_messages), None
            return

        # Create video
        status_callback("🎬 Creating video...")
        yield "\n".join(status_messages), None

        # Generate output path
        base_name = os.path.splitext(music_file)[0]
        output_filename = f"{base_name}_lyrics_video.mp4"
        output_path = os.path.join("video", output_filename)
        os.makedirs("video", exist_ok=True)

        # Create video with status updates
        success = create_video_with_lyrics(
            audio_file=audio_file_path,
            background_image=background_image.name,
            lyrics_segments=lyrics_segments,
            output_path=output_path,
            status_callback=status_callback
        )

        # Update after each major step
        yield "\n".join(status_messages), None

        if success:
            created_video_path = f"video/{output_filename}"
            status_callback(f"✅ Video created successfully: {output_path}")
            final_message = (
                "\n".join(status_messages) +
                "\n\n✅ Video creation completed!"
            )
        else:
            status_callback("❌ Failed to create video")
            final_message = (
                "\n".join(status_messages) +
                "\n\n❌ Video creation failed!"
            )

        yield final_message, created_video_path

    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        yield error_msg, None


def fix_double_utf8_encoding(text: str) -> str:
    """
    Fix double UTF-8 encoding issues in text

    Args:
        text: Text that may have double UTF-8 encoding

    Returns:
        Corrected text with proper UTF-8 encoding
    """
    if not text:
        return text

    try:
        # Try to detect and fix double UTF-8 encoding
        # First encode as Latin-1 to get the raw bytes, then decode as UTF-8
        corrected = text.encode('latin-1').decode('utf-8')
        return corrected
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            # Alternative method: handle common problematic sequences
            fixes = {
                'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
                'Ã ': 'à', 'Ã¨': 'è', 'Ã¬': 'ì', 'Ã²': 'ò', 'Ã¹': 'ù',
                'Ã¢': 'â', 'Ãª': 'ê', 'Ã®': 'î', 'Ã´': 'ô', 'Ã»': 'û',
                'Ã£': 'ã', 'Ã±': 'ñ', 'Ã§': 'ç', 'Ã¤': 'ä', 'Ã¶': 'ö',
                'Ã¼': 'ü', 'Ã¿': 'ÿ', 'Ã…': 'Å', 'Ã†': 'Æ', 'Ã˜': 'Ø'
            }

            result = text
            for bad, good in fixes.items():
                result = result.replace(bad, good)
            return result
        except Exception:
            # Last fallback: return original text
            return text




