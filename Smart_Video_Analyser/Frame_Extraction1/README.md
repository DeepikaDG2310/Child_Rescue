
# Frame Extraction V1 - Smart Video Analyzer

## Overview
The **Frame Extraction V1** component of the Smart Video Analyzer is designed to process video files and extract meaningful frames for analysis. This repository provides methods to extract keyframes efficiently, leveraging multiple algorithms, such as histogram-based shot boundary detection, SSIM (Structural Similarity Index Measure), and color space comparison. The primary goal is to create an effective and modular pipeline for video frame extraction.

---

## Features
- **Keyframe Extraction**: Extracts only the most meaningful frames from a video.
- **Customizable Algorithms**: Supports multiple frame extraction methods like:
  - Histogram-based Shot Boundary Detection
  - Structural Similarity Index Measure (SSIM)
  - HSV Color Space Comparison
- **Multiprocessing Support**: Optimized for faster frame extraction using multiple CPU cores.
- **Folder-Based Input**: Processes video files directly from a folder.

---

## Requirements
### Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- pip (Python package manager)

### Dependencies
The required libraries are listed in the `requirements.txt` file. To install all dependencies, run:

```bash
pip install -r requirements.txt
```

---

## Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/umass-forensics/2024-smart-video-analyzer.git
cd 2024-smart-video-analyzer/Frame_Extraction_V1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Usage
### Command-Line Usage
You can run the script from the command line to extract frames from videos stored in a folder:

```bash
python frame_extractor.py --input_folder <path_to_video_folder> --output_folder <path_to_output_folder> --method <method>
```

#### Arguments:
- `--input_folder` (required): Path to the folder containing input videos.
- `--output_folder` (required): Path to save the extracted frames.
- `--method` (optional): Frame extraction method (`histogram`, `ssim`, `color_space`). Default is `histogram`.
- `--multiprocessing` (optional): Enable multiprocessing for faster processing (set as `true` or `false`). Default is `true`.

#### Example:
```bash
python frame_extractor.py --input_folder ./videos --output_folder ./frames --method histogram --multiprocessing true
```

### GUI Usage (Optional)
The repository includes a graphical interface powered by **Gooey** for easy interaction. Run the following command to launch the GUI:

```bash
python frame_extractor.py
```

---

## Output
- Extracted frames will be stored in the specified output folder, organized by subdirectories corresponding to the input video filenames.
- Each frame is named sequentially.

---

## Algorithms Explained
### 1. Histogram-Based Shot Boundary Detection
Compares histograms of consecutive frames to detect significant scene changes and save keyframes accordingly.

### 2. SSIM-Based Keyframe Extraction
Calculates the structural similarity between consecutive frames and saves frames with low similarity scores.

### 3. HSV Color Space Comparison
Compares frames based on their histograms in the HSV color space to identify keyframes.

---

## Optimization
- **Multiprocessing**: Speeds up the frame extraction process by leveraging multiple CPU cores.
- **Custom Thresholds**: Users can fine-tune thresholds for each method to improve keyframe selection accuracy.

---

## Contributing
Contributions are welcome! If you want to contribute:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request with a detailed explanation of your changes.

---

## Issues
If you encounter any issues or bugs, please create an issue in the [GitHub Issue Tracker](https://github.com/umass-forensics/2024-smart-video-analyzer/issues).

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

---


## Acknowledgments
Special thanks to the UMass Forensics team for their contributions and support in building this tool.
