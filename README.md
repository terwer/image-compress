[中文](README_zh_CN.md)

# Image Compress

Compress images to the exact size you need without sacrificing quality.

## Standard Usage

```bash
python cli/main.py -v -s 15 -c 0.5 data/icon.png -o data/icon_compressed.png
python cli/main.py -f WEBP -v -q 75 data/icon.png -o data/icon_compressed.png
python cli/main.py -f WEBP -v -c 0.5 -q 55 data/icon.png -o data/icon_compressed.png
python cli/main.py -v -s 180 data/preview.png -o data/preview_compressed.png
python cli/main.py -f WEBP -v -q 75 data/preview.png -o data/preview_compressed.png
```

More options: 

```bash
python cli/main.py -h
```

## Standalone Executable Version

This tool can also be packaged as a standalone executable file that runs without a Python environment:

1. Install packaging tools:
   ```bash
   pip install pyinstaller pillow
   ```

2. Package the tool:
   ```bash
   pyinstaller --onefile --windowed standalone_image_compressor.py
   ```

3. Find the executable in the `dist/` folder and use it directly:
   ```bash
   ./dist/standalone_image_compressor input.jpg -o output.jpg -q 80
   ./dist/standalone_image_compressor input.jpg -o output.jpg -s 20
   ./dist/standalone_image_compressor -d images_folder -o compressed_folder
   ```

On Windows systems, the executable will have a `.exe` extension.

## Cross-Platform Support

The standalone version works on all major platforms:

- **Windows**: `.exe` file
- **macOS**: Standalone executable
- **Linux**: Standalone executable

For Linux package management systems:
- **DEB packages** for Debian/Ubuntu
- **RPM packages** for Red Hat/CentOS/Fedora

### Building for Different Platforms

Use the cross-platform build script to create executables for different platforms:

```bash
# Build for current platform
python simple_cross_platform_build.py

# Build for specific platform
python simple_cross_platform_build.py --platform windows
python simple_cross_platform_build.py --platform darwin
python simple_cross_platform_build.py --platform linux

# Build for all platforms
python simple_cross_platform_build.py --all

# Create Linux packages (requires dpkg-deb and rpmbuild)
python simple_cross_platform_build.py --platform linux --packages
```

## GitHub Actions Automation

This repository includes GitHub Actions workflows to automatically build and release executables for all platforms:

- **Workflow file**: [.github/workflows/build-release.yml](.github/workflows/build-release.yml)
- **Trigger**: Push a tag starting with `v` (e.g., `v1.0.0`)
- **Platforms**: Windows, macOS, and Linux
- **Output**: GitHub Release with executables for all platforms

### Creating a New Release

To create a new release with automated builds:

```bash
# Commit your changes
git add .
git commit -m "Prepare for release"

# Create and push a new tag
git tag v1.0.0
git push origin main --tags
```

The GitHub Actions workflow will automatically:
1. Build executables for Windows, macOS, and Linux
2. Create a new GitHub Release
3. Upload all executables as release assets