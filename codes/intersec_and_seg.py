import csv
import sys
import os
from pathlib import Path

def main():

    if len(sys.argv) < 5:
        print("Usage: python script.py <ref> <hyp> <out_ref> <out_hyp>")
        sys.exit(1)

directory_path1 = sys.argv[1]
directory_out_path1 = sys.argv[2]
directory_path = Path(directory_path1)

directory_path22 = sys.argv[3]
directory_path2 = Path(directory_path22)
directory_out_path2 = sys.argv[4]
import re
print("Directory given: ", directory_path1)
bad_chars = [';', ':', '!', "*",".", ",","{","}", "[", "]","(",")" ]
for filename in os.listdir(directory_path1):
    if not filename.endswith('.csv'):
        continue
    print("filename: ", filename)
    ref_col = 3
    hyp_col = 3

    # List to store the extracted data
    extracted_data1 = [] # ref will have more per row
    extracted_data2 = []

    # used for output file naming
    # filename = os.path.basename(directory_path)
    used = dict()
    # Open the TSV file and extract the data
    with open(directory_path1+filename, 'r', newline='', encoding='utf-8') as file1, \
        open(directory_path22+filename[:-4]+".tsv", 'r', newline='', encoding='utf-8') as file2:
    
        # reader1 = csv.DictReader(file1, delimiter='\t')
        # reader2 = csv.DictReader(file2, delimiter='\t')

        list1 = list(csv.reader(file1))
        list2 = list(csv.reader(file2, delimiter='\t'))
        print(list2)
        len1 = len(list1)
        len2 = len(list2)
        j = 1
        curr = ""
        end = 0
        # i: ref_col
        # j: hyp_col
        # i want to match hyp column and ref columns i.e want to simply skip the hyp columns wrt ref columns
        




        # for all the ref transcripts
        print("Reference:", list1[0])
        print("HYP:", list2[0])
        for i in range(1,len1):
            curr = ""
            # print(i,j, list1[i][2] , list2[j][1], type(list1[i][2]) )
            # while the end time of hyp is less than that of ref, we are appending refs into a variable
            while j < len2 and  ( float(list2[j][1]) < float(list1[i][1]) or ( float(list2[j][1])-float(list1[i][1]) ) <0.5 ):
                end = list1[i][1]
                # if the end time of hyp is less than the start time of ref we can skip
                
                if (list2[j][1] < list1[i][0]):
                    j+=1
                    continue
                curr += list2[j][hyp_col] + " "
                j+=1
            if end not in used.keys():
                text = list1[i][ref_col]
                #text = re.sub(r'\{[^{}]*\}', '', list1[i][ref_col] )
                #text = re.sub('[^a-zA-Z0-9 ]', '', text)
                extracted_data1.append( text + " ("+ str(end) +") \n")
                text = curr
                #text = re.sub(r'\{[^{}]*\}', '',curr )
                #text = re.sub('[^a-zA-Z0-9 ]', '', text)
                extracted_data2.append(text + " ("+ str(end) +") \n")

                used[end]=1

    # Write the data to a text file as a single line
    with open( directory_out_path1 + filename[:-4] + '_sctk.txt', 'w', encoding='utf-8') as out_file:
        extracted_data_str =  ' '.join( extracted_data1 )
        # extracted_data_str = re.sub('{.*}' ,'', extracted_data_str )
        out_file.write(extracted_data_str)

    with open( directory_out_path2 + filename[:-4] + '_sctk.txt', 'w', encoding='utf-8') as out_file2:
        extracted_data2_str = ' '.join( extracted_data2)
        # extracted_data2_str = re.sub('{.*}' ,'', extracted_data2_str )
        out_file2.write( extracted_data2_str)

    # print(extracted_data1)
    # print("\n\n\n")
    # print(extracted_data2)
    print("Dir1: ", directory_out_path1)
    print("Dir2: ", directory_out_path2)
    print("Data has been written to" + filename[:-4] + "_sctk.txt")

if __name__ == "__main__":
    main()

