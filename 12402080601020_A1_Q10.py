import csv
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

DATA_FILE = "assignment_data.json"      # data is saved here automatically


class TrackerApp:
    def __init__(self, root):
        self.root = root
        root.title("Assignment Tracker")
        self.students = {}      # enrollment -> name
        self.records = []       # each: enrollment, name, assignment, status, marks, remarks
        self.load()
        self.build_ui()
        self.refresh()

    # ---------- saving and loading (JSON) ----------
    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, encoding="utf-8") as fh:
                    data = json.load(fh)
                self.students = data.get("students", {})
                self.records = data.get("records", [])
            except (OSError, json.JSONDecodeError):
                messagebox.showwarning("Load", "Data file unreadable; starting empty.")

    def save(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as fh:
                json.dump({"students": self.students, "records": self.records}, fh, indent=1)
        except OSError as e:
            messagebox.showerror("Save failed", str(e))

    # ---------- screen layout ----------
    def build_ui(self):
        f = ttk.Frame(self.root, padding=8)
        f.pack(fill="both", expand=True)
        self.v_enr, self.v_name = tk.StringVar(), tk.StringVar()
        self.v_asg, self.v_marks = tk.StringVar(value="Assignment 1"), tk.StringVar()
        self.v_status, self.v_late = tk.StringVar(value="Completed"), tk.BooleanVar()
        self.v_rem, self.v_filter = tk.StringVar(), tk.StringVar(value="All")

        ttk.Label(f, text="Enrollment").grid(row=0, column=0, sticky="w")
        ttk.Entry(f, textvariable=self.v_enr, width=14).grid(row=0, column=1)
        ttk.Label(f, text="Name").grid(row=0, column=2, sticky="w")
        ttk.Entry(f, textvariable=self.v_name, width=20).grid(row=0, column=3)

        ttk.Label(f, text="Assignment").grid(row=1, column=0, sticky="w")
        ttk.Combobox(f, textvariable=self.v_asg, width=14,
                     values=[f"Assignment {i}" for i in range(1, 11)]).grid(row=1, column=1)
        ttk.Label(f, text="Marks (0-100)").grid(row=1, column=2, sticky="w")
        ttk.Entry(f, textvariable=self.v_marks, width=8).grid(row=1, column=3, sticky="w")

        ttk.Radiobutton(f, text="Completed", variable=self.v_status, value="Completed").grid(row=2, column=0)
        ttk.Radiobutton(f, text="Pending", variable=self.v_status, value="Pending").grid(row=2, column=1)
        ttk.Checkbutton(f, text="Late submission", variable=self.v_late).grid(row=2, column=2)

        ttk.Label(f, text="Remarks").grid(row=3, column=0, sticky="w")
        ttk.Entry(f, textvariable=self.v_rem, width=40).grid(row=3, column=1, columnspan=3, sticky="we")

        bar = ttk.Frame(f)
        bar.grid(row=4, column=0, columnspan=4, pady=6)
        for text, cmd in (("Add Student", self.add_student),
                          ("Add Submission", self.add_submission),
                          ("Update Marks", self.update_marks),
                          ("Export CSV", self.export_csv)):
            ttk.Button(bar, text=text, command=cmd).pack(side="left", padx=3)

        ttk.Label(f, text="Filter").grid(row=5, column=0, sticky="w")
        flt = ttk.Combobox(f, textvariable=self.v_filter, state="readonly", width=12,
                           values=["All", "Pending", "Completed"])
        flt.grid(row=5, column=1)
        flt.bind("<<ComboboxSelected>>", lambda _e: self.refresh())
        self.lbl_count = ttk.Label(f, text="")
        self.lbl_count.grid(row=5, column=2, columnspan=2, sticky="e")

        cols = ("enrollment", "name", "assignment", "status", "marks", "remarks")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c.title())
            self.tree.column(c, width=100)
        sb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.grid(row=6, column=0, columnspan=4, sticky="nsew")
        sb.grid(row=6, column=4, sticky="ns")
        f.rowconfigure(6, weight=1)
        f.columnconfigure(3, weight=1)

    # ---------- input validation ----------
    def _enrollment(self):
        enr = self.v_enr.get().strip()
        if not enr.isalnum():
            raise ValueError("Enrollment must be non-empty letters/digits.")
        return enr

    def _marks(self, required):
        txt = self.v_marks.get().strip()
        if not txt:
            if required:
                raise ValueError("Marks are required.")
            return ""
        try:
            val = float(txt)
        except ValueError:
            raise ValueError("Marks must be a number.")
        if not 0 <= val <= 100:
            raise ValueError("Marks must be between 0 and 100.")
        return int(val) if val == int(val) else val

    # ---------- button actions ----------
    def add_student(self):
        try:
            enr = self._enrollment()
            name = self.v_name.get().strip()
            if not name or not all(ch.isalpha() or ch.isspace() for ch in name):
                raise ValueError("Name must contain only letters and spaces.")
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        self.students[enr] = name
        self.save()
        messagebox.showinfo("Student", f"Saved {enr} - {name}")

    def add_submission(self):
        try:
            enr = self._enrollment()
            if enr not in self.students:
                raise ValueError("Add the student first.")
            asg = self.v_asg.get().strip()
            if not asg:
                raise ValueError("Assignment is required.")
            status = self.v_status.get()
            marks = self._marks(required=(status == "Completed"))
            if any(r["enrollment"] == enr and r["assignment"] == asg for r in self.records):
                raise ValueError("That submission already exists.")
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        remarks = self.v_rem.get().strip()
        if self.v_late.get():
            remarks = (remarks + " Late").strip()
        self.records.append({"enrollment": enr, "name": self.students[enr],
                             "assignment": asg, "status": status,
                             "marks": marks, "remarks": remarks})
        self.save()
        self.refresh()

    def update_marks(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Update", "Select a row first.")
        try:
            marks = self._marks(required=True)
        except ValueError as e:
            return messagebox.showerror("Invalid input", str(e))
        rec = self.records[int(sel[0])]
        rec["marks"], rec["status"] = marks, "Completed"
        self.save()
        self.refresh()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            initialfile="report.csv",
                                            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh)
                w.writerow(["enrollment", "name", "assignment", "status", "marks", "remarks"])
                for r in self.records:
                    w.writerow([r["enrollment"], r["name"], r["assignment"],
                                r["status"], r["marks"], r["remarks"]])
            messagebox.showinfo("Export", "Report saved to " + path)
        except OSError as e:
            messagebox.showerror("Export failed", str(e))

    def refresh(self):
        flt = self.v_filter.get()
        self.tree.delete(*self.tree.get_children())
        shown = 0
        for i, r in enumerate(self.records):      # row id = position in self.records
            if flt == "All" or r["status"] == flt:
                self.tree.insert("", "end", iid=str(i), values=(
                    r["enrollment"], r["name"], r["assignment"],
                    r["status"], r["marks"], r["remarks"]))
                shown += 1
        self.lbl_count.config(text=f"Showing {shown} of {len(self.records)}")


if __name__ == "__main__":
    root = tk.Tk()
    TrackerApp(root)
    root.mainloop()