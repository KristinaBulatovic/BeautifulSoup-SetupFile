import cx_Freeze

executables = [cx_Freeze.Executable("LuckyTruckScript1.py")]

cx_Freeze.setup(
    name = "LuckyTruck",
    options = {"build_exe": {"packages":["bs4", "os", "lxml"]}},
    executables = executables
    )