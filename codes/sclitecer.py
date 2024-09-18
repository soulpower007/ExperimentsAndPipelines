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
# hypothesis
hyp_dir_path = sys.argv[2]
def cleanit(txt):
    stk = []
    op = ""
    for x in txt:
        l = len(stk)
        if len(stk)==0 and x!='[' and x!=']' and x!='(' and x!=')' and x!='{' and x!='}':
            op+=x
            continue

        if x=='[':
            stk.append('[')
        if x==']' and l!=0 and stk[l-1]=='[':
            stk.pop()
        if x=='(':
            stk.append('(')
        if x==')' and l!=0 and stk[l-1]=='(':
            stk.pop()
        if x=='{':
            stk.append('{')
        if x=='}' and l!=0 and stk[l-1]=='{':
            stk.pop()
    return op

for filename in os.listdir(hyp_dir_path):
    if not filename.endswith('tsv'):
        print("continuing ", filename)
        continue
    # Specify the path to your TSV file
    tsv_file_path = os.path.join(hyp_dir_path, filename)
    csv_file_path = os.path.join(ref_dir_path, filename[:-3]+"csv")
    df_hyp = None
    df_ref = None
    # Read the TSV file using pandas
    df_hyp = pd.read_csv(tsv_file_path, sep='\t', header=None, skiprows=1)
    # with open(csv_file_path, encoding='euc-jp', errors='replace') as ref_file:
    #    df_ref = pd.read_csv(ref_file, header=None)
    df_ref = pd.read_csv(csv_file_path, header=None, skiprows=1)

    # Ensure that the DataFrame has at least four columns
    if df_hyp.shape[1] < 4:
        print("The hyp does not have enough columns.")
    elif df_ref.shape[1] < 4:
         print("The ref does not have enough columns.")
    else:
        #print(df_hyp)
        #print(df_ref)
        # Access the 4th column (index 3) and concatenate its contents
        start_j=0
        end_j=len(df_hyp)-1
        len1 = len(df_ref)
        len2 = len(df_hyp)
        #print(len1, len2)
        #print(start_j, end_j)
        #print(df_hyp.iloc[0], "||", df_ref.iloc[0])

        #print("Endpoints of REF: ", float(df_ref.iloc[0][0]) ,  float(df_ref.iloc[len1-1][1]))
        # eliminate the top part of hyp
        while float(df_hyp.iloc[start_j][0]) < float(df_ref.iloc[1][0]) :
            start_j+=1
        while float(df_hyp.iloc[end_j][1])> float(df_ref.iloc[len1-1][1]):
            end_j-=1
        start_j-=1
        end_j+=1
        print("HYP:")
        print(df_hyp.iloc[start_j:end_j, 0:2] )
        print("REF:______________________________")
        print(df_ref.iloc[:, 0:2] )
        concatenated_text_hyp = ' '.join(df_hyp.iloc[start_j:end_j, 3].astype(str))
        concatenated_text_ref = ' '.join(df_ref.iloc[:, 3].astype(str))

        concatenated_text_hyp = cleanit(concatenated_text_hyp)
        concatenated_text_ref = cleanit(concatenated_text_ref)

        concatenated_text_hyp = re.sub(r'[a-zA-Z0-9\[\]\(\)@。?\"「」%,.\/、 ]', '', concatenated_text_hyp)
        concatenated_text_ref = re.sub(r'[a-zA-Z0-9\[\]\(\)@。?\"「」%,.\/、 ]', '', concatenated_text_ref)
        with open("exp1.txt", 'w') as file:
            file.write(concatenated_text_hyp+"\n")

        with open("exp2.txt", 'w') as file:
            file.write(concatenated_text_ref+"\n")
        subprocess.run(['sclite', '-r', 'exp1.txt', 'trn', '-h' 'exp2.txt','trn' , '-c' 'NOASCII', ])

        print("File: ", filename[:-3])

        print("REF:\n", concatenated_text_ref[:], "\n____________________________next_____________________\n", "HYP:\n",concatenated_text_hyp[:])
        print(cer(concatenated_text_ref, concatenated_text_hyp ))
        break
