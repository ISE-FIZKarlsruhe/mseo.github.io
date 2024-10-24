import xml.etree.ElementTree as ET
import pandas as pd
import pickle

# Load the dictionary from the file
with open("dic_external.pkl", "rb") as f:
    dic_external = pickle.load(f)

def extract_metric(tree_element):
    metric_family = tree_element.tag
    #print(metric_family)
    for child in tree_element:
        #print("---- ", child)
        metric_document = {}
        metric_document["metric_family"] =  metric_family
        metric_document["metric_name"] = child.tag
        metric_document["value"] = child.text 
        #print(metric_document)
        yield metric_document

def load_metrics(filename: str, ontology_name: str) -> pd.DataFrame:
    tree = ET.parse(filename)
    root = tree.getroot()
    metrics = []
    for child in root[0]:
        if child.tag == "Classmetrics": ## we don't handle class metrics
            continue
        for metric_document in extract_metric(child):
            metrics.append(metric_document)
    df = pd.DataFrame(metrics).rename(columns={"metric_name": "metric_code", "value": ontology_name})
    return df

def add_metrics(df_metrics: pd.DataFrame, df_new_metrics: pd.DataFrame) -> pd.DataFrame:
    selected_columns = list(set(df_new_metrics.columns) -  set(['metric_family']))
    df_new_table = df_metrics.merge(df_new_metrics[selected_columns],how='left', on= "metric_code")
    return df_new_table

df_all = pd.read_csv("output.csv")
df_metrics_table = pd.read_excel("metrics_labels.xlsx")
df_metrics_table = df_metrics_table[["metric_name","metric_code","ontometrics_name","evaluation_criteria"]]
evaluated_ontologies = []

for index, row in df_all.iterrows():
    try:
        url = df_all['mirror_from'][index]
        filename = 'all_files/' + df_all['namespace'][index] + '.' + df_all['mirror_from'][index][-3:]
        print(filename)
        df_ = load_metrics('all_files/' + df_all['namespace'][index] + '.xml', df_all['namespace'][index])

        df_metrics_table = add_metrics(df_metrics_table, df_)
        evaluated_ontologies.append(df_all['namespace'][index]) 
    except:# KeyError as e:
        print(url)
        continue

df_metrics_table.drop(["metric_code"], axis=1, inplace=True)

df_metrics_table.transpose().to_excel("validation_metrics_table.xls")#, index=False)


from functools import partial
def use_f_2(x, num_decimals):
    try:
        n = int(str(x))
        return n
    except ValueError:
        try:
            n = float(str(x))
            return f"%.{num_decimals}f" % float(x)
        except Exception as e:
            return x

# the number of columns can be passed to this function
use_f = lambda x: partial(use_f_2, num_decimals=x)
df_base_metrics = df_metrics_table[0:7][['metric_name'] + evaluated_ontologies]
df_base_metrics.rename(columns={'metric_name':'metric name'}, inplace=True)
caption = "Base metrics."
label="tab:base-metrics"
with pd.option_context("max_colwidth", 1000, "display.precision", 3):
    df_base_metrics.transpose().to_latex("base_metrics.tex",  multicolumn=True, header=True,# index_names=False, index=False, 
                                         column_format='m{3.5cm}'+'m{1cm}'*7, caption=caption, label=label)


df_schema_and_graph_metrics = df_metrics_table[7:][['metric_name','evaluation_criteria'] + evaluated_ontologies]
df_schema_and_graph_metrics.rename(columns={'metric_name':'metric name', 'evaluation_criteria': 'evaluation criteria'}, inplace=True)



#### Add number of external class metric
### Number of external classes is evalutated using Protegé 
description = """The interpretation of NoC values depends on the number of classes in the ontology. For
example, if NoC is near the total number of internal classes a large fraction of the ontology depends on concepts defined in other places.
Thus the change in the external ontologies can influence the intended semantics to a great extent.
We report (i) the absolute NoC values and (ii) the ratios between NoC and the # of classes among parenthesis"""
dic_external['metric name'] = 'NoC'
dic_external['evaluation criteria'] = description
new_row_s = pd.DataFrame(dic_external, index=[0])

df_schema_and_graph_metrics = pd.concat([df_schema_and_graph_metrics.loc[7:12],new_row_s,df_schema_and_graph_metrics.loc[13:17]]).reset_index(drop=True)


