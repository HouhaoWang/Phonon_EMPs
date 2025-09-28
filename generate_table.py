import pickle
import re

# --- Load persistent data structures ----
with open("Materials.pkl", "rb") as file:
    Material_list = pickle.load(file)

with open("HSL.pkl", "rb") as file:
    HSL_list = pickle.load(file)

with open("HSL(latex).pkl", "rb") as file:
    HSL_latex_list = pickle.load(file)


with open("EMP.pkl", "rb") as file:
    EMP_list = pickle.load(file)

with open("Results.pkl", "rb") as file:
    Results_list = pickle.load(file)


def get_SG_material_infomation(SG):
    """
    Retrieve material information for a given space-group number.
    Parameters
    ----------
    SG : int
        Space-group number to filter materials.

    Returns
    -------
    tuple of three lists
        (SG_MPID_list, SG_Formula_list, SG_mp_list)
            SG_MPID_list   : list of Material Project identification number for materials whose SG matches.
            SG_Formula_list: list of Chemical Formulas.
            SG_mp_list     : list of mp tags in the public phonon database at Kyoto University.
    """
    SG_MPID_list    = []
    SG_mp_list      = []
    SG_Formula_list = []
    for material in Material_list:
        if material[0] == SG:
            SG_MPID_list.append(material[2])
            SG_mp_list.append(material[1])
            SG_Formula_list.append(material[-1])
    return SG_MPID_list, SG_Formula_list, SG_mp_list
def get_SG_HSL_information(SG):
    """
    Retrieve high-symmetry-line-related information for a given space-group number.
    Parameters
    SG : int
    Target space-group number.
    Returns
    tuple of five lists
    1. SG_HSL_name_list                 : names of all high-symmetry lines for this SG.
    2. SG_HSL_HSP_num_list              : number of high-symmetry points in each high-symmetry line.
    3. SG_HSL_HSP_list                  : names and coordinates of the high-symmetry points in each high-symmetry line.
    4. SG_HSL_coordinate_latex_list     : LaTeX-formatted coordinates of the high-symmetry lines.
    5. SG_HSL_HSP_latex_list : LaTeX-formatted names and coordinates of the high-symmetry points.

    """
    SG_HSL_name_list      = [item[1] for item in HSL_list if item[0] == SG]
    SG_HSL_HSP_num_list   = [item[2] for item in HSL_list if item[0] == SG]
    SG_HSL_HSP_list       = [item[-1] for item in HSL_list if item[0] == SG]
    SG_HSL_coordinate_latex_list     = [item[3] for item in HSL_latex_list if item[0] == SG]
    SG_HSL_HSP_latex_list = [item[-1] for item in HSL_latex_list if item[0] == SG]

    return (SG_HSL_name_list,
            SG_HSL_HSP_num_list,
            SG_HSL_HSP_list,
            SG_HSL_coordinate_latex_list,
            SG_HSL_HSP_latex_list)
def get_EBC_results_list(SG,material_mp,HSL_name):
    SG_HSL_name_list = get_SG_HSL_information(SG)[0]
    HSL_index = SG_HSL_name_list.index(HSL_name)
    HSL_all_HSP_list = get_SG_HSL_information(SG)[2][HSL_index]
    HSL_all_path_list = [HSL_all_HSP_list[i] + HSL_all_HSP_list[i + 1] for i in range(len(HSL_all_HSP_list) - 1)]
    HSL_HSP_coordinate_latex = get_SG_HSL_information(SG)[4][HSL_index]
    HSL_all_path_latex_list = [f"{a[0]} {a[1]}$——$${b[0]} {b[1]}" for a, b in zip(HSL_HSP_coordinate_latex[:-1], HSL_HSP_coordinate_latex[1:])]
    hsl_bc_inf_list = [result[-1] for result in Results_list if result[0] == SG and result[1] == material_mp and result[2] == HSL_name]
    hsl_bc_inf_finally_list = [list(row.values()) for row in hsl_bc_inf_list]
    hsp_bc_latex_list = [f"{idx[0]}$\\oplus${idx[1]}" for idx in hsl_bc_inf_list[0]]
    emp_rows = [r for r in EMP_list if r[0] == SG and r[1] == HSL_name]
    hsp_bc_topo_list, hsp_bc_emp_list = [], []
    for idx in hsl_bc_inf_list[0]:
        bc = f"{idx[0]},{idx[1]}"
        for er in emp_rows:
            try:
                pos = er[4].index(bc)
                hsp_bc_topo_list.append(er[6][pos])
                hsp_bc_emp_list.append(er[-2][pos])
                break
            except ValueError:
                continue
    return (hsl_bc_inf_list,HSL_all_path_list,HSL_all_path_latex_list,hsl_bc_inf_finally_list,hsp_bc_latex_list,hsp_bc_topo_list,hsp_bc_emp_list)
