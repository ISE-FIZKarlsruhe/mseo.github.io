import pandas as pd

df_all = pd.read_csv("output1_mse.csv")
df_all['OWL2 profile information'] = ""

metrics = { "expressivity_incl": 'Semantic expressivity',
            "rdfs": 'Does the ontology correspond to the RDFS profile?',
            "constructs": 'Logical constructs used',
            #"owl2dl_profile_violation": 'Counts of OWL2 DL profile violations',
            "rule_count": 'Number of SWRL rules used',
            "syntax": 'What serialisation is used for the ontology?',
            "tautology_count": 'Number of tautological axioms',
            "certain_cycle": 'If true, there is a definite cycle in the ontology. If false, cyclicity is unknown (experimental)',
            #"namespace_axiom_count": 'Number of axioms using at least one term in a namespace',
            #"namespace_entity_count": 'Number of distinct entities used from a namespace',
            "logical_axiom_count": 'Number of logical axioms in ontology',
            "most_freq_concept": 'Most frequently used class',
            }

for metric, metric_description in metrics.items():
    df_all[metric_description] = ""

for index, row in df_all.iterrows():
    namespace = df_all['namespace'][index]
    filename = 'all_files/' + namespace + '.csv'
    try:
        df = pd.read_csv(filename)
    except:
        print(filename)
        continue
    for profile in ["owl2", "owl2_dl", "owl2_el", "owl2_ql", "owl2_rl"]:
        if df[df.metric == profile].metric_value.values[0] == 'true':
            try:
                df_all.at[index, 'OWL2 profile information'] = profile
            except:
                df_all.at[index, 'OWL2 profile information'] = 'Error'
    try:
        df_all.at[index, 'Counts of OWL2 DL profile violations'] = df[df.metric == "owl2dl_profile_violation"].metric_value.values
    except:
        df_all.at[index, 'Counts of OWL2 DL profile violations'] = ''
    try:
        df_all.at[index, 'Number of axioms using at least one term in a namespace'] = df[df.metric == "namespace_axiom_count"].metric_value.values
    except:
        df_all.at[index, 'Number of axioms using at least one term in a namespace'] = ''
    try:
        df_all.at[index, 'namespace_entity_count'] = df[df.metric == "namespace_entity_count"].metric_value.values
    except:
        df_all.at[index, 'namespace_entity_count'] = ''

    for metric, metric_description in metrics.items():
        try:
            df_all.at[index, metric_description] = df[df.metric == metric].metric_value.values[0]
        except:
            df_all.at[index, metric_description] = 'Error'

df_all.to_csv("output2_mse.csv")

#docker run -v C:/Users/eno/Documents/Git_repo/ISE-FIZKarlsruhe_github/mseo.github.io/all_files:/work --rm -ti obolibrary/robot robot measure --input /work/bmo.ttl --output /work/bmo.csv
