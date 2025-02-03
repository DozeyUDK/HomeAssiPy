import customtkinter
import os
os.add_dll_directory(r'C:\Program Files\IBM\IBM DATA SERVER DRIVER\bin')
import ibm_db
from datetime import datetime
from tkinter import messagebox
import threading

class MyCheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master, values, items):
        super().__init__(master)
        self.values = values
        self.items = items
        self.value_checkboxes = []
        self.item_checkboxes = []

        # Tworzenie checkboxów dla wartości po lewej stronie
        for i, value in enumerate(self.values):
            checkbox = customtkinter.CTkCheckBox(self, text=value)
            checkbox.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="w")
            self.value_checkboxes.append(checkbox)

        # Tworzenie checkboxów dla "items" po prawej stronie
        for i, item in enumerate(self.items):
            checkbox = customtkinter.CTkCheckBox(self, text=item)
            checkbox.grid(row=i, column=1, padx=10, pady=(10, 0), sticky="e")
            self.item_checkboxes.append(checkbox)

    def get_values(self):
        """Zwraca zaznaczone wartości po lewej stronie"""
        checked_values = []
        for checkbox in self.value_checkboxes:
            if checkbox.get() == 1:
                checked_values.append(checkbox.cget("text"))
        return checked_values

    def get_items(self):
        """Zwraca zaznaczone wartości po prawej stronie"""
        checked_items = []
        for checkbox in self.item_checkboxes:
            if checkbox.get() == 1:
                checked_items.append(checkbox.cget("text"))
        return checked_items

    def select_all_values(self):
        for checkbox in self.value_checkboxes:
            checkbox.select()

    def deselect_all_values(self):
        for checkbox in self.value_checkboxes:
            checkbox.deselect()

    def select_all_items(self):
        for checkbox in self.item_checkboxes:
            checkbox.select()

    def deselect_all_items(self):
        for checkbox in self.item_checkboxes:
            checkbox.deselect()

    def save_to_file(self):
        selected_values = self.get_values()
        selected_items = self.get_items()

        with open("selected_checkboxes.txt", "w") as file:
            file.write("Selected Values:\n")
            file.write("\n".join(selected_values))
            file.write("\n\nSelected Items:\n")
            file.write("\n".join(selected_items))
        print("Selections saved to selected_checkboxes.txt")

class ExcelTableWindow(customtkinter.CTkToplevel):
    def __init__(self, master, values, items):
        super().__init__(master)
        self.title("Excel-like Table")
        self.geometry("500x400")

        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(fill="both", expand=True)

        # Nagłówki tabeli
        header_values = customtkinter.CTkLabel(self.frame, text="Values", width=20)
        header_values.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        header_items = customtkinter.CTkLabel(self.frame, text="Items", width=20)
        header_items.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Wypełnianie tabeli danymi
        for i, value in enumerate(values):
            value_label = customtkinter.CTkLabel(self.frame, text=value, width=20)
            value_label.grid(row=i+1, column=0, padx=5, pady=5, sticky="nsew")

        for i, item in enumerate(items):
            item_label = customtkinter.CTkLabel(self.frame, text=item, width=20)
            item_label.grid(row=i+1, column=1, padx=5, pady=5, sticky="nsew")