def get_HSL_table(SG,MPID,HSL_name):

    MPID_index = get_SG_material_infomation(SG)[0].index(MPID)
    mp = get_SG_material_infomation(SG)[2][MPID_index]
    HSL_index = get_SG_HSL_information(SG)[0].index(HSL_name)
    HSL_coordinate_latex = get_SG_HSL_information(SG)[3][HSL_index].replace("$","").replace("\\left","").replace("\\right","").replace("\\frac","").replace("}{","/").replace("{","").replace("}","").replace("\ ","").replace(" ","").replace(",",", ")
    HSL_HSP_coordinate_latex=[row.replace("$","").replace("\\left","").replace("\\right","").replace("\\frac","").replace("}{","/").replace("{","").replace("}","").replace("\ ","").replace(" ","").replace(",",", ") for row in get_EBC_results_list(SG,mp,HSL_name)[2]]
    HSL_HSP_num=len(HSL_HSP_coordinate_latex)
    hsl_bc_inf_list=get_EBC_results_list(SG,mp,HSL_name)[3]
    hsp_bc_latex_list=[row.replace("\\oplus","⊕").replace("$","") for row in get_EBC_results_list(SG,mp,HSL_name)[-3]]
    hsp_bc_topo_list=get_EBC_results_list(SG,mp,HSL_name)[-2]
    hsp_bc_emp_list=get_EBC_results_list(SG,mp,HSL_name)[-1]

    if HSL_HSP_num==2:
        print(f"-" * 98)
        print(f"{'':<38} {HSL_name}{HSL_coordinate_latex}")
        print(f"-" * 98)
        print(f"{HSL_HSP_coordinate_latex[0]:<43} {'|':<10} {HSL_HSP_coordinate_latex[1]:<43}")
        print(f"-"*98)
        print(f"{'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10} {'|':<10} {'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10}")
        for row in range(len(hsp_bc_latex_list)):
            print(f"{hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[0][row]:<10} {'|':<10} {hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[1][row]:<10}")
        print(f"-" * 98)

    else:
        print(f"-" * 208)
        print(f"{'':<90} {HSL_name}{HSL_coordinate_latex}")
        print(f"-" * 208)
        print(f"{HSL_HSP_coordinate_latex[0]:<43} {'|':<10} {HSL_HSP_coordinate_latex[1]:<43} {'|':<10} {HSL_HSP_coordinate_latex[2]:<43} {'|':<10} {HSL_HSP_coordinate_latex[3]:<43}")
        print(f"-"*208)
        print(f"{'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10} {'|':<10} {'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10} {'|':<10} {'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10} {'|':<10} {'Irr':<10} {'Topo':<10} {'EMP':<10} {'Num':<10}")
        for row in range(len(hsp_bc_latex_list)):
            print(f"{hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[0][row]:<10} {'|':<10} {hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[1][row]:<10} {'|':<10} {hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[2][row]:<10} {'|':<10} {hsp_bc_latex_list[row]:<10} {hsp_bc_topo_list[row]:<10} {hsp_bc_emp_list[row]:<10} {hsl_bc_inf_list[3][row]:<10}")
        print(f"-" * 208)

def menu_EMP_Catalog_table():
    ACC_EMP_list = ['C-1 WP', 'C-2 DP', 'C-2 WP', 'C-3 WP', 'DP', 'P-WNL', 'P-WNLs', 'QDP', 'QTP', 'TP']
    ACC_EMP_notation_list = ["Charge-1 Weyl point", "Charge-2 Dirac point", "Charge-2 Weyl point",
                             "Charge-3 Weyl point", "Dirac point",
                             "The nodal point located on a Weyl nodal line, or at the joint point of several Weyl nodal lines that can be connected to a specific Weyl nodal line through symmetry operators",
                             "The nodal point located at the joint point of several Weyl nodal lines",
                             "Quadratic Dirac point", "Quadratic triple point", "Triple point"]
    print(f"-" * 200)
    print(f"{'Emergent particle':<20} {'Notation of emergent particle':<20}")
    print(f"-" * 200)
    for row in range(len(ACC_EMP_list)):
        print(f"{ACC_EMP_list[row]:<20} {ACC_EMP_notation_list[row]:<10}")
    print(f"-" * 200)
