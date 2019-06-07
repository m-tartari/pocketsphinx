#!/usr/bin/env python
import rospy
from std_msgs.msg import String, Header

import pyaudio
from os import environ, path
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *



class recognizer(object):
      def __init__(self):
            # Start node and publisher
            rospy.init_node("recognizer")
            rospy.on_shutdown(self.shutdown)
            self.pub_ = rospy.Publisher('~output', Header, queue_size=1)

            # Load Pocketsphinx parameters
            if rospy.has_param('~stopword'):
                self.STOPWORD = rospy.get_param('~stopword')
            else:
                self.STOPWORD = "STOP"
                rospy.loginfo("Loading the default stopword "+self.STOPWORD)

            if rospy.has_param('~hotword'):
                self.HOTWORD = rospy.get_param('~hotword')
            else:
                self.HOTWORD = "ASSISTANT"
                rospy.loginfo("Loaded the default hotword "+self.HOTWORD)

            if rospy.has_param('~model_dir'):
                self.MODELDIR = rospy.get_param('~model_dir')
            else:
                rospy.loginfo("Loading the acoutic model from default directory")
                self.MODELDIR = "/usr/local/lib/python2.7/dist-packages/pocketsphinx/model/en-us/en-us"
                rospy.loginfo("Done loaded the default acoustic model")
            
            if rospy.has_param('~data_dir'):
                self.MODELDIR = rospy.get_param('~data_dir')
            else:
                rospy.loginfo("Loading the acoustic data from the default data folder")
                self.DATADIR = "/usr/local/lib/python2.7/dist-packages/pocketsphinx/data/"
                rospy.loginfo("Done loaded the default acoustic data")

            # Load microphone stream config.
            if rospy.has_param('~chunk'):                          # CHUNKS of bytes to read each time from mic
                self.CHUNK = rospy.get_param('~chunk')
            else:
                self.CHUNK = 1024
                rospy.loginfo("Loaded the default chunk size")

            if rospy.has_param('~format'):
                self.FORMAT = rospy.get_param('~format')
            else:
                self.FORMAT = pyaudio.paInt16
                rospy.loginfo("Loaded the default stream format")

            if rospy.has_param('~channel'):
                self.CHANNELS = rospy.get_param('~channel')
            else:
                self.CHANNELS = 1
                rospy.loginfo("Loaded the default channel")

            if rospy.has_param('~rate'):
                self.RATE = rospy.get_param('~rate')
            else:
                self.RATE = 16000
                rospy.loginfo("Loaded the default rate")
            
            # Load dictionary
            if rospy.has_param('~dictionary'):
                self.LEXICON = rospy.get_param('~dictionary')
                rospy.loginfo("Loaded "+self.LEXICON)
            else:
                rospy.logerr('No dictionary found. Please add an appropriate dictionary argument.')
                return  

            if rospy.has_param('~lm'):
                self.LM = rospy.get_param('~lm')
                rospy.loginfo("Loaded "+self.LM)
            else:
                rospy.logerr('No LM file defined. Please add an appropriate parameter.')
                return
            if rospy.has_param('~command_list'):
                self.CMD = rospy.get_param('~command_list')
                rospy.loginfo("Loaded "+self.CMD)
            else:
                rospy.logerr('No command list defined file defined. Please add an appropriate parameter.')
                return

            # Decoder setup
            config = Decoder.default_config()
            config.set_string('-hmm',self.MODELDIR)
            config.set_string('-lm', self.LM)
            config.set_string('-dict', self.LEXICON)	
            config.set_string('-logfn', '/dev/null')
            self.decoder = Decoder(config)

            #load list of commands and remove \n at the end of each entry
            logfile = open(self.CMD, 'r')
            self.command_list = logfile.readlines()
            logfile.close()
            rospy.loginfo("command list:")
            for n in range(len(self.command_list)): 
                rospy.loginfo(self.command_list[n])
                self.command_list[n]=self.command_list[n].strip()

            self.listen_for_speech()


      def listen_for_speech(self):
            #
            # Main Looping function, continually listens for sound and parses out string commands.
            #
            p = pyaudio.PyAudio()
            # Input
            stream = p.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK)

            rospy.loginfo(">>Listening..")
            

            # MAIN LOOP
            in_speech_bf = False
            self.decoder.start_utt()
            while not rospy.is_shutdown():
                buf = stream.read(1024)
                if buf:
                    self.decoder.process_raw(buf, False, False)
                    if self.decoder.get_in_speech() != in_speech_bf:
                        in_speech_bf = self.decoder.get_in_speech()
                        if not in_speech_bf:
                            self.decoder.end_utt()
                            word=self.decoder.hyp().hypstr
                            rospy.loginfo( 'Result:'+ word)

                            # if contains stopword publish it immediately
                            if (word.find(self.STOPWORD)!=-1):
                                rospy.loginfo( "found stopword")
                                self.publish(self.STOPWORD)

                            # else look for hotword
                            elif word.startswith(self.HOTWORD):
                                    #remove hotword from command
                                    word=word[(len(self.HOTWORD)+1):]
                                    rospy.loginfo( 'Stripped:'+ word)
                                    
                                    #check if command is in the list
                                    if word in self.command_list: 
                                              rospy.loginfo( "Found it")
                                              self.publish(word) #TODO: checkif  it works
                            rospy.loginfo("Read to receive comnnad")
                            self.decoder.start_utt()
                else:
                    break
            self.decoder.end_utt()


      def publish(self,string):
        voice_cmd=Header()
        voice_cmd.frame_id=string
        voice_cmd.stamp=rospy.Time.now()
        self.pub_.publish(voice_cmd)

      def shutdown(self):
            #
            #command executed after Ctrl+C is pressed
            #
            rospy.loginfo("Stopping PocketSphinx")

if(__name__ == '__main__'):
    start = recognizer()
