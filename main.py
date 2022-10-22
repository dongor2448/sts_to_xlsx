from sts_util import read_run_file, load_sts_df, write_data, output_xlsx
import os


character_chosen = ["IRONCLAD", "WATCHER", "THE_SILENT", "DEFECT"]


if __name__ == "__main__":
    path_list = read_run_file.get()
    df = load_sts_df.load_df(path_list)
    if df.shape[0] != 0:
        for char in character_chosen:
            summary = write_data.write(df, char)
            if summary != {}:
                output_xlsx.output(summary, char)
    else:
        print(f"no run history founded...")
    if os.path.exists(f"./stsinform"):
        print("done!")
    os.system("pause")

