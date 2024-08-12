import pandas as pd
import subprocess
import urllib.request
import os.path

def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

df_all = pd.read_csv("output.csv")

onts = []
onts_robot = []

for index, row in df_all.iterrows():
    ont_list = [nspace.lower().strip() for nspace in df_all['namespace'][index].split(',')]
    onts_robot.extend(ont_list)

for ont in onts:
    if ont not in onts_robot:
        print(ont)
        

for index, row in df_all.iterrows():
    url = df_all['mirror_from'][index]
    namespace = df_all['namespace'][index]
    try:
        filename = df_all['namespace'][index] + '.' + df_all['mirror_from'][index][-3:]
        print(filename)
        if not os.path.isfile('all_files/' +  filename):
            urllib.request.urlretrieve(url, 'all_files/' +  filename)

        command = f"docker run -v C:/Users/eno/Documents/Git_repo/ISE-FIZKarlsruhe_github/mseo.github.io/all_files:/work --rm -ti obolibrary/robot robot measure --input /work/{filename} --metrics all --output /work/{namespace}.csv"


        if not os.path.isfile('all_files/' +  namespace + '.csv'):
            hello_info = run(command)
            if hello_info.returncode != 0:
                print("An error occured: %s", hello_info.stderr)
                print("The error is for ", namespace)
            else:
                print("Hello command executed successfully!")
            
        else:
            print(df_all['namespace'][index], index)
            df_all.drop(index, inplace=True)
    except:
        print('failed',url)

df_all.to_csv("output_robot.csv")