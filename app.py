import uuid
import os
import argparse
from transcribeUtils import *
from srtUtils import *
import time
from videoUtils import *
from audioUtils import *
from flask import Flask, make_response, jsonify, request,send_file
import json

import urllib.request

app = Flask(__name__)


@app.route('/', methods = ["POST","GET"])
def predict():
    # data = request.get_json()
    # args['outlang'] = data['lang']

    args = dict()
    args['region']='us-east-2'
    args['inbucket']='cc-project-buck/'
    args['infile']='ellen.mp4'
    args['outbucket']='cc-project-buck/'
    args['outfilename']='subtitledVideo'
    args['outfiletype']='mp4'
    args['outlang']=['es']



    # print out parameters and key header information for the user
    print( "==> translatevideo.py:\n")
    print( "==> Parameters: ")
    print("\tInput bucket/object: " + args['inbucket'] + args['infile'] )
    print( "\tOutput bucket/object: " + args['outbucket'] + args['outfilename'] + "." + args['outfiletype'] )

    print( "\n==> Target Language Translation Output: " )

    for lang in args['outlang']:
        print( "\t" + args['outbucket'] + args['outfilename'] + "-" + lang + "." + args['outfiletype'])
        
        
    # Create Transcription Job
    response = createTranscribeJob( args['region'], args['inbucket'], args['infile'] )

    # loop until the job successfully completes
    print( "\n==> Transcription Job: " + response["TranscriptionJob"]["TranscriptionJobName"] + "\n\tIn Progress"),

    while( response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
        print( "."),
        time.sleep( 30 )
        response = getTranscriptionJobStatus( response["TranscriptionJob"]["TranscriptionJobName"] )

    print( "\nJob Complete")
    print( "\tStart Time: " + str(response["TranscriptionJob"]["CreationTime"]) )
    print( "\tEnd Time: "  + str(response["TranscriptionJob"]["CompletionTime"]) )
    print( "\tTranscript URI: " + str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) )

    # Now get the transcript JSON from AWS Transcribe
    transcript = getTranscript( str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) ) 
    print( "\n==> Transcript: \n" + transcript)

    # Create the SRT File for the original transcript and write it out.  
    writeTranscriptToSRT( transcript, 'en', "subtitles-en.srt" )  
    # createVideo( args['infile'], "subtitles-en.srt", args['outfilename'] + "-en." + args['outfiletype'], "audio-en.mp3", True)


    # # Now write out the translation to the transcript for each of the target languages
    for lang in args['outlang']:
        writeTranslationToSRT(transcript, 'en', lang, "subtitles-" + lang + ".srt", args['region'] ) 	
        
        # Now that we have the subtitle files, let's create the audio track
        createAudioTrackFromTranslation( args['region'], transcript, 'en', lang, "audio-" + lang + ".mp3" )
        
        # Finally, create the composited video
        createVideo2( args['infile'], "subtitles-" + lang + ".srt", args['outfilename'] + "-" + lang + "." + args['outfiletype'], "audio-" + lang + ".mp3", False)

    

    # response = make_response(
    #             jsonify(
    #                 data
    #             ),
    #             200,
    #         )
    # response.headers["Content-Type"] = "application/json"
    # os.remove(file_path
    # print("file deleted")

    # return "Completed"
        command ='ffmpeg -i '+args['outfilename']+'-'+lang+'.mp4 -i subtitles-'+lang+'.srt -c copy -c:s mov_text finalTranslatedVideo.mp4'
        os.system(command)
    return "Done"
    # return send_file('C:/Users/Admin/Desktop/CC/ellen.mp4')

if __name__=='__main__':
    app.run(debug=True,port=5000)