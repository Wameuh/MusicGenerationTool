"""
Main Entry Point

This is the main entry point for the Suno Music Generator application.
Run this file to start the Gradio web interface with organized directories.
"""

from music_generation import create_directories
from gradio_interface import create_gradio_interface


def main():
    """
    Main function to launch the Suno Music Generator interface.
    """
    print("🎵 Starting Suno Music Generator...")
    print("📂 Setting up organized directory structure...")

    # Create the organized directory structure
    create_directories()

    print("📁 Directory structure:")
    print("   ├── data/        (for savedData.json)")
    print("   ├── music/       (for MP3 files)")
    print("   └── video/       (for MP4 files)")

    try:
        # Create the Gradio interface
        print("📦 Loading interface modules...")
        interface = create_gradio_interface()

        print("✅ Interface created successfully!")
        print("🚀 Launching web interface...")
        print("📍 Access the interface at: http://127.0.0.1:7860")
        print("")
        print("🎯 Features:")
        print("   • Generate music → saved to music/")
        print("   • Generate videos → saved to video/")
        print("   • Data management → saved to data/")
        print("   • Built-in audio player")
        print("   • Automatic API key storage")
        print("")

        # Launch the interface
        interface.launch(
            debug=True,
            share=False,
            server_name="127.0.0.1",
            server_port=7860
        )

    except Exception as e:
        print(f"❌ Error starting the application: {str(e)}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install gradio requests")
        print("💡 Make sure you're running from the project root directory")


if __name__ == "__main__":
    main()
