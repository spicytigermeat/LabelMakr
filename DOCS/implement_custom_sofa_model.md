# How to implement your own SOFA Model.
Here is a guide on how to implement your own SOFA model into LabelMakr!

NOTE:
- Please use ISO lang codes for LabelMakr. For example, if you are training an English model, suffix it with "en". If the accent is a specific region or dialect, you can do this: "en_uk". This is done to keep the naming cohesive.
- The G2p is TOTALLY optional! It's only necessary for languages where you will be likely to find words outside of the dictionary provided. For example, english has a lot of strange compound words, so the G2p can guess that. If your language is consistent in terms of spelling/pronunciation, like Spanish, a G2p is probably not necessary.
- There's no simple guides out there for the G2p's, but it uses OpenUTAU's G2p models with modified training parameters.

## What you will need
- SOFA Model (renamed to model.ckpt)
- SOFA Dictionary (renamed to dict.txt)

So, the folder structure will look like this once you have it set. Let's assume your model is called "custom_sofa_en"
```
LabelMakr
|  assets
|  corpus
|  models
|  custom_sofa_en
|  |  dict.txt
|  |  model.ckpt
|  strings
labelmakr.py
...
```  

Optional:

### OpenUTAU G2p
- OpenUTAU G2p CHECKPOINT (usually called g2p-best.ptsd, renamed to model.ptsd)
- OpenUTAU G2p training config (called cfg.yaml)

Change the `_target_` in all 3 locations in cfg.yaml to this:
```
_target_: models.g2p_model.G2p
Decoder:
  _target_: models.g2p_model.Decoder
  ...
Encoder:
  _target_: models.g2p_model.Encoder
  ...
```

This is what your folder structure will look like when you have it set up with a G2p. Let's assume your model is called "custom_sofa_en".
You need to be sure that all of the g2p items are saved in a folder called "g2p". LabelMakr will automatically determine if your SOFA Model has a G2p available to use.
```
LabelMakr
|  assets
|  corpus
|  models
|  custom_sofa_en
|  |  g2p
|  |  |  cfg.yaml
|  |  |  model.ptsd
|  |  dict.txt
|  |  model.ckpt
|  strings
labelmakr.py
...
```  
