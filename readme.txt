 _       _          _                 _         
| |     | |        | |               | |        
| | __ _| |__   ___| |_ __ ___   __ _| | ___ __ 
| |/ _` | '_ \ / _ \ | '_ ` _ \ / _` | |/ / '__|
| | (_| | |_) |  __/ | | | | | | (_| |   <| |   
|_|\__,_|_.__/ \___|_|_| |_| |_|\__,_|_|\_\_|   
                                                
##############
#	CREDIT	 #
##############

SOFA developed by suco/qiuqiao
Whisper created by OpenAI

tgm_sofa English SOFA Model created by tigermeat
colstone_jpn Japanese SOFA Model created by colstone
mandarin_suco Mandarin Singing SOFA Model created by SOFA Developer suco/qiuqiao

GUI Translations:
Japanese: tigermeat
Chinese: ArchiVoice
Indonesian: Koji
Russian: m

##########################
#	 CURRENT FEATURES	 #
##########################

Transcribe & Force-Align English, Japanese, Mandarin Chinese and Russian.

Transcribe any languages supported by Whisper
(manually type in the 2 digit language code in the language drop down.)

Utilize the built in transcription editor to fix your transcriptions.

#############
#	USAGE	#
#############

REQUIREMENTS:
- Windows operating system (for Japanese transcriptions only)
- NVIDIA GPU (you can try CPU inference, but it probably won't work well.)

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

5: Then, after running the transcription, you can go to the "Align" tab and run SOFA! If your transcriptions are in English, select "tgm_sofa". If your transcriptions are Japanese, select "colstone_jpn". If your transcriptions are in Mandarin Chinese, select "mandarin_suco".

##############
#	EXTRAS	 #
##############

If you get this warning on the command line:

"You are using a CUDA device ('{your_gpu}') that has Tensor Cores. To properly utilize them, you should set `torch.set_float32_matmul_precision('medium' | 'high')` which will trade-off precision for performance. For more details, read https://pytorch.org/docs/stable/generated/torch.set_float32_matmul_precision.html#torch.set_float32_matmul_precision"

Then please enable "Use Tensorcores" in the settings menu! This will fully utilize your GPU, speeding up forced-alignments!