class DatabaseConnector(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.db_connection = None
        
        self.grid_columnconfigure(0, weight=1)
        
        # Nagłówek
        self.connection_label = customtkinter.CTkLabel(self, text="Database Connection", font=("Arial", 16, "bold"))
        self.connection_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="w")
        
        # Pola wprowadzania danych
        labels = ["Host:", "Port:", "Username:", "Password:", "Database Name:"]
        self.entries = {}

        for i, label_text in enumerate(labels):
            label = customtkinter.CTkLabel(self, text=label_text)
            label.grid(row=i+1, column=0, padx=(10, 5), pady=5, sticky="w")

            entry = customtkinter.CTkEntry(self, width=300)
            if label_text == "Password:":
                entry.configure(show="*")

            if label_text == "Port:":
                entry.insert(0, "50000")  # Domyślny port Db2

            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="ew")
            self.entries[label_text.lower().replace(":", "").replace(" ", "_")] = entry
        
        # Przycisk połączenia
        self.connect_button = customtkinter.CTkButton(self, text="Connect", command=self.connect_to_database)
        self.connect_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Sekcja do wykonywania zapytań SQL
        self.sql_label = customtkinter.CTkLabel(self, text="Execute SQL Query:")
        self.sql_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        self.sql_entry = customtkinter.CTkEntry(self, width=300)
        self.sql_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        self.execute_sql_button = customtkinter.CTkButton(self, text="Execute Query", command=self.execute_sql)
        self.execute_sql_button.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Pole tekstowe na wyniki
        self.result_textbox = customtkinter.CTkTextbox(self, height=150, width=300)
        self.result_textbox.grid(row=10, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Dodatkowe przyciski
        button_frame = customtkinter.CTkFrame(self)
        button_frame.grid(row=11, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        clear_button = customtkinter.CTkButton(button_frame, text="Clear", command=self.clear_results)
        clear_button.pack(side="left", padx=5)

        save_button = customtkinter.CTkButton(button_frame, text="Save Results", command=self.save_results)
        save_button.pack(side="right", padx=5)

    def connect_to_database(self):
        """Nawiązywanie połączenia z bazą danych IBM Db2"""
        host = self.entries['host'].get()
        dbname = self.entries['database_name'].get()
        port = int(self.entries['port'].get())  # Pobranie portu Db2
        username = self.entries['username'].get()
        password = self.entries['password'].get()

        if not all([host, port, username, password, dbname]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            # 🔹 Połączenie z bazą IBM Db2
            conn_str = (
                f"DATABASE={dbname};"
                f"HOSTNAME={host};"
                f"PORT={port};"  # Port Db2
                f"PROTOCOL=TCPIP;"
                f"UID={username};"
                f"PWD={password};"
            )

            # Tworzenie połączenia do Db2
            self.db_connection = ibm_db.connect(conn_str, "", "")

            messagebox.showinfo("Success", "DB2 Connection Established!")
            
            # Uruchomienie wątku "keep-alive"
            keep_alive_thread = threading.Thread(target=self.keep_connection_alive, args=(self.db_connection,), daemon=True)
            keep_alive_thread.start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.db_connection = None

    def keep_connection_alive(self, conn):
        """Utrzymanie połączenia z bazą Db2 aktywnego"""
        import time
        try:
            while True:
                if not ibm_db.active(conn):
                    messagebox.showerror("Error", "Connection lost!")
                    break
                time.sleep(60)  # Sprawdzamy co minutę
        except Exception as e:
            print(f"Keep-alive error: {str(e)}")

    def execute_sql(self):
        """Wykonuje zapytanie SQL w bazie Db2"""
        if not self.db_connection:
            messagebox.showerror("Error", "Connect to the database first!")
            return
        
        query = self.sql_entry.get()
        if not query.strip():
            messagebox.showwarning("Warning", "Enter an SQL query!")
            return
        
        try:
            stmt = ibm_db.exec_immediate(self.db_connection, query)
            results = []
            result = ibm_db.fetch_assoc(stmt)
            while result:
                results.append(result)
                result = ibm_db.fetch_assoc(stmt)

            output = "\n".join([str(row) for row in results]) if results else "No results."
            
            self.result_textbox.delete("1.0", "end")
            self.result_textbox.insert("1.0", output)
        
        except Exception as e:
            messagebox.showerror("Query Error", str(e))

    def clear_results(self):
        """Czyści pole wyników"""
        self.result_textbox.delete("1.0", "end")

    def save_results(self):
        """Zapisuje wyniki zapytania SQL do pliku"""
        results = self.result_textbox.get("1.0", "end").strip()
        
        if not results:
            messagebox.showwarning("Warning", "No results to save!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sql_results_{timestamp}.txt"
        
        with open(filename, "w") as f:
            f.write(results)
        
        messagebox.showinfo("Success", f"Results saved to {filename}")

    def disconnect(self):
        """Rozłącza połączenie z bazą danych"""
        if self.db_connection:
            ibm_db.close(self.db_connection)
            self.db_connection = None
        messagebox.showinfo("Disconnected", "Database connection closed.")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("My App with Items and Tabs")
        self.geometry("1200x960")  # Increased width to accommodate both frames

        # Create main container frame
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both")
       
        # Left side
        self.left_frame = customtkinter.CTkFrame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Right side
        self.right_frame = customtkinter.CTkFrame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        # Left tabview
        self.tabview = customtkinter.CTkTabview(self.left_frame)
        self.tabview.add("Values & Items")
        self.tabview.add("Results")
        self.tabview.add("Manage Files")
        self.tabview.pack(expand=True, fill="both")

        # Right tabview
        self.tabview2 = customtkinter.CTkTabview(self.right_frame)
        self.tabview2.add("Values & Items")
        self.tabview2.add("Results")
        self.tabview2.add("Manage Files")
        self.tabview2.pack(expand=True, fill="both")

        # Lists for both frames
        values = ["value 1", "value 2", "value 3", "value 4", "value 5", "value 6"]
        items = ["item 1", "item 2", "item 3", "item 4", "item 5", "item 6"]

        # Left frame components
        self.checkbox_frame = MyCheckboxFrame(self.tabview.tab("Values & Items"), values=values, items=items)
        self.checkbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_show = customtkinter.CTkButton(self.tabview.tab("Values & Items"), text="Show Selected", command=self.button_callback)
        self.button_show.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.button_save = customtkinter.CTkButton(self.tabview.tab("Manage Files"), text="Save to File", command=self.checkbox_frame.save_to_file)
        self.button_save.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.results_label_values = customtkinter.CTkLabel(self.tabview.tab("Results"), text="Selected Values:")
        self.results_label_values.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.results_label_items = customtkinter.CTkLabel(self.tabview.tab("Results"), text="Selected Items:")
        self.results_label_items.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.button_table = customtkinter.CTkButton(self.tabview.tab("Values & Items"), text="Open Table", command=self.open_excel_table)
        self.button_table.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Right frame components
        self.checkbox_frame2 = DatabaseConnector(self.tabview2.tab("Values & Items"))
        self.checkbox_frame2.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.button_show2 = customtkinter.CTkButton(self.tabview2.tab("Values & Items"), text="Show Selected", command=self.button_callback2)
        self.button_show2.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.button_save2 = customtkinter.CTkButton(self.tabview2.tab("Manage Files"), text="Save to File", command=self.checkbox_frame2.save_results)
        self.button_save2.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.results_label_values2 = customtkinter.CTkLabel(self.tabview2.tab("Results"), text="Selected Values:")
        self.results_label_values2.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.results_label_items2 = customtkinter.CTkLabel(self.tabview2.tab("Results"), text="Selected Items:")
        self.results_label_items2.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.button_table2 = customtkinter.CTkButton(self.tabview2.tab("Values & Items"), text="Open Table", command=self.open_excel_table2)
        self.button_table2.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    def button_callback(self):
        selected_values = self.checkbox_frame.get_values()
        selected_items = self.checkbox_frame.get_items()
        self.results_label_values.configure(text="Selected Values:\n" + "\n".join(selected_values))
        self.results_label_items.configure(text="Selected Items:\n" + "\n".join(selected_items))

    def button_callback2(self):
        selected_values = self.checkbox_frame2.get_values()
        selected_items = self.checkbox_frame2.get_items()
        self.results_label_values2.configure(text="Selected Values:\n" + "\n".join(selected_values))
        self.results_label_items2.configure(text="Selected Items:\n" + "\n".join(selected_items))

    def open_excel_table(self):
        selected_values = self.checkbox_frame.get_values()
        selected_items = self.checkbox_frame.get_items()
        table_window = ExcelTableWindow(self, values=selected_values, items=selected_items)
        table_window.grab_set()

    def open_excel_table2(self):
        selected_values = self.checkbox_frame2.get_values()
        selected_items = self.checkbox_frame2.get_items()
        table_window = ExcelTableWindow(self, values=selected_values, items=selected_items)
        table_window.grab_set()

if __name__ == "__main__":
    app = App()
    app.mainloop()