### update NoR and NoL metrics with relative values inside parenthesis
num_classes = [ int(v) for v in df_base_metrics.iloc[2:3, 1:].values.flatten().tolist()]
nor = [int(v) if not pd.isna(v) else 0 for v in df_schema_and_graph_metrics.iloc[7:8, 2:].values.flatten().tolist()]
nol = [int(v) if not pd.isna(v) else 0 for v in df_schema_and_graph_metrics.iloc[8:9,2:].values.flatten().tolist() if v!=None]
noc = [int(v) if not pd.isna(v) else 0 for v in df_schema_and_graph_metrics.iloc[6:7,2:].values.flatten().tolist() if v!=None]
print(new_row_s)
#print(df_base_metrics.iloc[2:3, 1:].values.flatten().tolist())
for i,v in enumerate(num_classes):
    if int(num_classes[i]) != 0:
        new_nor = "%s (%1.2f)" % (nor[i],int(nor[i])/int(num_classes[i]))
        df_schema_and_graph_metrics.iloc[5:6,2+i:3+i] = new_nor
        new_nol = "%s (%1.2f)" % (nol[i],int(nol[i])/int(num_classes[i]))
        df_schema_and_graph_metrics.iloc[7:8,2+i:3+i] = new_nol
        new_noc = "%s (%1.2f)" % (noc[i],int(noc[i])/int(num_classes[i]))
        df_schema_and_graph_metrics.iloc[6:7,2+i:3+i] = new_noc
    else:
        new_nor = "%s (-)" % (nor[i],)
        df_schema_and_graph_metrics.iloc[5:6,2+i:3+i] = new_nor
        new_nol = "%s (-)" % (nol[i],)
        df_schema_and_graph_metrics.iloc[7:8,2+i:3+i] = new_nol
        new_noc = "%s (-)" % (noc[i],)
        df_schema_and_graph_metrics.iloc[6:7,2+i:3+i] = new_noc


new_row_s = pd.DataFrame(dic_external, index=[0])
pd.concat([df_schema_and_graph_metrics.loc[7:12],new_row_s,df_schema_and_graph_metrics.loc[13:17]]).reset_index(drop=True)


df_schema_and_graph_metrics_no_description = df_schema_and_graph_metrics[["metric name"] + evaluated_ontologies]
caption = "Topology metrics."
label="tab:topology-metrics"
#df_schema_and_graph_metrics_no_description = df_schema_and_graph_metrics_no_description[df_schema_and_graph_metrics_no_description['metric name'].isin(["NoR","NoC","NoL","ADIT-LN"])]
with pd.option_context("max_colwidth", 1000):
    df_schema_and_graph_metrics_no_description.transpose().applymap(lambda x: "%1.2f" % (float(x)) if isinstance(x, (str)) and '.' in x and not ' ' in x else x).to_latex("schema_and_graph_metrics.tex",  
        multicolumn=True, header=True,# index_names=False, index=False,
        column_format='m{3.5cm}'+'m{2cm}'*12, 
        caption=caption, label=label,
        #formatters=[None, use_f(3)]#, use_f(3), use_f(3)]
        )

df_metrics_table.drop(["metric_name"], axis=1, inplace=True)
df_metrics_table.drop(["evaluation_criteria"], axis=1, inplace=True)
df_metrics_table = df_metrics_table[df_metrics_table['ontometrics_name'].isin(["Absolute root cardinality", "Absolute leaf cardinality", "Absolute depth", "Average depth", "Maximal depth", "Absolute breadth", "Average breadth", "Maximal breadth", "Tangledness"])]
df_metrics_table.transpose().applymap(lambda x: "%1.2f" % (float(x)) if isinstance(x, (str)) and '.' in x and not ' ' in x else x).to_latex("validation_metrics_table.tex")#, index=False)

df_general_table = pd.read_csv("general_table.csv")

empty_df = pd.DataFrame()

# Define the list of dataframes to add
for ontology in df_metrics_table.transpose().index:
    if ontology in list(df_general_table["Short Name"]):
        
        empty_df = empty_df.append(df_general_table[df_general_table["Short Name"]==ontology], ignore_index=True)
    else:
        print(ontology)

with pd.option_context("max_colwidth", 1000):
    empty_df.to_latex("general.tex",
                  column_format='m{5cm}m{2cm}m{5cm}m{2cm}m{2cm}m{2cm}m{2cm}m{2cm}m{2cm}',
                  index=False, escape=False)

# Load the dictionary from the file
with open("dic_pitfalls.pkl", "rb") as f:
    dic_pitfalls = pickle.load(f)

empty_df = pd.DataFrame(columns=["Ontology Name", "Critical", "Important", "Minor" ])
for ontology in df_metrics_table.transpose().index:
    if ontology in list(df_general_table["Short Name"]):
        try:
            critical = dic_pitfalls[ontology]['Critical']
            important = dic_pitfalls[ontology]['Important']
            minor = dic_pitfalls[ontology]['Minor']
            empty_df = empty_df.append({'Ontology Name': ontology,
                                        'Critical': '-' if not critical else ', '.join([f"{item[0]}: {item[1]}" for item in critical]),
                                        'Important': '-' if not important else ', '.join([f"{item[0]}: {item[1]}" for item in important]),
                                        'Minor': '-' if not minor else ', '.join([f"{item[0]}: {item[1]}" for item in minor])}, ignore_index=True)
        except:
            empty_df = empty_df.append({'Ontology Name': ontology,
                                        'Critical': '-' ,
                                        'Important': '-',
                                        'Minor': '-' }, ignore_index=True)

with pd.option_context("max_colwidth", 1000):
    empty_df.to_latex("pitfalls.tex",
                  column_format='m{4cm}m{3cm}m{3cm}m{5cm}',
                  index=False, escape=False)