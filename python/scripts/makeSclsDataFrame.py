import ast
import argparse
import os

from validation.sclsDataProcessing import *

parser = argparse.ArgumentParser()

parser.add_argument(
    "--input", "-i", default="/grid_mnt/data_cms_upgrade/biriukov/data/singleElectrons_D110/step3/15_1_0_pre2/dumper",
    help="import folder of file to process"
)

parser.add_argument(
    "--output", "-o", default="/grid_mnt/data_cms_upgrade/biriukov/TICL_Validation/scls_csv_files",
    help="Directory to save output csv file"
)

parser.add_argument(
    "--scores", "-s", default="best_associated",
    help = "What scores to use. There must be eiter best_associated, best_shared_e or no (if no association required)"
)

parser.add_argument(
    "--n-files", "-nf", default=-1,
    help="Maximal number of files to process. Set (-1) if processing of all files is required"
)

args = parser.parse_args()

if args.input[0] == "[":
    args.input = ast.literal_eval(args.input)

isList = True
if type(args.input) != list:
    isList = False
    args.input = [args.input]

isFile = False
files = []
for path in args.input:
    if not os.path.exists(path):
        raise Exception(f"Path {path} does not exist!")

    if os.path.isdir(path):
        files_per_path = [entry.name for entry in os.scandir(path) if entry.is_file()]
    else:
        isFile = True
        files_per_path = [path]
    files.append(files_per_path)

df_total = pd.DataFrame({})

scores_func = {'best_associated': bestS2RScore,
               'best_shared_e': bestS2RSharedE,
               'associated': associatedS2R,
               'no': ''}[args.scores]

i = 0
for files_per_path, path in zip(files, args.input):
    for file in files_per_path:
        if (int(args.n_files) != (-1)) and (int(args.n_files) <= i):
            print(f"The number of process files is reached {args.n_files}")
            break

        if isList or not isFile:
            filepath = f'{path}/{file}'
        else:
            filepath = file

        root_file = ur.open(filepath)
        df = pd.DataFrame()
        
        if args.scores != 'no':
            reco_id = scores_func(df, root_file)

        if (args.scores == 'best_associated') or (args.scores == 'best_shared_e'):
            func_args = [df, root_file, reco_id[0]]
            fillEventNumber(*func_args)
            fillNSclsPerCP(*func_args)
            fillNTrPerScls(*func_args)
            fillSclsRecoArrays(*func_args)
            fillSclsSimArrays(*func_args)
            fillR2S(*func_args)
            computeBaryResponse(df)
            computeResponse(df)
        
        if (args.scores == 'no'):
            fillEventNumber(df, root_file, None)
            fillNSclsPerEvent(df, root_file)
            fillSclsRecoArrays(df, root_file, scores=None)

        # Doesn't work, to be fixed soon
        if (args.scores == 'associated'):
            func_args = [df, root_file, reco_id]
            fillEventNumber(*func_args)
            fillNSclsPerCP(*func_args)
            fillNTrPerScls(*func_args)
            fillSclsRecoArrays(*func_args)
            fillSclsSimArrays(*func_args)
            fillR2S(*func_args)
            computeBaryResponse(df)
            computeResponse(df)

        df['file'] = i
        i += 1

        df_total = pd.concat([df_total, df], ignore_index=True)
        print(f"\rFile {file} is finished", sep=" ", flush=True)

if (not os.path.exists(args.output)) and (len(args.output.split('/')[-1].split('.')) == 1):
    os.mkdir(args.output)

if os.path.isdir(args.output):
    df_total.to_csv(f'{args.output}/csv_from_dumper.csv', index=False)
else:
    df_total.to_csv(args.output, index=False)



