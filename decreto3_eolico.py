import tkinter as tk
from tkinter import filedialog, ttk
import os

from decreto3eolico.analysis_executor import run_analysis


def browse_file(entry_widget):
    filename = filedialog.askopenfilename()
    if filename:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, filename)


def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, directory)


def generate_report():
    files = {
        "distanza_angolo_WTG": file1_entry.get(),
        "input_file_CMG": file2_entry.get(),
        "input_file_meteo": file3_entry.get(),
        "input_file_turbine_parameters": file4_entry.get()
    }
    orografia_choice = orografia_var.get()
    results_dir = results_entry.get()

    if not all(files.values()) or not results_dir:
        status_label.config(
            text="Error: Please select all files and output directory", fg="red")
        return

    # Placeholder for report generation logic
    report_path = os.path.join(results_dir, "generated_report.txt")
    try:
        run_analysis(
            files["distanza_angolo_WTG"],
            files["input_file_CMG"],
            files["input_file_meteo"],
            files["input_file_turbine_parameters"],
            orografia_choice,
            results_dir,
        )
    except Exception as e:
        status_label.config(
            text=f"Error generating report: {e}", fg="red")
        return
    # clean all entries
    for entry in file_entries:
        entry.delete(0, tk.END)

    status_label.config(text=f"Report saved at: {report_path}", fg="green")


# Create main window
root = tk.Tk()
root.state('zoomed')
root.title("Decreto3 Eolico Report Generator")
root.geometry("800x300")

# File entry fields
file1_entry = tk.Entry(root, width=50)
file2_entry = tk.Entry(root, width=50)
file3_entry = tk.Entry(root, width=50)
file4_entry = tk.Entry(root, width=50)
results_entry = tk.Entry(root, width=50)

file_entries = [file1_entry, file2_entry,
                file3_entry, file4_entry, results_entry]

# Browse buttons
browse_buttons = [
    tk.Button(root, text="Browse", command=lambda e=entry: browse_file(e))
    for entry in file_entries[:-1]
]
browse_buttons.append(tk.Button(root, text="Browse",
                      command=lambda: browse_directory(results_entry)))

# Orografia dropdown
orografia_var = tk.StringVar()
orografia_dropdown = ttk.Combobox(root, textvariable=orografia_var, values=[
                                  "complessa", "semplice"], state="readonly")
orografia_dropdown.set("complessa")  # Default choice

# Layout
labels = [
    "Distanza Angolo WTG:", "Input File CMG:", "Input File Meteo:",
    "Input File Turbine Parameters:", "Results Directory:"
]

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(
        row=i, column=0, padx=10, pady=5, sticky='w')
    file_entries[i].grid(row=i, column=1, padx=10, pady=5)
    browse_buttons[i].grid(row=i, column=2, padx=10, pady=5)

tk.Label(root, text="Orografia:").grid(
    row=5, column=0, padx=10, pady=5, sticky='w')
orografia_dropdown.grid(row=5, column=1, padx=10, pady=5)

# Generate button
generate_button = tk.Button(
    root, text="Generate Report", command=generate_report)
generate_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

# Status label
status_label = tk.Label(root, text="", fg="black")
status_label.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

# Start main loop
root.mainloop()
