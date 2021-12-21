# social-distancing-tracker

This is a dashboard for monitoring one meter social distancing for outdoor areas using computer vision. This can be implemented realtime on CPU thanks to <a href="https://docs.openvino.ai/latest/index.html" target="_blank">OpenVino</a> model optimisation. To track objects (people), SORT algorithm with Kalmann Filter (tracker) and Hungarian algorithm (data association) has been used. Pre-trained openvino people detection model (MobileNetV2 SSD) has been used for detection. Perspective transformation has been used to get the bird's eye view to enhance the distance measurement accuracy. OpenCV is used for image processing.

Demo: <a href="https://www.youtube.com/watch?v=joDZVKSOvhM" target="_blank">https://www.youtube.com/watch?v=joDZVKSOvhM</a>

<p align="center">
  <img src="https://github.com/tharakarehan/social-distancing-tracker/blob/main/sample_nobbox.gif">
</p>

## Installation

Install <a href="https://docs.openvino.ai/2021.4/get_started.html" target="_blank">OpenVino 2021.4</a>

Create a new conda environment. If you dont have conda installed download [miniconda](https://docs.conda.io/en/latest/miniconda.html)

```bash
conda create -n sdt python=3.8 
```
Clone this repository to your computer and navigate to the directory.

Activate new enviroment
```bash
conda activate std  
```
Install all the libraries used
```bash
pip install -r requirements.txt  
```
Initialize OpenVino
```bash
source /opt/intel/openvino_2021/bin/setupvars.sh  
```

## Usage

Run the script run_sort.py

```bash
usage: run_sort.py [-h] [-i INPUT_FILE] -m MODEL_PATH [-t THRESHOLD]
                   [-o OUTPUT_FILE] [-c CAMERA] [--save] [--find_homography]
                   [--no_bbox] [--slow]

Run SORT

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        input videos file path name
  -m MODEL_PATH, --model_path MODEL_PATH
                        path to the model
  -t THRESHOLD, --threshold THRESHOLD
                        threshold for detections
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        output video file path name
  -c CAMERA, --camera CAMERA
                        camera stream index
  --save                whether to save the video
  --find_homography     if the transformation matrix is not available
  --no_bbox             circles will be drawn instead of bounding boxes
  --slow                reduce the fps of the video if too high
```
With Bounding Boxes for Visualization

<p align="center">
  <img src="https://github.com/tharakarehan/social-distancing-tracker/blob/main/sample_bbox.gif">
</p>

## License

[MIT](https://choosealicense.com/licenses/mit/)

