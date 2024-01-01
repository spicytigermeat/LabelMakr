# SOFA_GUI
GUI Tool for Whisper Transcription and SOFA Alignment

![image](https://github.com/spicytigermeat/SOFA_GUI/assets/103609620/710821bc-f612-4423-b7a8-bd13c70a02e7)

Please use the portable version for Windows found [here](https://github.com/spicytigermeat/SOFA_GUI/releases/tag/v0.0.1)

# Manual installation

If you'd like to install this manually, follow these steps!
Requirements:
- anaconda3
- Windows/Linux (Tested on Win11/Ubuntu 22.04 with conda)

Known issues:
- It looks really ugly on Linux (issue with customtkinter being ran on python 3.8, not a priority to fix rn)

1: Create a new environment and activate it, then CD to an empty folder.

Windows:
```
conda create -n sofa_gui python=3.8 -y
conda activate sofa_gui
cd {path_to_folder}
```
Linux:
```
conda create -n sofa_gui python=3.8 -y
source activate sofa_gui
cd {path_to_folder}
```

2: Manually install torch.

Windows:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
Linux:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3: Install SOFA_GUI

Windows:
```
git clone https://github.com/spicytigermeat/SOFA_GUI.git
pip install -r requirements.txt
```
Linux:
```
git clone https://github.com/spicytigermeat/SOFA_GUI.git
pip3 install -r requirements.txt
```

4: Install SOFA

Windows:
```
cd SOFA_GUI
git clone https://github.com/qiuqiao/SOFA.git
pip install -r SOFA/requirements.txt
```

Linux:
```
cd SOFA_GUI
git clone https://github.com/qiuqiao/SOFA.git
pip install -r SOFA/requirements.txt
```

5: Manually install the SOFA Model.

Download the files from [this release](https://github.com/spicytigermeat/SOFA-Models/releases/tag/v0.0.4).

Place "tgm_sofa_v004.ckpt" in `SOFA_GUI/SOFA/ckpt`
Place "tgm_sofa_dict.txt" in `SOFA_GUI/SOFA/dictionary`

This should work, please let me know if any steps listed here do not achieve the desired result!

