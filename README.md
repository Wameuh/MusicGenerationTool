# 🎵 Suno Music Generator

A Python application for generating music and videos using the Suno API with a modern Gradio web interface and organized file structure.

## Features

- 🎼 **Music Generation**: Generate music with lyrics using the Suno API
- 🎬 **Video Generation**: Create videos from generated music
- 🎧 **Audio Player**: Built-in web audio player for generated music
- 💾 **Data Management**: Automatic saving and loading of music metadata
- 🔄 **Workflow Management**: Complete generation-to-download workflow
- 🖥️ **Web Interface**: Modern, responsive Gradio interface
- 📁 **Organized Structure**: Automatic directory organization for files

## Project Structure

```
Generation/
├── src/                         # Source code modules
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Main entry point
│   ├── music_generation.py      # Music generation functions
│   ├── video_generation.py      # Video generation functions
│   └── gradio_interface.py      # Gradio web interface
├── data/                        # Data files (auto-created)
│   └── savedData.json           # Music metadata
├── music/                       # Generated music files (auto-created)
│   └── *.mp3                    # Audio files
├── video/                       # Generated video files (auto-created)
│   └── *.mp4                    # Video files
├── requirements.txt             # Python dependencies
├── README.md                   # This file
└── migrate_files.py            # Migration script for existing files
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

#### 3. Generate Videos
- Navigate to the **"Generate Video"** tab
- Click **"🔄 Refresh Music List"** to see available music
- Select a music file from the dropdown
- Click **"🎬 Generate Video"**
- Videos will be saved to `video/` directory
- The system will automatically use the stored API key

## Key Features Explained

### Organized Directory Structure
The application automatically creates and manages three directories:
- **`data/`**: Contains `savedData.json` with all metadata
- **`music/`**: Contains all generated MP3 audio files
- **`video/`**: Contains all generated MP4 video files

### Fixed File Naming System
The application uses a robust file naming system that:
- Ensures sequential numbering (e.g., `Orolunga_1.mp3`, `Orolunga_2.mp3`)
- Prevents file overwrites by checking existing files
- Returns actual downloaded filenames for accurate metadata storage
- Stores full file paths in the JSON metadata

### Automatic API Key Storage
- API keys are stored with each music entry in `data/savedData.json`
- Video generation automatically uses the stored API key
- No need to re-enter API keys for video generation

### Comprehensive Error Handling
- Detailed debug output for troubleshooting
- Graceful error handling throughout the workflow
- Clear user feedback for all operations
- Automatic directory creation when needed

## API Information

This application uses the Suno API endpoints:
- Music Generation: `https://apibox.erweima.ai/api/v1/generate`
- Video Generation: `https://apibox.erweima.ai/api/v1/mp4/generate`

## File Organization

- **Audio**: MP3 format in `music/` directory
- **Video**: MP4 format in `video/` directory
- **Metadata**: JSON format in `data/savedData.json`
- **Paths**: All file paths are stored in metadata for easy reference

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **API Errors**: Verify your API key is correct and has sufficient credits
3. **File Not Found**: Check that generated files exist in the correct directories
4. **Audio Player Issues**: Ensure your browser supports HTML5 audio
5. **Directory Issues**: Run the migration script if you have existing files

### Debug Mode

The application runs in debug mode by default, providing detailed console output for troubleshooting.

### Migration Issues

If you encounter issues with the migration script:
- Ensure you have write permissions in the current directory
- Check that no files are being used by other applications
- Run the script from the project root directory

## Development

### Module Overview

- **`music_generation.py`**: Core music generation logic, API calls, file downloading
- **`video_generation.py`**: Video generation, status monitoring, video downloading
- **`gradio_interface.py`**: Web interface, user interactions, data display
- **`main.py`**: Application entry point and startup logic

### Adding New Features

To extend the application:
1. Add new functions to the appropriate module
2. Update the Gradio interface in `gradio_interface.py`
3. Test thoroughly with debug output
4. Consider directory organization for new file types

## Changelog

### Version 2.0 (Current)
- ✅ Organized directory structure (`data/`, `music/`, `video/`)
- ✅ Automatic directory creation
- ✅ Migration script for existing files
- ✅ Updated file path management
- ✅ Improved metadata storage with full paths
- ✅ Better error handling and user feedback

### Version 1.0 (Previous)
- Basic music and video generation
- Gradio interface
- File naming fixes
- API key parameterization

## License

This project is licensed under the MIT License - see below for details.

### MIT License

```
MIT License

Copyright (c) 2024 Suno Music Generator

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