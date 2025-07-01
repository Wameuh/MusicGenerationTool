# 🎵 Suno API Wrapper

A comprehensive Python wrapper for the Suno API that enables music generation and video creation with synchronized lyrics through a modern Gradio web interface.

## Features

- 🎼 **Music Generation**: Generate music with lyrics using the Suno API
- 🎬 **Video Creation**: Create videos with synchronized lyrics overlay from generated music
- 🎯 **Smart Caching**: Automatic timestamped lyrics caching to avoid repeated API calls
- 🎧 **Audio Player**: Built-in web audio player for generated music
- 💾 **Data Management**: Automatic saving and loading of music metadata
- 🔄 **Workflow Management**: Complete generation-to-video workflow
- 🖥️ **Web Interface**: Modern, responsive Gradio interface
- 📁 **Organized Structure**: Automatic directory organization for files

## Project Structure

```
Generation/
├── src/                         # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main entry point
│   ├── music_generation.py      # Music generation functions
│   ├── video_generation.py      # Video generation functions (legacy)
│   ├── video_creation.py        # New video creation with synchronized lyrics
│   └── gradio_interface.py      # Gradio web interface
├── data/                        # Data files (auto-created)
│   └── savedData.json           # Music metadata and cached timestamps
├── music/                       # Generated music files (auto-created)
│   └── *.mp3                    # Audio files
├── video/                       # Generated video files (auto-created)
│   └── *.mp4                    # Video files with synchronized lyrics
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## Installation

1. **Clone or download** this project to your local machine

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Suno API key** from the Suno API service

## Usage

### Starting the Application

Run the main application:

```bash
python src/main.py
```

The web interface will be available at: `http://127.0.0.1:7860`

### Using the Interface

#### 1. Generate Music
- Navigate to the **"Generate Music"** tab
- Enter your Suno API token
- Provide a music name/title
- Enter lyrics (paroles)
- Specify the music style
- Click **"Generate Music"**
- Files will be saved to `music/` directory

#### 2. Listen to Generated Music
- Go to the **"Music List & Player"** tab
- Click **"🔄 Refresh List"** to see your generated music
- Select a music file from the dropdown
- Use the built-in audio player to listen

#### 3. Create Videos with Synchronized Lyrics
- Navigate to the **"Video Creation"** tab
- Click **"🔄 Refresh Music List"** to see available music
- Select a music file from the dropdown
- Upload a background image
- Click **"🎬 Create Video"**
- Videos with synchronized lyrics will be saved to `video/` directory

## Key Features Explained

### Synchronized Lyrics Video Creation
The application creates professional videos with:
- **Timestamped Lyrics**: Precise synchronization with audio using Suno API
- **Smart Caching**: Lyrics timing data cached to avoid repeated API calls
- **Text Animation**: Smooth fade in/out effects for lyrics display
- **Intelligent Text Wrapping**: Automatic line breaks for optimal readability
- **720p Optimization**: Videos optimized for 720p while preserving aspect ratio
- **GPU Acceleration**: Automatic GPU detection (NVIDIA/AMD) with CPU fallback
- **Encoding Fixes**: Automatic correction of UTF-8 encoding issues

### Organized Directory Structure
The application automatically creates and manages:
- **`data/`**: Contains `savedData.json` with metadata and cached timestamps
- **`music/`**: Contains all generated MP3 audio files
- **`video/`**: Contains all generated MP4 video files with synchronized lyrics

### Smart Lyrics Processing
The system includes advanced lyrics processing:
- **Structural Filtering**: Removes intro/verse/chorus markers from display
- **Word-to-Line Matching**: Intelligent mapping of timestamped words to lyrics lines
- **Fallback System**: Graceful degradation when API limits are reached
- **French Character Support**: Proper handling of accented characters

### Automatic API Key Storage
- API keys are stored with each music entry in `data/savedData.json`
- Video creation automatically uses the stored API key
- Timestamped lyrics are cached to minimize API usage

## Technical Specifications

### Video Creation Features
- **Resolution**: 720p with aspect ratio preservation
- **Font**: Arial with customizable size and stroke
- **Positioning**: Centered text at 75% screen height
- **Effects**: Fade in/out transitions for smooth display
- **Audio**: High-quality AAC encoding at 256kbps
- **Performance**: GPU-accelerated encoding when available

### Supported Formats
- **Audio Input**: MP3 format
- **Video Output**: MP4 format with H.264 encoding
- **Background Images**: JPEG, PNG formats
- **Text Encoding**: UTF-8 with automatic correction

## API Information

This application uses the Suno API endpoints:
- Music Generation: `https://apibox.erweima.ai/api/v1/generate`
- Video Generation: `https://apibox.erweima.ai/api/v1/mp4/generate`
- Timestamped Lyrics: `https://apibox.erweima.ai/api/v1/generate/get-timestamped-lyrics`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **API Errors**: Verify your API key is correct and has sufficient credits
3. **Video Creation Issues**: Ensure background image is a valid image file
4. **Audio Player Issues**: Ensure your browser supports HTML5 audio
5. **Insufficient Credits**: The system will use cached data when API credits are low

### Video Creation Troubleshooting

- **Black Screen**: Check that background image path is correct
- **No Text**: Verify that lyrics exist in the saved data
- **Encoding Errors**: System automatically handles most UTF-8 issues
- **Slow Rendering**: GPU acceleration is attempted first, then CPU fallback

### Debug Mode

The application provides detailed console output for troubleshooting all operations.

## Development

### Module Overview

- **`music_generation.py`**: Core music generation logic, API calls, file downloading
- **`video_creation.py`**: Advanced video creation with synchronized lyrics and caching
- **`video_generation.py`**: Legacy video generation (basic functionality)
- **`gradio_interface.py`**: Web interface, user interactions, data display
- **`main.py`**: Application entry point and startup logic

### Adding New Features

To extend the application:
1. Add new functions to the appropriate module
2. Update the Gradio interface in `gradio_interface.py`
3. Test thoroughly with debug output
4. Consider caching strategies for API-dependent features

## License

This project is licensed under the MIT License.

### MIT License

```
MIT License

Copyright (c) 2024 Suno API Wrapper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Note**: Please respect the Suno API terms of service when using this application.

## Contributing

Feel free to submit issues and pull requests to improve the application.

---

**Note**: Make sure you have a valid Suno API key and sufficient credits before using the application.