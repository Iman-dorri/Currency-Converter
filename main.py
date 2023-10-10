import requests
import json
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from decimal import Decimal
import calendar
import os


class CurrencyConverter:
    def __init__(self):
        self.data = self.load_currency_data()

    def fetch_currency_data(self):
        """
        This method should fetch new currency data using the openexchangerate API
        It has some boilerplate code you can use.
        """
        app_id = os.environ["app_id"]
        url = f"https://openexchangerates.org/api/latest.json?app_id={app_id}"
        headers = {
            "accept": "application/json"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def check_result(self, result: float):
        if result <= 9.999000099990002e-05:
            return round(Decimal(result), 6)
        else:
            return round(result, 2)

    def convert_any_currency(self, from_currency, to_currency, amount):
        result = ""
        if len(from_currency) == 0 or len(to_currency) == 0 or len(str(amount)) == 0:
            messagebox.showerror(title="Error", message="Please do not leave any fields empty!")
        elif not amount.isdigit():
            messagebox.showerror(title="Error", message="Please enter a positive "
                                                        "number with no decimal in amount field!")
        elif from_currency.isdigit():
            messagebox.showerror(title="Error", message="Please enter an existing currency from the list!")
        elif to_currency.isdigit():
            messagebox.showerror(title="Error", message="Please enter an existing currency from the list!")
        else:
            currency_rate_from = 0
            currency_rate_to = 0
            for key, value in self.data["rates"].items():
                if from_currency in key:
                    currency_rate_from = value
            for key, value in self.data["rates"].items():
                if to_currency in key:
                    currency_rate_to = value
                try:
                    result = (currency_rate_to / currency_rate_from) * int(amount)
                except ZeroDivisionError:
                    messagebox.showerror(title="Error", message="Please enter an existing currency from the list!")
                    break
            try:
                final_result = self.check_result(float(result))
                if final_result == 0.000000:
                    messagebox.showerror(title="Error", message="Please enter an existing currency from the list!")
                else:
                    messagebox.showinfo(title="Result",
                                        message=f"{amount} {from_currency} is equal to {final_result} {to_currency}")
            except ValueError:
                pass
        return result

    def list_currencies(self):
        options = []
        for key, value in self.data["rates"].items():
            options.append(f"{key} - {value}")
        return options

    def load_currency_data(self):
        try:
            with open("data.json", "r") as data_file:
                self.data = json.load(data_file)
        except FileNotFoundError:
            self.data = self.fetch_currency_data()
            with open("data.json", "w") as data_file:
                json.dump(self.data, data_file, indent=4)
        modification_time = self.data["timestamp"]
        time_now = datetime.now().now()
        if modification_time < calendar.timegm(time_now.utctimetuple()):
            self.data = self.fetch_currency_data()
            with open("data.json", "w") as data_file:
                json.dump(self.data, data_file, indent=4)
                messagebox.showinfo(title="Info", message="The data has been updated successfully!")
                return self.data
        else:
            return self.data

    def export_to_json(self):
        with open("data.json", "w") as data_file:
            json.dump(self.data, data_file, indent=4)
            print("The data has been saved!")


# -------------------------------------------------UI SETUP----------------------------------------------------------- #


def main():
    converter = CurrencyConverter()
    windows = Tk()
    windows.title("Currency Converter")
    windows.config(padx=50, pady=50)

    canvas = Canvas(width=300, height=300)
    logo_png = PhotoImage(file="logo.png")
    canvas.create_image(150, 150, image=logo_png)
    canvas.grid(column=0, row=0, columnspan=6)

    # datatype of menu text
    clicked = StringVar()

    # initial menu text
    clicked.set("List of all currencies")

    # Create Dropdown menu
    options = converter.list_currencies()
    drop = OptionMenu(windows, clicked, *options)
    drop.config()
    drop.grid(column=3, row=2, columnspan=3)

    amount_label = Label(text="Enter the amount here:")
    amount_label.grid(column=0, row=3)
    amount_entry = Entry(width=20)
    amount_entry.grid(column=1, row=3)

    chosen_currency_label = Label(text="Convert from:")
    chosen_currency_label.grid(column=2, row=3)
    convert_from_entry = Entry(width=20)
    convert_from_entry.grid(column=3, row=3)

    chosen_currency_label_2 = Label(text="to:")
    chosen_currency_label_2.grid(column=4, row=3)
    convert_to_entry = Entry(width=20)
    convert_to_entry.grid(column=5, row=3)

    convert_button = Button(text="Convert", width=19,
                            command=lambda:
                            converter.convert_any_currency(from_currency=convert_from_entry.get().upper(),
                                                           to_currency=convert_to_entry.get().upper(),
                                                           amount=amount_entry.get()))
    convert_button.grid(column=3, row=5, columnspan=3)
    refresh_button = Button(text="Refresh data", width=15, command=converter.load_currency_data)
    refresh_button.grid(column=0, row=2)
    export_button = Button(text="Export data", width=15, command=converter.export_to_json)
    export_button.grid(column=0, row=5)
    modification_time = datetime.fromtimestamp(converter.data["timestamp"])
    modification_datetime = modification_time.strftime("%X")
    modification_info = Label(text=f"The data is modified at: {modification_datetime}")
    modification_info.grid(column=0, row=1)
    windows.mainloop()


if __name__ == "__main__":
    main()
