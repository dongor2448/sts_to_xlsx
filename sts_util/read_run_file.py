import os


def get():
    run_file = []
    print("searching run history... please wait")
    for root, dirs, files in os.walk(os.getcwd(), topdown=False):
        for name in files:
            if os.path.join(root, name).endswith(r".run"):
                run_file.append(os.path.join(root, name))
    return run_file