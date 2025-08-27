# Suggested Directory Structure

```
iphone_photobooth/
│
├── src/                      # Source code
│   ├── capture/             # Camera capture modules
│   │   ├── __init__.py
│   │   ├── usb_camera.py   # USB/Continuity camera handler
│   │   ├── rtsp_stream.py  # RTSP streaming handler
│   │   └── audio.py        # Audio recording module
│   │
│   ├── processing/          # Video/audio processing
│   │   ├── __init__.py
│   │   ├── filters.py      # Video filters & effects
│   │   ├── overlay.py      # Text/image overlays
│   │   └── merger.py       # Audio/video sync & merge
│   │
│   ├── ui/                  # User interface
│   │   ├── __init__.py
│   │   ├── controls.py     # Keyboard/mouse controls
│   │   ├── display.py      # Window management
│   │   └── menu.py         # Settings menu
│   │
│   └── utils/              # Utilities
│       ├── __init__.py
│       ├── device_finder.py # Camera/audio device detection
│       ├── config.py       # Configuration management
│       └── logger.py       # Logging utilities
│
├── effects/                 # Visual effects & filters
│   ├── backgrounds/        # Virtual backgrounds
│   ├── frames/            # Photo frames/borders
│   ├── stickers/          # Overlay stickers
│   └── filters.json       # Filter configurations
│
├── templates/              # Output templates
│   ├── photobooth/        # Classic photobooth layouts
│   │   ├── strip_2x4.psd
│   │   ├── grid_2x2.psd
│   │   └── single.psd
│   └── social/            # Social media templates
│       ├── instagram_square.psd
│       ├── tiktok_vertical.psd
│       └── youtube_thumbnail.psd
│
├── outputs/                # Generated content
│   ├── recordings/        # Video recordings
│   ├── photos/           # Screenshots
│   ├── strips/           # Photo booth strips
│   └── exports/          # Processed exports
│
├── config/                # Configuration files
│   ├── default.yaml      # Default settings
│   ├── presets/          # User presets
│   └── devices.json      # Saved device configs
│
├── tests/                 # Test files
│   ├── test_capture.py
│   ├── test_effects.py
│   └── test_export.py
│
├── docs/                  # Documentation
│   ├── API.md
│   ├── EFFECTS.md
│   └── TROUBLESHOOTING.md
│
├── scripts/              # Utility scripts
│   ├── install.sh       # Installation script
│   ├── calibrate.py     # Camera calibration
│   └── benchmark.py     # Performance testing
│
└── web/                  # Web interface (optional)
    ├── static/
    ├── templates/
    └── app.py           # Flask/FastAPI web UI
```

## Benefits of This Structure:

1. **Modularity**: Separate concerns (capture, processing, UI)
2. **Extensibility**: Easy to add new effects, filters, templates
3. **Organization**: Clear separation of code, assets, outputs
4. **Testing**: Dedicated test directory
5. **Configuration**: Centralized config management
6. **Templates**: Photo booth strip layouts
7. **Effects**: Instagram-like filters and backgrounds
8. **Web Interface**: Optional browser-based control

## Implementation Priority:

1. **Phase 1**: Basic reorganization
   - Move core code to `src/`
   - Create `outputs/` subdirectories
   
2. **Phase 2**: Add effects
   - Implement filters (B&W, vintage, etc.)
   - Add overlay capabilities
   
3. **Phase 3**: Photo booth features
   - Create strip templates
   - Add countdown timer
   - Implement burst mode
   
4. **Phase 4**: Advanced features
   - Web interface
   - Cloud upload
   - Social media integration