# ADAP-BIG-V2

ADAP-BIG-V2 is a software that detects peaks in mass spec data using object detection and image processing through the YOLOv5 algorithm


## YoloV5 Pytorch Model Training
Model training notebook:
https://colab.research.google.com/drive/1vu1k6z1g4rmgjnz271kcRZLEP1_-K79M?usp=sharing

## Workflow
![ADAP-3D-V2 Draft Workflow](https://user-images.githubusercontent.com/82981121/129616586-56591c73-2434-4297-bcc3-f680e05477fd.PNG)

## Installation

CD to the folder with requirements.txt and run this command in the terminal:

```bash
pip install requirements.txt
```

## Usage

```python
python ADAP-BIG-OBJECT-DETECTION.py
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
