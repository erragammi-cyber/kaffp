import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import calendar
from datetime import datetime
from tkcalendar import Calendar
import json

class FitnessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Будь первым!")
        self.root.geometry("800x600")
        
        # Загружаем базу тренировок
        self.load_trainings()
        
        # Основные переменные
        self.course = tk.StringVar()
        self.selected_days = []
        self.trainings = {}
        self.completed_trainings = set()  # Отслеживание выполненных тренировок
        self.params_changed = False  # Флаг изменения параметров
        
        # Создаем главные фреймы
        self.create_widgets()
        
    def load_trainings(self):
        """Загрузка базы тренировок из JSON файла"""
        try:
            with open('trainings.json', 'r', encoding='utf-8') as f:
                self.training_database = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Файл trainings.json не найден!")
            self.training_database = []
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл trainings.json поврежден!")
            self.training_database = []
    
    def create_widgets(self):
        # Создаем ноутбук для вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка выбора параметров
        self.setup_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_frame, text="Настройки")
        
        # Вкладка предстоящих тренировок
        self.schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_frame, text="Предстоящие тренировки")
        
        # Создаем фреймы с прокруткой
        self.create_scrollable_frames()
        
        # Настройка параметров
        self.setup_parameters()
        
        # Настройка календаря
        self.setup_calendar()
        
        # Настройка вкладки тренировок
        self.setup_schedule_tab()
        
    def create_scrollable_frames(self):
        # Создаем фреймы с прокруткой
        self.setup_canvas = tk.Canvas(self.setup_frame)
        self.setup_scrollbar = ttk.Scrollbar(self.setup_frame, orient="vertical", command=self.setup_canvas.yview)
        self.setup_scrollable_frame = ttk.Frame(self.setup_canvas)
        
        self.setup_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.setup_canvas.configure(scrollregion=self.setup_canvas.bbox("all"))
        )
        
        self.setup_canvas.create_window((0, 0), window=self.setup_scrollable_frame, anchor="nw")
        self.setup_canvas.configure(yscrollcommand=self.setup_scrollbar.set)
        
        self.setup_canvas.pack(side="left", fill="both", expand=True)
        self.setup_scrollbar.pack(side="right", fill="y")
        
        # Привязываем колесико мыши к прокрутке
        self.setup_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Для вкладки тренировок
        self.schedule_canvas = tk.Canvas(self.schedule_frame)
        self.schedule_scrollbar = ttk.Scrollbar(self.schedule_frame, orient="vertical", command=self.schedule_canvas.yview)
        self.schedule_scrollable_frame = ttk.Frame(self.schedule_canvas)
        
        self.schedule_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
        )
        
        self.schedule_canvas.create_window((0, 0), window=self.schedule_scrollable_frame, anchor="nw")
        self.schedule_canvas.configure(yscrollcommand=self.schedule_scrollbar.set)
        
        self.schedule_canvas.pack(side="left", fill="both", expand=True)
        self.schedule_scrollbar.pack(side="right", fill="y")
        
        # Привязываем колесико мыши к прокрутке
        self.schedule_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        # Обработка прокрутки колесиком мыши
        canvas = event.widget
        if isinstance(canvas, tk.Canvas):
            if event.delta:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.num == 4:  # Linux
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:  # Linux
                canvas.yview_scroll(1, "units")
        
    def setup_parameters(self):
        # Заголовок
        title_label = ttk.Label(self.setup_scrollable_frame, text="Будь первым!", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Выбор курса
        course_frame = ttk.LabelFrame(self.setup_scrollable_frame, text="Выберите курс обучения", padding=10)
        course_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.course_var = tk.StringVar(value="1")
        courses = [("1", 1), ("2", 2), ("3-5", 3)]
        
        for text, value in courses:
            rb = ttk.Radiobutton(course_frame, text=text, variable=self.course_var, value=value)
            rb.pack(anchor=tk.W, pady=2)
        
        # Ввод параметров
        params_frame = ttk.LabelFrame(self.setup_scrollable_frame, text="Введите Ваши параметры по основным нормативам", padding=10)
        params_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Сила
        strength_frame = ttk.LabelFrame(params_frame, text="Сила", padding=10)
        strength_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(strength_frame, text="Подтягивания:").pack(anchor=tk.W)
        self.pullups_entry = ttk.Entry(strength_frame)
        self.pullups_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.pullups_entry.bind('<KeyRelease>', self.on_params_change)
        
        ttk.Label(strength_frame, text="Подъем переворотом:").pack(anchor=tk.W, pady=(10,0))
        self.chinups_entry = ttk.Entry(strength_frame)
        self.chinups_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.chinups_entry.bind('<KeyRelease>', self.on_params_change)
        
        # Выносливость
        endurance_frame = ttk.LabelFrame(params_frame, text="Выносливость", padding=10)
        endurance_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(endurance_frame, text="Бег на 5 километров (мин:сек):").pack(anchor=tk.W)
        self.run5k_entry = ttk.Entry(endurance_frame)
        self.run5k_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.run5k_entry.bind('<KeyRelease>', self.on_params_change)
        
        ttk.Label(endurance_frame, text="Бег на 3 километра (мин:сек):").pack(anchor=tk.W, pady=(10,0))
        self.run3k_entry = ttk.Entry(endurance_frame)
        self.run3k_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.run3k_entry.bind('<KeyRelease>', self.on_params_change)
        
        ttk.Label(endurance_frame, text="Марш-бросок на 5 километров (мин:сек):").pack(anchor=tk.W, pady=(10,0))
        self.march5k_entry = ttk.Entry(endurance_frame)
        self.march5k_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.march5k_entry.bind('<KeyRelease>', self.on_params_change)
        
        # Быстрота
        speed_frame = ttk.LabelFrame(params_frame, text="Быстрота", padding=10)
        speed_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(speed_frame, text="Бег на 100 метров (сек):").pack(anchor=tk.W)
        self.run100m_entry = ttk.Entry(speed_frame)
        self.run100m_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.run100m_entry.bind('<KeyRelease>', self.on_params_change)
        
        ttk.Label(speed_frame, text="Челночный бег 10 х 10 метров (сек):").pack(anchor=tk.W, pady=(10,0))
        self.shuttle10x10_entry = ttk.Entry(speed_frame)
        self.shuttle10x10_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.shuttle10x10_entry.bind('<KeyRelease>', self.on_params_change)
        
        ttk.Label(speed_frame, text="Бег на 60 метров (сек):").pack(anchor=tk.W, pady=(10,0))
        self.run60m_entry = ttk.Entry(speed_frame)
        self.run60m_entry.pack(fill=tk.X, pady=2)
        # Привязываем событие изменения к обновлению расписания
        self.run60m_entry.bind('<KeyRelease>', self.on_params_change)
        
    def setup_calendar(self):
        # Календарь
        calendar_frame = ttk.LabelFrame(self.setup_scrollable_frame, text="Выберите дни тренировок", padding=10)
        calendar_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Создаем календарь
        self.cal = Calendar(calendar_frame, selectmode='day', year=datetime.now().year, month=datetime.now().month)
        self.cal.pack(pady=10)
        
        # Кнопка подтверждения выбора
        confirm_button = ttk.Button(calendar_frame, text="Подтвердить выбор дней", command=self.confirm_days)
        confirm_button.pack(pady=10)
        
        # Метки для выбранных дней
        self.selected_days_label = ttk.Label(calendar_frame, text="Выбранные дни: Нет")
        self.selected_days_label.pack(pady=5)
        
        # Привязываем событие выбора даты
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        
    def on_params_change(self, event=None):
        """Обновление расписания при изменении параметров"""
        # Помечаем, что параметры изменились и нужно обновить тренировки при следующей генерации
        self.params_changed = True
        
        # Обновляем расписание, если уже были выбраны дни
        if self.selected_days and self.trainings:
            # Перегенерируем тренировки на основе новых параметров
            self.generate_trainings()
    
    def setup_schedule_tab(self):
        # Заголовок вкладки тренировок
        title_label = ttk.Label(self.schedule_scrollable_frame, text="Предстоящие тренировки", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Инструкция
        instruction_label = ttk.Label(self.schedule_scrollable_frame, 
                                    text="Выберите дни тренировок во вкладке 'Настройки' для отображения тренировок")
        instruction_label.pack(pady=10)
        
        # Кнопка обновления
        refresh_button = ttk.Button(self.schedule_scrollable_frame, text="Обновить", command=self.refresh_schedule)
        refresh_button.pack(pady=10)
        
        # Кнопка генерации тренировок
        generate_button = ttk.Button(self.schedule_scrollable_frame, text="Сгенерировать тренировки", command=self.generate_trainings)
        generate_button.pack(pady=10)
        
    def on_date_select(self, event):
        selected_date = self.cal.get_date()
        if selected_date not in self.selected_days:
            self.selected_days.append(selected_date)
        else:
            self.selected_days.remove(selected_date)
        
        self.update_selected_days_label()
        
    def confirm_days(self):
        # Подтверждение выбора дней
        self.update_selected_days_label()
        messagebox.showinfo("Подтверждение", f"Выбранные дни: {', '.join(self.selected_days)}")
        
    def update_selected_days_label(self):
        if self.selected_days:
            self.selected_days_label.config(text=f"Выбранные дни: {', '.join(self.selected_days)}")
        else:
            self.selected_days_label.config(text="Выбранные дни: Нет")
            
    def refresh_schedule(self):
        # Очищаем предыдущие элементы
        for widget in self.schedule_scrollable_frame.winfo_children():
            if widget.winfo_y() > 100:  # Сохраняем заголовок и кнопки
                widget.destroy()
        
        # Показываем тренировки для выбранных дней
        if self.selected_days:
            for day in self.selected_days:
                self.add_training_card(day)
        else:
            no_trainings_label = ttk.Label(self.schedule_scrollable_frame, 
                                         text="Нет выбранных дней тренировок. Перейдите во вкладку 'Настройки'.")
            no_trainings_label.pack(pady=20)
    
    def add_training_card(self, day):
        # Создаем карточку тренировки в стиле iOS
        card_frame = ttk.Frame(self.schedule_scrollable_frame, relief=tk.RAISED, borderwidth=2)
        card_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Заголовок с датой
        date_label = ttk.Label(card_frame, text=f"Тренировка на {day}", font=("Arial", 12, "bold"))
        date_label.pack(pady=5)
        
        # Проверяем, есть ли тренировка для этого дня
        if day in self.trainings:
            training_info = self.trainings[day]
            training_label = ttk.Label(card_frame, text=training_info['name'], wraplength=400)
            training_label.pack(pady=5)
            
            # Проверяем статус выполнения
            if day in self.completed_trainings:
                status_label = ttk.Label(card_frame, text="✓ Выполнено", foreground="green", font=("Arial", 10, "bold"))
                status_label.pack(pady=2)
                card_frame.configure(relief=tk.FLAT, borderwidth=0)
            else:
                status_label = ttk.Label(card_frame, text="Не выполнено", foreground="red", font=("Arial", 10))
                status_label.pack(pady=2)
        else:
            no_training_label = ttk.Label(card_frame, text="Тренировка пока не назначена", 
                                        foreground="gray")
            no_training_label.pack(pady=5)
        
        # Кнопка для подробного просмотра
        details_button = ttk.Button(card_frame, text="Подробнее", 
                                  command=lambda d=day: self.show_training_details(d))
        details_button.pack(pady=5)
        
    def show_training_details(self, day):
        # Проверяем, есть ли тренировка для этого дня
        if day not in self.trainings:
            messagebox.showwarning("Предупреждение", "Для этого дня не назначена тренировка.")
            return
            
        # Создаем новое окно с деталями тренировки
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Детали тренировки - {day}")
        details_window.geometry("600x700")
        
        # Создаем фрейм с прокруткой
        canvas = tk.Canvas(details_window)
        scrollbar = ttk.Scrollbar(details_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Привязываем колесико мыши к прокрутке
        canvas.bind("<MouseWheel>", self._on_mousewheel_popup)
        # Для Linux
        canvas.bind("<Button-4>", self._on_mousewheel_popup)
        canvas.bind("<Button-5>", self._on_mousewheel_popup)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        title_label = ttk.Label(scrollable_frame, text=f"{self.trainings[day]['name']}", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Информация о тренировке
        training_info = self.trainings[day]
        
        # Основная информация
        info_frame = ttk.Frame(scrollable_frame)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(info_frame, text=f"Тип: {', '.join(training_info['type'])}", font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Уровень: {training_info['level']}", font=("Arial", 10)).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Длительность: {training_info['duration_min']} мин", font=("Arial", 10)).pack(anchor=tk.W)
        
        # Разминка
        warmup_frame = ttk.LabelFrame(scrollable_frame, text="Разминка", padding=10)
        warmup_frame.pack(fill=tk.X, padx=20, pady=10)
        
        warmup_text = tk.Text(warmup_frame, wrap=tk.WORD, height=4, padx=10, pady=10)
        warmup_text.insert(tk.END, training_info['warmup'])
        warmup_text.config(state=tk.DISABLED)
        warmup_text.pack(fill=tk.X)
        
        # Основная часть
        main_frame = ttk.LabelFrame(scrollable_frame, text="Основная часть", padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        main_text = tk.Text(main_frame, wrap=tk.WORD, padx=10, pady=10)
        
        # Форматируем упражнения
        for exercise in training_info['main']:
            exercise_text = f"• {exercise['exercise']}: "
            if isinstance(exercise['reps'], str):
                exercise_text += f"{exercise['sets']} подхода по {exercise['reps']} повторений"
            else:
                exercise_text += f"{exercise['sets']} подхода по {exercise['reps']} повторений"
                
            if exercise['rest_sec'] > 0:
                exercise_text += f" (отдых {exercise['rest_sec']} сек)"
            exercise_text += "\n"
            
            main_text.insert(tk.END, exercise_text)
        
        main_text.config(state=tk.DISABLED)
        main_text.pack(fill=tk.BOTH, expand=True)
        
        # Заминка
        cooldown_frame = ttk.LabelFrame(scrollable_frame, text="Заминка", padding=10)
        cooldown_frame.pack(fill=tk.X, padx=20, pady=10)
        
        cooldown_text = tk.Text(cooldown_frame, wrap=tk.WORD, height=4, padx=10, pady=10)
        cooldown_text.insert(tk.END, training_info['cooldown'])
        cooldown_text.config(state=tk.DISABLED)
        cooldown_text.pack(fill=tk.X)
        
        # Кнопка "Выполнено"
        complete_button = ttk.Button(scrollable_frame, text="Выполнено", 
                                   command=lambda: self.mark_training_completed(day, details_window))
        complete_button.pack(pady=20)
        
        # Также привязываем колесико мыши к основному фрейму для прокрутки
        scrollable_frame.bind("<MouseWheel>", self._on_mousewheel_popup)
        scrollable_frame.bind("<Button-4>", self._on_mousewheel_popup)
        scrollable_frame.bind("<Button-5>", self._on_mousewheel_popup)
    
    def _on_mousewheel_popup(self, event):
        # Обработка прокрутки колесиком мыши в popup окне
        if event.delta:
            self.focus_set()  # Устанавливаем фокус на окно
            event.widget.master.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:  # Linux
            event.widget.master.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux
            event.widget.master.yview_scroll(1, "units")
        
    def mark_training_completed(self, day, window):
        # Отмечаем тренировку как выполненную
        self.completed_trainings.add(day)
        window.destroy()
        self.refresh_schedule()  # Обновляем отображение
        
    def get_user_data(self):
        # Собираем данные пользователя
        data = {
            'course': self.course_var.get(),
            'strength': {
                'pullups': self.pullups_entry.get(),
                'chinups': self.chinups_entry.get()
            },
            'endurance': {
                'run5k': self.run5k_entry.get(),
                'run3k': self.run3k_entry.get(),
                'march5k': self.march5k_entry.get()
            },
            'speed': {
                'run100m': self.run100m_entry.get(),
                'shuttle10x10': self.shuttle10x10_entry.get(),
                'run60m': self.run60m_entry.get()
            },
            'selected_days': self.selected_days
        }
        return data

    def generate_trainings(self):
        # Генерация тренировок на основе введенных данных
        user_data = self.get_user_data()
        
        if not user_data['selected_days']:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите дни тренировок.")
            return
        
        # Оценка уровня по каждому качеству
        strength_level = self.assess_strength_level(user_data['strength'])
        endurance_level = self.assess_endurance_level(user_data['endurance'])
        speed_level = self.assess_speed_level(user_data['speed'])
        
        # Выводим сообщение пользователю в зависимости от его уровня
        self.show_level_message(strength_level, endurance_level, speed_level)
        
        # Определение приоритетов
        priorities = self.determine_priorities(strength_level, endurance_level, speed_level)
        
        # Генерация тренировок для каждого дня
        self.trainings = self.create_training_schedule(user_data['selected_days'], priorities)
        
        # Сбрасываем флаг изменений параметров
        self.params_changed = False
        
        # Обновление вкладки тренировок
        self.refresh_schedule()
        
        messagebox.showinfo("Генерация", "Тренировки успешно сгенерированы!")
    
    def show_level_message(self, strength_level, endurance_level, speed_level):
        # Определяем общий уровень
        levels = [strength_level, endurance_level, speed_level]
        
        # Проверяем, все ли уровни "Excellent"
        if all(level == "Excellent" for level in levels):
            message = "Поздравляем! У вас отличные результаты по всем параметрам. Продолжайте в том же духе!"
            messagebox.showinfo("Уровень подготовки", message)
        else:
            # Определяем слабые места
            weak_areas = []
            if strength_level in ["Fail", "Satisfactory"]:
                weak_areas.append("силовые качества")
            if endurance_level in ["Fail", "Satisfactory"]:
                weak_areas.append("выносливость")
            if speed_level in ["Fail", "Satisfactory"]:
                weak_areas.append("быстрота")
                
            if weak_areas:
                message = f"Вам стоит уделить больше внимания следующим аспектам: {', '.join(weak_areas)}. Приложение сгенерирует тренировки с акцентом на развитие этих качеств."
                messagebox.showinfo("Уровень подготовки", message)
    
    def assess_strength_level(self, strength_data):
        # Оценка уровня силы на основе результатов
        levels = []
        
        # Получаем номер курса
        course = int(self.course_var.get())
        
        # Подтягивания - точные нормативы
        pullups = strength_data['pullups']
        if pullups.isdigit():
            pullups = int(pullups)
            if course == 1:
                if pullups >= 13:  # Отл – 13 раз
                    levels.append("Excellent")
                elif pullups >= 11:  # Хор – 11 раз
                    levels.append("Good")
                elif pullups >= 9:   # Уд – 9 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if pullups >= 15:  # Отл – 15 раз
                    levels.append("Excellent")
                elif pullups >= 13:  # Хор – 13 раз
                    levels.append("Good")
                elif pullups >= 11:   # Уд – 11 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if pullups >= 16:  # Отл – 16 раз
                    levels.append("Excellent")
                elif pullups >= 14:  # Хор – 14 раз
                    levels.append("Good")
                elif pullups >= 12:   # Уд – 12 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Подъем переворотом - точные нормативы
        chinups = strength_data['chinups']
        if chinups.isdigit():
            chinups = int(chinups)
            if course == 1:
                if chinups >= 7:  # Отл – 7 раз
                    levels.append("Excellent")
                elif chinups >= 6:  # Хор – 6 раз
                    levels.append("Good")
                elif chinups >= 5:   # Уд – 5 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if chinups >= 8:  # Отл – 8 раз
                    levels.append("Excellent")
                elif chinups >= 7:  # Хор – 7 раз
                    levels.append("Good")
                elif chinups >= 6:   # Уд – 6 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if chinups >= 9:  # Отл – 9 раз
                    levels.append("Excellent")
                elif chinups >= 8:  # Хор – 8 раз
                    levels.append("Good")
                elif chinups >= 7:   # Уд – 7 раз
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Определяем общий уровень силы
        if "Fail" in levels:
            return "Fail"
        elif "Satisfactory" in levels:
            return "Satisfactory"
        elif "Good" in levels:
            return "Good"
        else:
            return "Excellent"
    
    def assess_endurance_level(self, endurance_data):
        # Оценка уровня выносливости на основе результатов
        levels = []
        
        # Получаем номер курса
        course = int(self.course_var.get())
        
        # Бег 5 км - точные нормативы
        run5k = self.parse_time(endurance_data['run5k'])
        if run5k is not None:
            if course == 1:
                if run5k <= 1440:  # Отл – 24:00 мин
                    levels.append("Excellent")
                elif run5k <= 1500:  # Хор – 25:00 мин
                    levels.append("Good")
                elif run5k <= 1560:   # Уд – 26:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if run5k <= 1380:  # Отл – 23:00 мин
                    levels.append("Excellent")
                elif run5k <= 1440:  # Хор – 24:00 мин
                    levels.append("Good")
                elif run5k <= 1500:   # Уд – 25:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if run5k <= 1320:  # Отл – 22:00 мин
                    levels.append("Excellent")
                elif run5k <= 1380:  # Хор – 23:00 мин
                    levels.append("Good")
                elif run5k <= 1440:   # Уд – 24:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Бег 3 км - точные нормативы
        run3k = self.parse_time(endurance_data['run3k'])
        if run3k is not None:
            if course == 1:
                if run3k <= 740:  # Отл – 12:20 мин (740 сек)
                    levels.append("Excellent")
                elif run3k <= 755:  # Хор – 12:35 мин (755 сек)
                    levels.append("Good")
                elif run3k <= 790:   # Уд – 13:10 мин (790 сек)
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if run3k <= 730:  # Отл – 12:10 мин (730 сек)
                    levels.append("Excellent")
                elif run3k <= 740:  # Хор – 12:20 мин (740 сек)
                    levels.append("Good")
                elif run3k <= 780:   # Уд – 13:00 мин (780 сек)
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if run3k <= 720:  # Отл – 12:00 мин (720 сек)
                    levels.append("Excellent")
                elif run3k <= 740:  # Хор – 12:20 мин (740 сек)
                    levels.append("Good")
                elif run3k <= 770:   # Уд – 12:50 мин (770 сек)
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Марш-бросок 5 км - нормативы (предположим те же, что и для 5км бега)
        march5k = self.parse_time(endurance_data['march5k'])
        if march5k is not None:
            if course == 1:
                if march5k <= 1440:  # Отл – 24:00 мин
                    levels.append("Excellent")
                elif march5k <= 1500:  # Хор – 25:00 мин
                    levels.append("Good")
                elif march5k <= 1560:   # Уд – 26:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if march5k <= 1380:  # Отл – 23:00 мин
                    levels.append("Excellent")
                elif march5k <= 1440:  # Хор – 24:00 мин
                    levels.append("Good")
                elif march5k <= 1500:   # Уд – 25:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if march5k <= 1320:  # Отл – 22:00 мин
                    levels.append("Excellent")
                elif march5k <= 1380:  # Хор – 23:00 мин
                    levels.append("Good")
                elif march5k <= 1440:   # Уд – 24:00 мин
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Определяем общий уровень выносливости
        if "Fail" in levels:
            return "Fail"
        elif "Satisfactory" in levels:
            return "Satisfactory"
        elif "Good" in levels:
            return "Good"
        else:
            return "Excellent"
    
    def assess_speed_level(self, speed_data):
        # Оценка уровня быстроты на основе результатов
        levels = []
        
        # Получаем номер курса
        course = int(self.course_var.get())
        
        # Бег 100 м - точные нормативы
        run100m = speed_data['run100m']
        if run100m.replace('.', '', 1).isdigit():
            run100m = float(run100m)
            if course == 1:
                if run100m <= 14.2:  # Отл – 14.2 сек
                    levels.append("Excellent")
                elif run100m <= 14.6:  # Хор – 14.6 сек
                    levels.append("Good")
                elif run100m <= 15.6:   # Уд – 15.6 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if run100m <= 14.0:  # Отл – 14.0 сек
                    levels.append("Excellent")
                elif run100m <= 14.4:  # Хор – 14.4 сек
                    levels.append("Good")
                elif run100m <= 15.2:   # Уд – 15.2 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if run100m <= 13.9:  # Отл – 13.9 сек
                    levels.append("Excellent")
                elif run100m <= 14.3:  # Хор – 14.3 сек
                    levels.append("Good")
                elif run100m <= 15.0:   # Уд – 15.0 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Челночный бег 10x10 м - точные нормативы
        shuttle = speed_data['shuttle10x10']
        if shuttle.replace('.', '', 1).isdigit():
            shuttle = float(shuttle)
            if course == 1:
                if shuttle <= 28.0:  # Отл – 28.0 сек
                    levels.append("Excellent")
                elif shuttle <= 28.5:  # Хор – 28.5 сек
                    levels.append("Good")
                elif shuttle <= 29.5:   # Уд – 29.5 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if shuttle <= 27.5:  # Отл – 27.5 сек
                    levels.append("Excellent")
                elif shuttle <= 28.0:  # Хор – 28.0 сек
                    levels.append("Good")
                elif shuttle <= 29.0:   # Уд – 29.0 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if shuttle <= 27.0:  # Отл – 27.0 сек
                    levels.append("Excellent")
                elif shuttle <= 27.5:  # Хор – 27.5 сек
                    levels.append("Good")
                elif shuttle <= 28.5:   # Уд – 28.5 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Бег 60 м - точные нормативы
        run60m = speed_data['run60m']
        if run60m.replace('.', '', 1).isdigit():
            run60m = float(run60m)
            if course == 1:
                if run60m <= 8.7:  # Отл – 8.7 сек
                    levels.append("Excellent")
                elif run60m <= 9.4:  # Хор – 9.4 сек
                    levels.append("Good")
                elif run60m <= 9.8:   # Уд – 9.8 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            elif course == 2:
                if run60m <= 8.6:  # Отл – 8.6 сек
                    levels.append("Excellent")
                elif run60m <= 9.3:  # Хор – 9.3 сек
                    levels.append("Good")
                elif run60m <= 9.7:   # Уд – 9.7 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
            else:  # 3-й и старшие курсы
                if run60m <= 8.4:  # Отл – 8.4 сек
                    levels.append("Excellent")
                elif run60m <= 9.1:  # Хор – 9.1 сек
                    levels.append("Good")
                elif run60m <= 9.5:   # Уд – 9.5 сек
                    levels.append("Satisfactory")
                else:
                    levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Определяем общий уровень быстроты
        if "Fail" in levels:
            return "Fail"
        elif "Satisfactory" in levels:
            return "Satisfactory"
        elif "Good" in levels:
            return "Good"
        else:
            return "Excellent"
    
    def parse_time(self, time_str):
        # Парсинг времени в формате "мин:сек" в секунды
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                minutes = int(parts[0])
                seconds = int(parts[1])
                return minutes * 60 + seconds
            except:
                return None
        elif time_str.replace('.', '', 1).isdigit():
            # Если время в секундах
            return float(time_str)
        else:
            return None
    
    def determine_priorities(self, strength_level, endurance_level, speed_level):
        # Определение приоритетов на основе уровней
        priorities = {
            'strength': strength_level,
            'endurance': endurance_level,
            'speed': speed_level
        }
        return priorities
    
    def create_training_schedule(self, days, priorities):
        # Создание расписания тренировок на основе базы данных тренировок
        schedule = {}
        
        # Проверяем, все ли качества на уровне "Excellent"
        all_excellent = all(level == "Excellent" for level in priorities.values())
        
        # Определяем приоритетные типы тренировок на основе слабых мест
        priority_types = self.get_priority_types(priorities)
        
        # Выбираем тренировки из базы данных
        for i, day in enumerate(days):
            # Если все качества "Excellent", включаем поддерживающие тренировки
            if all_excellent and len(days) > 1:
                # Каждая третья тренировка может быть поддерживающей
                if i % 3 == 0:  # Пример: чередуем основные и поддерживающие
                    training = self.find_training_by_tags(['поддерживающая'])
                else:
                    training = self.find_training_by_type(['сила', 'выносливость', 'быстрота'], "low")
            else:
                # Определяем тип тренировки для дня на основе приоритетов
                if len(days) == 1:
                    # Если только один день - комплексная тренировка
                    training = self.find_training_by_tags(['комплекс', 'тест'])
                elif len(days) == 2:
                    # Если два дня - чередуем силу и выносливость
                    if i % 2 == 0:
                        training = self.find_training_by_type(['сила'], priority_types['strength'])
                    else:
                        training = self.find_training_by_type(['выносливость'], priority_types['endurance'])
                elif len(days) == 3:
                    # Если три дня - силы, выносливость, быстрота
                    if i % 3 == 0:
                        training = self.find_training_by_type(['сила'], priority_types['strength'])
                    elif i % 3 == 1:
                        training = self.find_training_by_type(['выносливость'], priority_types['endurance'])
                    else:
                        training = self.find_training_by_type(['быстрота'], priority_types['speed'])
                elif len(days) >= 4:
                    # Если 4+ дня - распределяем по приоритетам
                    if i % 3 == 0:
                        training = self.find_training_by_type(['сила'], priority_types['strength'])
                    elif i % 3 == 1:
                        training = self.find_training_by_type(['выносливость'], priority_types['endurance'])
                    else:
                        training = self.find_training_by_type(['быстрота'], priority_types['speed'])
            
            if training:
                schedule[day] = training
            else:
                # Если не найдена подходящая тренировка, создаем базовую
                schedule[day] = self.get_default_training()
        
        return schedule
    
    def get_priority_types(self, priorities):
        # Определяем приоритеты по типам тренировок
        priority_types = {}
        
        # Для каждого типа определяем уровень приоритета
        for quality, level in priorities.items():
            if level in ["Fail", "Satisfactory"]:
                priority_types[quality] = "high"  # Высокий приоритет для развития
            elif level == "Good":
                priority_types[quality] = "medium"  # Средний приоритет
            else:  # Excellent
                priority_types[quality] = "low"  # Низкий приоритет
    
        return priority_types
    
    def find_training_by_type(self, types, priority_level):
        # Находим тренировку по типу и уровню
        # Сначала ищем тренировки, соответствующие типам
        matching_trainings = []
        
        for training in self.training_database:
            if any(t in training['type'] for t in types):
                # Исключаем поддерживающие тренировки, если не ищем их специально
                if "поддерживающая" not in training['tags']:
                    # Учитываем уровень сложности в зависимости от приоритета
                    if priority_level == "high":
                        # Для высокого приоритета выбираем тренировки подходящего уровня или немного выше
                        if training['level'] in ["базовый", "средний"]:
                            matching_trainings.append(training)
                    elif priority_level == "medium":
                        # Для среднего приоритета выбираем тренировки среднего уровня
                        if training['level'] in ["средний"]:
                            matching_trainings.append(training)
                    else:  # low
                        # Для низкого приоритета выбираем тренировки среднего или продвинутого уровня
                        if training['level'] in ["средний", "продвинутый"]:
                            matching_trainings.append(training)
        
        # Если нашли подходящие тренировки, возвращаем случайную
        if matching_trainings:
            import random
            return random.choice(matching_trainings)
        else:
            # Если не нашли подходящие тренировки, возвращаем первую попавшуюся подходящего типа
            for training in self.training_database:
                if any(t in training['type'] for t in types) and "поддерживающая" not in training['tags']:
                    return training
    
        return None
    
    def find_training_by_tags(self, tags):
        # Находим тренировку по тегам
        matching_trainings = []
        for training in self.training_database:
            if any(tag in training['tags'] for tag in tags):
                matching_trainings.append(training)
        
        # Если нашли подходящие тренировки, возвращаем случайную
        if matching_trainings:
            import random
            return random.choice(matching_trainings)
        return None
    
    def get_default_training(self):
        # Возвращаем базовую тренировку по умолчанию
        return {
            "id": "default",
            "name": "Базовая тренировка",
            "type": ["сила", "выносливость"],
            "level": "базовый",
            "duration_min": 45,
            "warmup": "Легкий бег 5 мин, разминка суставов",
            "main": [
                {"exercise": "Приседания", "sets": 3, "reps": 15, "rest_sec": 60},
                {"exercise": "Отжимания", "sets": 3, "reps": 10, "rest_sec": 60},
                {"exercise": "Бег", "sets": 1, "reps": 2000, "rest_sec": 0}  # 2 км
            ],
            "cooldown": "Растяжка мышц",
            "tags": ["база", "вес_тела"]
        }

def main():
    root = tk.Tk()
    app = FitnessApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()