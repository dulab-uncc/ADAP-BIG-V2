# ADAP-3D_V2

ADAP-3D_V2 is a software that detects peaks in mass spectrometry data using object detection and image processing through the YOLOv5 algorithm and preprocessing blocking methods.


## YoloV5 Pytorch Model Training
Model training notebook:
https://colab.research.google.com/drive/1Zfc0K-rSsAA366ymqeoTUNEbx3bATYP8?usp=sharing

Labeling website:
[hasty.ai](url)

Export YoloV5 Pytorch formatted data:
[roboflow.com](url)

## Workflow

![Untitled Diagram drawio](https://user-images.githubusercontent.com/82981121/133908890-de9c1ced-aad1-4003-82d4-b6e1f3a0b6a4.png)

## Installation

CD to the folder with requirements.txt and run this command in the terminal:

```bash
pip install requirements.txt
```

## Usage

```python
python adap_3d_main.py
```

## Adjust Parameters

Navigate to params.py in the adap-3d-cli directory and adjust parameters in this module

## Results

YoloV5 inferences stored in the cloned repo runs folder.

Exports one `.csv` file to user specified `results path` (user can specify in `params.py`) containing:
  - Block # peak is located in
  - M/Z value of peak
  - Retention Time value of peak
  - M/Z and Retention Time ranges
  - Confidence of model on specified peak

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
