from fews.config import HyperParams, MembershipCsvFiles
from fews.engine import defuzzifier, temporal_engine
from fews.domain import ObservationMatrix 
from fews.domain import load_membership_functions  
from fews.engine.fuzzifier import fuzzifier
from fews.ingestion import parse_obs



def main():
    obs_matrix = None 
    mf_csvs = MembershipCsvFiles()
    membership_functions = load_membership_functions(mf_csvs)
    params = HyperParams()

    concern_values = []

    while True:
        print("Input vital signs in format [hr, sbp, rr, temp, spo2, fio2, patient_id]. \n press q to quit.")
        user_inputted_obs = input() 
        
        if user_inputted_obs.strip().lower() == "q":
            break

        obs_list = [item.strip() for item in user_inputted_obs.split(",")]

        obs_list = [float(val) for val in obs_list]
        
        p_id = obs_list.pop()

        obs = parse_obs(obs_list)

        if not obs_matrix:
            obs_matrix = ObservationMatrix.from_first_observation(patient_id = int(p_id), first_obs = obs)
        else:
            obs_matrix.add_observation(obs)

        if len(obs_matrix.obs) >= 3:
            concern_values.append(temporal_engine(obs_matrix, params, membership_functions))
            print(f"Concern Score [0,18] = {concern_values[-1]}")
        else:
            fuzzified = fuzzifier(obs, membership_functions)
            defuzzified = defuzzifier(fuzzified)
            concern_values.append(defuzzified)
            print(f"Concern Score [0, 18] = {defuzzified}")
            

if __name__ == "__main__":
    main()