def menu_Material_Catalog_table():
    SG = int(input("Enter space group number (1-230):\n").strip())
    if SG not in [i for i in range(1,231)]:
        print("Invalid choice.")
        return
    SG_HSL_name_list = get_SG_HSL_information(SG)[0]
    SG_HSL_coordinate_latex_list=[row.replace("$","").replace("\\left","").replace("\\right","").replace("\\frac","").replace("}{","/").replace("{","").replace("}","").replace("\ ","").replace(" ","").replace(",",", ") for row in get_SG_HSL_information(SG)[3]]
    SG_MPID_list,SG_Formula_list,SG_mp_list=get_SG_material_infomation(SG)
    SG_Formula_list=[row.replace("$","").replace("_","").replace("{","").replace("}","") for row in SG_Formula_list]
    HSL_latex=""
    for row in range(len(SG_HSL_name_list)):
        SG_HSL_name=SG_HSL_name_list[row]
        SG_HSL_coordinate=SG_HSL_coordinate_latex_list[row]
        hsl_str=f"{SG_HSL_name}{SG_HSL_coordinate}\t"
        HSL_latex=HSL_latex+hsl_str
    HSL_latex=HSL_latex[:-1]
    print("-"*(33+len(HSL_latex)+30))
    print(f"{'SG':<5} {'MPID':<10} {'Formula':<20} {'High-symmetry lines'}")
    print("-" * (33 + len(HSL_latex) + 30))
    for material_index in range(len(SG_MPID_list)):
        MPID=SG_MPID_list[material_index]
        Formula=SG_Formula_list[material_index]
        print(f"{SG:<5} {MPID:<10} {Formula:<20} {HSL_latex}")
    print("-" * (33 + len(HSL_latex) + 30))
def menu_Diagnosis_Result__table():
    input_str = input("Enter space group and Material Project Identification number (e.g., 187 10615). Optional: add HSL name → 187 10615 DT:\n")
    lst = re.findall("[0-9]+|[A-Z]+",input_str)
    if len(lst) not in [2,3]:
        print("Invalid choice.")
        return
    SG = int(lst[0])
    MPID = int(lst[1])
    if SG not in [row for row in range(1,231)]:
        print("Invalid choice.")
        return
    SG_MPID_list = get_SG_material_infomation(SG)[0]
    if MPID not in SG_MPID_list:
        print("Invalid choice.")
        return
    MPID_index = SG_MPID_list.index(MPID)
    Formula = get_SG_material_infomation(SG)[1][MPID_index].replace("$","").replace("_","").replace("{","").replace("}","")
    SG_HSL_name_list = get_SG_HSL_information(SG)[0]
    if len(lst)==2:
        print(f"{Formula} with MPID {MPID} and {SG}")
        for HSL_name in SG_HSL_name_list:
            get_HSL_table(SG, MPID, HSL_name)
            print("\n")
    else:
        HSL_name=lst[2]
        if HSL_name not in SG_HSL_name_list:
            print("Invalid choice.")
            return
        else:
            print(f"{Formula} with MPID {MPID} and {SG}")
            get_HSL_table(SG, MPID, HSL_name)
            print("\n")
def main_menu():
    while True:
        print("\n==========Diagnosis of enforced phonon band crossings in the entire frequency window by compatibility relations==========")
        print(" 1) EMP Catalog")
        print(" 2) Material Catalog")
        print(" 3) Diagnosis Result")
        print("\n 0) Quit")
        # print("=========================================================================================================================")
        print("------------>>")
        choice = input("").strip()
        if  choice == "1":
            menu_EMP_Catalog_table()
        elif choice == "2":
            menu_Material_Catalog_table()
        elif choice == "3":
            menu_Diagnosis_Result__table()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()

