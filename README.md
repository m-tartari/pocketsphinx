# pocketsphinx

A python wrapper for speech-to-text application using Pocketsphinx. It publishes strings of detected commands, has a custom master-phrase for commands and can handle an emergency stop command.

The following repositories were used in our wrapper, but are not required for installation:

- [ros_voice_control](https://github.com/gorinars/ros_voice_control)

- [helperScripts](https://github.com/malceore/helperScripts)

## Installation

1. You will need to have pip preinstalled for this to work:

```
sudo apt-get install portaudio19-dev swig libpulse-dev
sudo -H pip install PyAudio pocketsphinx
```

2. Download and copy the selected language model to /usr/share/pocketsphinx/model/hmm/en_US/. It can be found [here](https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/)

3. Download this package using:

```
git clone https://github.com/m-tartari/pocketsphinx.git
```

## Use

A launch file pocketsphinx.launch has been included to launche the node and can be run using:

```
rosrun pocketsphinx pocketsphinx.launch
```

A sencond launch file has been included to show all available paramenter for the recognizer node.

The required files (that represent the language model) can be generated using a .txt file and the [Sphinx Knowledge Base Tool](http://www.speech.cs.cmu.edu/tools/lmtool-new.html). An example is visible in the lang_models directory

### Utilites

The script lm_test.py can be used to check the correct functioning of the language model. It can be run using:

```
roscd pocketsphinx
python run ./scripts/lm_test.py
```
