import csv
import re
import sys
import os
from pathlib import Path
import pandas as pd
from jiwer import cer
import subprocess

# reference
ref_dir_path = sys.argv[1]
# segments audio store
seg_dir_path = sys.argv[2]
# input audio
audio_dir_path = sys.argv[3]

for filename in os.listdir(ref_dir_path):
    if not filename.endswith('csv') or not filename.endswith('ja_1057.csv'):
        # print("continuing ", filename)
        continue
    # Specify the path to your TSV file
    csv_file_path = os.path.join(ref_dir_path, filename[:-3]+"csv")
    df_ref = None

    df_ref = pd.read_csv(csv_file_path, header=None, skiprows=1)

    if df_ref.shape[1] < 4:
         print("The ref does not have enough columns.")
    else:
        os.mkdir( os.path.join(seg_dir_path, filename[:-4]) )
        for i in range(len(df_ref)):
            #subprocess.run(["ls", "-l"])
            strt = float(df_ref.iloc[i][0])
            diff = float(df_ref.iloc[i][1]) - strt
            try:
                channel = ord(str(df_ref.iloc[i][2][0])) - ord('A')
            except:
                print(print(df_ref.iloc[i]))
            output = os.path.join(seg_dir_path,filename[:-4] , filename[:-4]+df_ref.iloc[i][2]+str(i) +".wav" )
            input = os.path.join(audio_dir_path, filename[:-4], filename[:-4]+"raw"+".sph")
            outputtrans = os.path.join(seg_dir_path, filename[:-4], filename[:-4]+"_"+df_ref.iloc[i][2]+"_"+str(i) +".txt" )
            # creating the text ref files
            file = open(outputtrans, 'w')
            file.write(str(df_ref.iloc[i][0]) + "_" + str(df_ref.iloc[i][1]) +"___"+df_ref.iloc[i][3])
            file.close()

            print(input)
            print(filename)
            print(audio_dir_path,filename[:-4]+"raw"+".sph" )
            #print([ "ffmpeg", "-i", input, "-ss", str(strt), "-t" , str(diff), "-map_channel", "0.0."+str(channel), output  ])
            subprocess.run([ "ffmpeg", "-i", input, "-ss", str(strt), "-t" , str(diff), "-map_channel", "0.0."+str(channel), output  ])
            
    break
