SOFA_GUI - created by tigermeat.

##############
#	CREDIT	 #
##############

SOFA developed by qiuqiao
Whisper created by OpenAI

tgm_sofa English SOFA Model created by tigermeat
colstone_jpn Japanese SOFA Model created by colstone

GUI Translations:
Japanese: tigermeat
Chinese: ArchiVoice
Indonesian: Koji

#############
#	USAGE	#
#############

REQUIREMENTS:
- ffmpeg installed in PATH (I'm sorry)
- Windows operating system (for Japanese transcriptions only)
- NVIDIA GPU (also sorry for this)

HOW TO INSTALL:
1: Run "installer.bat". This will do a few things:
- Download and install all models + files needed for SOFA_GUI to function.
- Automatically set up the python environment for Whisper and SOFA.

2: Run "run.bat" to use the program!

3: Place all of your files in the "corpus" folder, in this format. There is no limit to how many speakers you can run at one time, but the more files you have, the longer it will take.

corpus
|	{name_of_speaker_1}
|	|	wav1.wav
|	|	wav2.wav
|	|	...
|	{name_of_speaker_2}
|	|	wav1.wav
|	|	wav2.wav
|	|	...

4: The transcription tab will run the Whisper transcriptions. The default whisper model is "medium", but if you have ~10GB VRAM available, you should change it to "large" in the settings! Otherwise, the difference is small.

5: Then, after running the transcription, you can go to the "Align" tab and run SOFA! If your transcriptions are in English, select "tgm_sofa". If your transcriptions are Japanese, select "colstone_jpn". Currently, these are the only two languages supported.

##############
#	EXTRAS	 #
##############

If you get this warning on the command line:

"You are using a CUDA device ('{your_gpu}') that has Tensor Cores. To properly utilize them, you should set `torch.set_float32_matmul_precision('medium' | 'high')` which will trade-off precision for performance. For more details, read https://pytorch.org/docs/stable/generated/torch.set_float32_matmul_precision.html#torch.set_float32_matmul_precision"

Then do this:

In the "SOFA" folder, open up 'infer.py' in a notebook, and remove the "#" from the line that says "torch.set_float32_matmul_precision('medium')". This will just make inferance run a bit faster.