import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from app.controllers.Controller import Controller
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import numpy as np
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.figure import Figure

#Exceptions
from app.exceptions.UserRegistrationError import UserRegistrationError
from app.exceptions.UserLogInError import UserLogInError
from app.exceptions.UserFitbitAccountAlreadyInUseError import UserFitbitAccountAlreadyInUseError
from app.exceptions.UserTriesToPredictException import UserTriesToPredictException

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HeartPred'it")
        self.geometry("920x700")

        """Controller"""
        self.controller = Controller(self)

        """View Elements Status/Information"""
        self.is_authorized = False
        self.popup =None
        self.authorize_fitbit_button = None
        self.update_label = None
        self.current_prediction_canvas = None
        self.register_frame = None
        self.prediction_frame = None
        self.progress_var = tk.DoubleVar()

        """Main method to setup HeartPred'it UI """
        self.setup_ui()

    """
        Creates all elements for HeartPred'it UI
    """
    def setup_ui(self):
        self.login_auth_frame = tk.Frame(self, bg="white")
        self.login_auth_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.notebook = ttk.Notebook(self.login_auth_frame)
        self.notebook.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.create_login_frame()
      
        self.controller.set_login_frame(self.login_frame)

    """Create Login Frame where login elements such as email and password entries"""
    def create_login_frame(self):
        self.login_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.login_frame, text="Inicio de Sesión")
        self.create_label(self.login_frame, "Inicio de Sesión", 20)
        self.create_entry(self.login_frame, "Correo: (*)", False, 'email_entry')
        self.create_entry(self.login_frame, "Contraseña: (*)", True, 'password_entry')
        self.create_register_link(self.login_frame)
        self.create_button(self.login_frame, "Inicio de Sesión", self.on_login_click)

    """Creates Label to insert into 'frame' frame with 'text' = text and 'size' = size """
    def create_label(self, frame, text, size, fg="white", bg="#457EAC"):
        label = tk.Label(frame, text=text, font=("arial", size), fg=fg, bg=bg)
        label.pack(pady=5, padx=20, fill=tk.X)
        return label

    """Creates Tkinter entry on 'frame' = frame with 'text' = text and show attribute """
    def create_entry(self, frame, text, show, attr_name):
        tk.Label(frame, text=text, pady=2, fg="white", bg="#457EAC", font=('arial', 14)).pack(anchor='w', padx=20, pady=(20, 0))
        entry = tk.Entry(frame, show="*" if show else "")
        entry.pack(fill=tk.X, padx=20, pady=5)
        setattr(self, attr_name, entry)
        return entry
    
    """Creates register link on 'frame' = frame"""
    def create_register_link(self, frame):
        container = tk.Frame(frame, bg="#457EAC")
        container.pack(pady=10, padx=20, fill=tk.X)
        register_label = tk.Label(container, text="¿No tienes cuenta? Regístrate aquí", fg="white", cursor="hand2", bg="#457EAC", font=('arial', 12))
        register_label.pack(pady=2)
        register_label.bind("<Button-1>", self.on_register_click)
        return register_label
    
    """Logic for selecting Login Frame"""
    def select_login_frame(self):
        for tab_id in self.notebook.tabs():
            tab_name = self.notebook.tab(tab_id, "text")
            if tab_name == "Inicio de Sesión":
                self.notebook.select(tab_id)
                break 

    """Creates a Tkinter Button into 'frame' = frame with 'text' = text executing when clicked 'command' method """
    def create_button(self, frame, text, command, state="normal", label_var=None):
        container = tk.Frame(frame, bg="#457EAC")
        container.pack(pady=2)
        button = tk.Button(container, text=text, fg="white", bg="#457EAC", state=state, command=lambda: self.button_click(command, label_var), font=("arial", 12))
        button.pack(side=tk.LEFT)  
        if label_var is not None:
            label = tk.Label(container, textvariable=label_var, fg="green", bg="#457EAC")
            label.pack(side=tk.LEFT, pady=5)
        return button
    
    """Executes command method related to a tKinter button"""
    def button_click(self, command, label_var):
        command()
        if label_var is not None:
            label_var.set("✓")

    """Command that implements login in"""
    def on_login_click(self):

        try:
            email = self.email_entry.get()
            password = self.password_entry.get()

            if self.controller.check_login(email, password):
                self.controller.updateFitbitUserInfo(email)

                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)
                self.create_app_notebook()

        except UserLogInError as e: 
            self.show_error_message(self.login_frame, e.getMessage())
            return False
        
        else:
            self.show_error_message(self.login_frame, "Ups...! Inicio de sesión fallido!")

    """Show into 'frame' = frame 'text' error"""
    def show_error_message(self, frame, text):
        error_label = tk.Label(frame, text=text, font=("arial", 15), fg="red")
        error_label.pack(pady=5, padx=20, fill=tk.X)
        self.after(2000, error_label.pack_forget)

    """Creates App notebook"""
    def create_app_notebook(self):
        self.app_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.app_frame, text="HeartPred'it")
        
        header_frame = tk.Frame(self.app_frame, bg="#457EAC")
        header_frame.pack(side=tk.TOP, fill=tk.X)

        logout_button = tk.Button(header_frame, text="Cerrar Sesión", fg="white", bg="#457EAC", command=self.logout)
        logout_button.pack(side=tk.RIGHT, padx=20, pady=10)

        goodbye_acount_button = tk.Button(header_frame, text="Eliminar Cuenta", fg="white", bg="#457EAC", command=self.deleteUserAccount)
        goodbye_acount_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.create_welcome_label(self.app_frame)

    """Logic for user account delete"""
    def deleteUserAccount(self):
        """Logic for confirm user delete account"""
        def confirm_deletion():
            self.controller.deleteUserAccount()
            confirm_popup.destroy()

            for tab_id in self.notebook.tabs():
                self.notebook.forget(tab_id)
            self.create_login_frame()


        confirm_popup = tk.Toplevel(self.app_frame)
        confirm_popup.title("Confirmar Eliminación")
        confirm_popup.geometry("300x150")
        confirm_popup.configure(bg="#457EAC")

        label = tk.Label(confirm_popup, text="¿Seguro que quieres eliminar la cuenta?\n¡Acción irrevocable!", bg="#457EAC", fg="white")
        label.pack(pady=20)

        button_frame = tk.Frame(confirm_popup, bg="#457EAC")
        button_frame.pack(pady=10)

        confirm_button = tk.Button(button_frame, text="Confirmar", fg="white", bg="#FF0000", command=confirm_deletion)
        confirm_button.pack(side=tk.LEFT, padx=10)

        cancel_button = tk.Button(button_frame, text="Atrás", fg="white", bg="#457EAC", command=confirm_popup.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=10)
    
    """Logic for user logOut"""
    def logout(self):
        self.controller.logout()
        for tab_id in self.notebook.tabs():
            self.notebook.forget(tab_id)

        self.create_login_frame()

       
    """Creates Welcome label into 'frame' = frame"""
    def create_welcome_label(self, frame):
        user_info = self.controller.user_info()
        if user_info:
            self.create_label(frame, f"¡Bienvenido, {user_info}!", 20)
            self.create_status_frame(frame)
    
    """Creates status frame"""
    def create_status_frame(self, frame):
        self.status_frame = tk.Frame(frame, bg="#457EAC")
        self.status_frame.pack(pady=10, padx=20, fill=tk.X)

        last_update = self.controller.last_update()

        if last_update:
            last_update = last_update.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        else:
            last_update = "Nunca"

        self.update_label = self.create_label(self.status_frame, f"Última Sincronización: {last_update}", 14, fg="white", bg="#457EAC")
        self.create_button(self.status_frame, "Sincronizar", self.update_status)

        try:
            self.create_button(self.status_frame, "Predecir", self.on_predict_submit)
        except UserTriesToPredictException as e:
            self.show_error_message(self.status_frame, e.getMessage())
            return False


    """Logic for register click event"""
    def on_register_click(self, event):
        if self.register_frame is None:
            self.create_register_frame()
        self.notebook.select(self.register_frame)

    """Logic for creation of register frame"""
    def create_register_frame(self):
        self.register_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.register_frame, text="Registro")
        self.create_label(self.register_frame, "Registro", 20)
        self.create_entry(self.register_frame, "Usuario: (*)", False, 'register_user_entry')
        self.create_entry(self.register_frame, "Correo: (*)", False, 'register_email_entry')
        self.create_entry(self.register_frame, "Contraseña: (*)", True, 'register_password_entry')
        self.create_entry(self.register_frame, "Edad: (*)", False, 'age_entry')
        self.authorize_label_var = tk.StringVar()

        self.authorize_fitbit_button = self.create_button(self.register_frame, "Paso 1: Autorizar con Fitbit", self.authorize_with_fitbit, label_var=self.authorize_label_var)
        self.register_button = self.create_button(self.register_frame, "Paso 2: Registrarse", self.on_register_submit, state="disabled")

    """Logic for user register submit"""
    def on_register_submit(self):
        user = self.register_user_entry.get()
        email = self.register_email_entry.get()
        password = self.register_password_entry.get()
        age = self.age_entry.get()

        user_id = self.controller.fitbitAPI.user_id
        access_token = self.controller.fitbitAPI.access_token
        refresh_token = self.controller.fitbitAPI.refresh_token
        expires_in = self.controller.fitbitAPI.expires_in
        
        try:
            exito = self.controller.register(user, email, password, age, user_id, access_token, refresh_token, expires_in)
            if exito :
                 self.notebook.forget(self.register_frame)
                 self.notebook.forget(self.login_frame)
                 self.create_login_frame()
            return exito
        
        except UserRegistrationError as e: 
            self.show_error_message(self.register_frame, e.getMessage())
            return False
        except UserFitbitAccountAlreadyInUseError as e:
            self.notebook.forget(self.register_frame)
            self.show_error_message(self.login_frame, e.getMessage())

    """Logic for user prediction"""
    def on_predict_submit(self):

        self.ult_act = self.controller.checkLasUpdate()
        if self.ult_act is not None:
            if self.prediction_frame is None:
                self.create_prediction_frame()
            self.notebook.select(self.prediction_frame)
        else:
           self.show_error_message(self.status_frame, "Sincroniza antes de intentar predecir. Estado de Sincronización: Nunca")

    """Logic for prediction frame creation"""
    def create_prediction_frame(self):
        self.prediction_frame = tk.Frame(self.notebook, bg="#457EAC")
        self.notebook.add(self.prediction_frame, text="Predicción")

        last_update = self.controller.checkLasUpdate() 
        if last_update:
            last_update = last_update.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        else:
            last_update = "Nunca"

        self.update_label = self.create_label(self.prediction_frame, f"Última Sincronización: {last_update}", 14, fg="white", bg="#457EAC")
        
        self.comboBox = ttk.Combobox(self.prediction_frame, values=[5, 10, 15, 20, 25, 30])
        self.comboBox.set("Selecciona minutos")
        self.comboBox.pack(pady=20)
        
        self.create_button(self.prediction_frame, "Sincronizar", self.update_status)
        self.create_button(self.prediction_frame, "Predecir Ahora", self.predict)

        
        self.prediction_graph_frame = tk.Frame(self.prediction_frame, bg="#457EAC", padx=20, pady=20)
        self.prediction_graph_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)


    """Logic for prediction with ML models"""
    def predict(self):
        valor = self.comboBox.get()
        steps = int(valor)
        threading.Thread(target=self.run_prediction(steps,)).start()
    
    """Logic for predictions with ML models with selected number of minutes = steps"""
    def run_prediction(self, steps):
            
        self.controller.fitbitAPI.perfectDataForPrediction(steps)
        self.create_prediction_info()
       
    """Logic for resulted prediction graph"""
    def create_prediction_info(self):

        predictions = self.controller.predictions()
        datos_reales = self.controller.datosReales()
        
        self.graphPredictions(datos_reales, predictions)
       
    """Creation of Predictions graph"""
    def graphPredictions(self, datos_reales, predictions):
        if self.current_prediction_canvas:
            self.current_prediction_canvas.get_tk_widget().destroy()
        
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)

        ax.plot(datos_reales.index, datos_reales, label='Datos Reales', marker='o')
        ax.plot(predictions.index, predictions, label='Predicciones', linestyle='--', marker='x')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  
        fig.autofmt_xdate() 

        ax.set_xlabel('Tiempo')
        ax.set_ylabel('HeartRate')
        ax.set_title('Predicciones')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=self.prediction_graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        self.current_prediction_canvas = canvas
    
    """Logic for updating/syncronized with latest user data"""
    def update_status(self):
        
        self.progress_popup = tk.Toplevel(self)
        self.progress_popup.title("Sincronizando...")
        self.progress_popup.geometry("300x100")

        progress_label = tk.Label(self.progress_popup, text="Sincronizando...", font=("Arial", 14))
        progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.progress_popup, orient='horizontal', mode='determinate', length=200)
        self.progress_bar.pack(pady=5)

        threading.Thread(target=self.run_update_status_with_progress).start()

    """Logic for running on thread update/syncronize logic"""
    def run_update_status_with_progress(self):
        try:
            self.update_progress(2) 
            self.ult_act = self.controller.checkLasUpdate() 
            self.update_progress(25)

            if not self.ult_act:
                dates = self.get_last_30_days()
            else:
                dates = self.get_dates_since_last_activity(self.ult_act)

            remainingRequest = self.controller.fitbitAPI.get_remaining_requests()
            print(f"Remaining request [before] calling the data: {remainingRequest}")
            self.controller.fitbitAPI.getHeartRateData("1min", "00:00", "23:59", dates)
            self.update_progress(30) 
            self.controller.fitbitAPI.getCaloriesDistanceStepsData("1min", "00:00", "23:59", dates)
            self.update_progress(75)
            self.controller.fitbitAPI.dataPreprocess()
            self.update_progress(100) 
            remainingRequest = self.controller.fitbitAPI.get_remaining_requests()
            print(f"Remaining request [after] calling the data: {remainingRequest}")

            
            self.controller.updateApi_lastUpdate()
            self.ult_act = self.controller.checkLasUpdate()

            if self.update_label :
               last_update = self.ult_act.strftime("%A, %d de %B de %Y a las %H:%M:%S")
               self.update_label.config(text=f"Última Sincronización: {last_update}")

        finally:
            self.progress_popup.destroy()


    """Logic for updating progress syncroniz bar"""
    def update_progress(self, value):
        self.progress_bar['value'] = value
        self.progress_popup.update_idletasks()

    """Logic for get last 30 day from actual date"""
    def get_last_30_days(self):
        today = datetime.today()
        start_date = today - timedelta(days=30)
        return [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(31)]
   
    """Logic for getting days passed since last updated/syncronize"""
    def get_dates_since_last_activity(self, ult_act):
        last_activity_date = ult_act  
        today = datetime.today()
        days_diff = (today - last_activity_date).days
        return [(last_activity_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_diff + 1)]
    

    """Logic for creation of ReAuthoritazion PopUp with FitBit"""
    def reauthorizationPopup(self):
        
        self.popup = tk.Toplevel(self)
        self.popup.title("Re-authorization Requerida")
        self.popup.geometry("400x150")

        message_label = tk.Label(self.popup, text="Tu token de autorización ha expirado.\nPor favor, re-autoriza con tu cuenta Fitbit.")
        message_label.pack(pady=10)

        reauthorize_button = tk.Button(self.popup, text="Re-autorizar", command=self.authorize_with_fitbit)
        reauthorize_button.pack(pady=10)
    
    """Logic for user authorize with FitBit"""
    def authorize_with_fitbit(self):
        try :    

            self.user = "scriptUser"
            self.email = "scriptUser@gmail.com"
            self.password= "notEvenASecretPass!"
            self.age = "22"
             
            if self.register_frame :   

                self.user = self.register_user_entry.get()
                self.email = self.register_email_entry.get()
                self.password = self.register_password_entry.get()
                self.age = self.age_entry.get()   
           
            self.authoritize(self.user, self.email, self.password, self.age)

        except UserRegistrationError as e:   
            self.show_error_message(self.register_frame, e.getMessage())
            return False      
        
    """Logic for user authorize with FitBit"""
    def authoritize(self, user, email, password, age):
        self.is_authorized = self.controller.authorize_with_fitbit(user, email, password, age)

        if self.popup :
            self.popup.destroy()
        if self.is_authorized:
            if self.authorize_fitbit_button:
                self.authorize_fitbit_button.config(state="disabled")
                self.authorize_label_var.set("✓")
                self.register_button.config(state="normal")

        