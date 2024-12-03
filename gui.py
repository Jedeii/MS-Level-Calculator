import tkinter as tk
from tkinter import ttk, messagebox
from calculator import calculate_progress_dynamic, optimize_potion_usage
from data_loader import load_data

DEBUG = True

# Load data
data_levels, data_dailys = load_data()

def create_gui():
    def on_calculate():
        try:
            current_level = int(entry_level.get())
            current_exp = int(entry_exp.get())
            target_level = int(entry_target_level.get())
            burning = var_burning.get()
            include_mp = var_mp.get()  # Get Monster Park checkbox state
            mp_runs = int(entry_mp_runs.get() or 1)  # Default to 1 run if input is empty

            # Validate target level
            if target_level <= current_level:
                messagebox.showerror("Input Error", "Target Level must be higher than Current Level.")
                return

            # Get potion recommendations
            potions = [
                {"type": "TyGP", "quantity": int(entry_typhon.get() or 0), "level_cap": 240, "flat_rate": 137_783_047_111},
                {"type": "MGP", "quantity": int(entry_magnificent.get() or 0), "level_cap": 250, "flat_rate": 294_971_656_640},
                {"type": "TGP", "quantity": int(entry_transcendent.get() or 0), "level_cap": 270, "flat_rate": 2_438_047_518_853},
            ]

            recommendations = optimize_potion_usage(
                current_level, current_exp, target_level, potions, data_levels, data_dailys, burning, debug=DEBUG
            )

            # Perform dynamic calculations
            results = calculate_progress_dynamic(
                data_levels,
                data_dailys,
                current_level,
                current_exp,
                burning,
                target_level,
                recommendations={},  # Provide an empty dictionary if no recommendations are passed
                include_mp=include_mp,
                mp_runs=mp_runs,
                debug=DEBUG
            )

            # Perform calculations with recommendations
            adjusted_results = calculate_progress_dynamic(
                data_levels,
                data_dailys,
                current_level,
                current_exp,
                burning,
                target_level,
                recommendations,
                include_mp=include_mp,
                mp_runs=mp_runs,
                debug=DEBUG
            )

            # Display progression results
            result_total_exp.config(text=f"Total EXP Needed: {results['Total_EXP_Needed']:,}")
            result_days.config(text=f"Estimated Days to Level {target_level}: {results['Total_Days']:.2f} days")
            result_nx_cost.config(text=f"Total NX Cost: {results['Total_Cost_NX']} NX")  # Display NX cost

            # Display adjusted results
            result_adjusted_days.config(
                text=f"Estimated Days with Recommendations: {adjusted_results['Total_Days']:.2f} days"
            )

            # Display optimization results
            result_typhon.config(text=", ".join(map(str, recommendations['TyGP'])))
            result_magnificent.config(text=", ".join(map(str, recommendations['MGP'])))
            result_transcendent.config(text=", ".join(map(str, recommendations['TGP'])))

            if DEBUG:
                print(f"DEBUG: Results -> Total EXP: {results['Total_EXP_Needed']:,}, Days: {results['Total_Days']:.2f}")
                print(f"DEBUG: Adjusted Results -> Days with Recommendations: {adjusted_results['Total_Days']:.2f}")
                print(f"DEBUG: Total NX Cost -> {results['Total_Cost_NX']} NX")
                print(f"DEBUG: Potion Recommendations -> {recommendations}")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for level, EXP, and target level.")

    # Main window
    root = tk.Tk()
    root.title("Level Progression Calculator")

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Main Tab
    tab_main = ttk.Frame(notebook)
    notebook.add(tab_main, text="Main")

    tk.Label(tab_main, text="Current Level (200 or above):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_level = tk.Entry(tab_main)
    entry_level.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(tab_main, text="Current EXP:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_exp = tk.Entry(tab_main)
    entry_exp.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(tab_main, text="Target Level:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_target_level = tk.Entry(tab_main)
    entry_target_level.insert(0, "260")  # Default target level
    entry_target_level.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(tab_main, text="Number of Monster Park Runs:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
    entry_mp_runs = tk.Entry(tab_main)
    entry_mp_runs.insert(0, "1")  # Default to 1 run per day
    entry_mp_runs.grid(row=3, column=1, padx=10, pady=5)

    var_burning = tk.BooleanVar(value=False)
    tk.Checkbutton(tab_main, text="Burning (Level Up +2 per level)", variable=var_burning).grid(row=4, column=0, columnspan=2, pady=5)

    var_mp = tk.BooleanVar(value=True)
    tk.Checkbutton(tab_main, text="Include Monster Park (Highest Available EXP)", variable=var_mp).grid(row=5, column=0, columnspan=2, pady=5)

    tk.Button(tab_main, text="Calculate", command=on_calculate).grid(row=6, column=0, columnspan=2, pady=10)

    result_total_exp = tk.Label(tab_main, text="Total EXP Needed:")
    result_total_exp.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    result_days = tk.Label(tab_main, text="Estimated Days to Level:")
    result_days.grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    result_nx_cost = tk.Label(tab_main, text="Total NX Cost: 0 NX")
    result_nx_cost.grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    result_adjusted_days = tk.Label(tab_main, text="Estimated Days with Recommendations:")
    result_adjusted_days.grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    # Dailies Tab
    tab_dailies = ttk.Frame(notebook)
    notebook.add(tab_dailies, text="Dailies")

    tk.Label(tab_dailies, text="Select the dailies you plan to complete:").grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

    daily_vars = {}
    for i, row in data_dailys.iterrows():
        var = tk.BooleanVar(value=True)  # Default to True
        daily_vars[row['Daily']] = var
        tk.Checkbutton(tab_dailies, text=f"{row['Daily']} (EXP: {row['EXP_Reward']:,})", variable=var).grid(row=i + 1, column=0, sticky="w", padx=10, pady=2)

    # Bonk Potions Tab
    tab_bonk_pots = ttk.Frame(notebook)
    notebook.add(tab_bonk_pots, text="Bonk Potions")

    tk.Label(tab_bonk_pots, text="Typhon Growth Potions:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
    entry_typhon = tk.Entry(tab_bonk_pots)
    entry_typhon.insert(0, "0")
    entry_typhon.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(tab_bonk_pots, text="Magnificent Growth Potions:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
    entry_magnificent = tk.Entry(tab_bonk_pots)
    entry_magnificent.insert(0, "0")
    entry_magnificent.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(tab_bonk_pots, text="Transcendent Growth Potions:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
    entry_transcendent = tk.Entry(tab_bonk_pots)
    entry_transcendent.insert(0, "0")
    entry_transcendent.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(tab_main, text="Typhon Recommendations:").grid(row=13, column=0, sticky="w", padx=10, pady=5)
    result_typhon = tk.Label(tab_main, text="")
    result_typhon.grid(row=13, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_main, text="Magnificent Recommendations:").grid(row=14, column=0, sticky="w", padx=10, pady=5)
    result_magnificent = tk.Label(tab_main, text="")
    result_magnificent.grid(row=14, column=1, sticky="w", padx=10, pady=5)

    tk.Label(tab_main, text="Transcendent Recommendations:").grid(row=15, column=0, sticky="w", padx=10, pady=5)
    result_transcendent = tk.Label(tab_main, text="")
    result_transcendent.grid(row=15, column=1, sticky="w", padx=10, pady=5)

    root.mainloop()


# Uncomment this line to run the GUI
create_gui()
