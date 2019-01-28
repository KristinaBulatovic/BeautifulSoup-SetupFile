import cx_Freeze

executables = [cx_Freeze.Executable("scrape.py")]

cx_Freeze.setup(
    name = "LuckyTruck",
    options = {"build_exe": {"packages":["bs4", "os", "lxml","pandas","re","requests", "numpy"], "includes" : "idna.idnadata"}},
    executables = executables

    )

