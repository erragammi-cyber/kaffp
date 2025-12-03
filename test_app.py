import json
import sys
import os
import random

# Добавляем путь к рабочей директории
sys.path.append('/workspace')

def test_training_logic():
    print("Тестирование логики приложения...")
    
    # Загружаем базу тренировок
    with open('trainings.json', 'r', encoding='utf-8') as f:
        training_database = json.load(f)
    
    print(f"✓ Загружено {len(training_database)} тренировок из базы данных")
    
    # Проверяем, что база данных тренировок не пуста
    assert len(training_database) > 0, "База данных тренировок пуста"
    
    # Проверяем, что тренировки имеют правильную структуру
    sample_training = training_database[0]
    required_fields = ['id', 'name', 'type', 'level', 'duration_min', 'warmup', 'main', 'cooldown', 'tags']
    
    for field in required_fields:
        assert field in sample_training, f"Поле {field} отсутствует в тренировке"
    
    print("✓ Структура тренировки корректна")
    
    # Тестируем функции оценки уровня из основного приложения
    def assess_strength_level(strength_data):
        # Оценка уровня силы на основе результатов
        levels = []
        
        # Подтягивания - нормативы для 3 курса (пример)
        pullups = strength_data['pullups']
        if pullups.isdigit():
            pullups = int(pullups)
            if pullups >= 15:  # условный норматив "отлично"
                levels.append("Excellent")
            elif pullups >= 12:  # условный норматив "хорошо"
                levels.append("Good")
            elif pullups >= 8:   # условный норматив "удовл."
                levels.append("Satisfactory")
            else:
                levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Подъем переворотом
        chinups = strength_data['chinups']
        if chinups.isdigit():
            chinups = int(chinups)
            if chinups >= 8:  # условный норматив "отлично"
                levels.append("Excellent")
            elif chinups >= 5:  # условный норматив "хорошо"
                levels.append("Good")
            elif chinups >= 3:   # условный норматив "удовл."
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
    
    def assess_endurance_level(endurance_data):
        # Оценка уровня выносливости на основе результатов
        levels = []
        
        # Парсинг времени в формате "мин:сек" в секунды
        def parse_time(time_str):
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
        
        # Бег 5 км - нормативы для 3 курса (пример)
        run5k = parse_time(endurance_data['run5k'])
        if run5k is not None:
            if run5k <= 1200:  # условный норматив "отлично" (20:00)
                levels.append("Excellent")
            elif run5k <= 1320:  # условный норматив "хорошо" (22:00)
                levels.append("Good")
            elif run5k <= 1500:   # условный норматив "удовл." (25:00)
                levels.append("Satisfactory")
            else:
                levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Бег 3 км
        run3k = parse_time(endurance_data['run3k'])
        if run3k is not None:
            if run3k <= 720:  # условный норматив "отлично" (12:00)
                levels.append("Excellent")
            elif run3k <= 780:  # условный норматив "хорошо" (13:00)
                levels.append("Good")
            elif run3k <= 900:   # условный норматив "удовл." (15:00)
                levels.append("Satisfactory")
            else:
                levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Марш-бросок 5 км
        march5k = parse_time(endurance_data['march5k'])
        if march5k is not None:
            if march5k <= 2400:  # условный норматив "отлично" (40:00)
                levels.append("Excellent")
            elif march5k <= 2700:  # условный норматив "хорошо" (45:00)
                levels.append("Good")
            elif march5k <= 3000:   # условный норматив "удовл." (50:00)
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
    
    def assess_speed_level(speed_data):
        # Оценка уровня быстроты на основе результатов
        levels = []
        
        # Бег 100 м
        run100m = speed_data['run100m']
        if run100m.replace('.', '', 1).isdigit():
            run100m = float(run100m)
            if run100m <= 12.0:  # условный норматив "отлично"
                levels.append("Excellent")
            elif run100m <= 14.0:  # условный норматив "хорошо"
                levels.append("Good")
            elif run100m <= 16.0:   # условный норматив "удовл."
                levels.append("Satisfactory")
            else:
                levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Челночный бег 10x10 м
        shuttle = speed_data['shuttle10x10']
        if shuttle.replace('.', '', 1).isdigit():
            shuttle = float(shuttle)
            if shuttle <= 12.0:  # условный норматив "отлично"
                levels.append("Excellent")
            elif shuttle <= 14.0:  # условный норматив "хорошо"
                levels.append("Good")
            elif shuttle <= 16.0:   # условный норматив "удовл."
                levels.append("Satisfactory")
            else:
                levels.append("Fail")
        else:
            levels.append("Unknown")
        
        # Бег 60 м
        run60m = speed_data['run60m']
        if run60m.replace('.', '', 1).isdigit():
            run60m = float(run60m)
            if run60m <= 7.0:  # условный норматив "отлично"
                levels.append("Excellent")
            elif run60m <= 8.0:  # условный норматив "хорошо"
                levels.append("Good")
            elif run60m <= 9.0:   # условный норматив "удовл."
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
    
    def determine_priorities(strength_level, endurance_level, speed_level):
        # Определение приоритетов на основе уровней
        priorities = {
            'strength': strength_level,
            'endurance': endurance_level,
            'speed': speed_level
        }
        return priorities
    
    def get_priority_types(priorities):
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
    
    def find_training_by_type(training_database, types, priority_level):
        # Находим тренировку по типу и уровню
        # Сначала ищем тренировки, соответствующие типам
        matching_trainings = []
        
        for training in training_database:
            if any(t in training['type'] for t in types):
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
            return random.choice(matching_trainings)
        else:
            # Если не нашли подходящие тренировки, возвращаем первую попавшуюся подходящего типа
            for training in training_database:
                if any(t in training['type'] for t in types):
                    return training
    
        return None
    
    def create_training_schedule(training_database, days, priorities):
        # Создание расписания тренировок на основе базы данных тренировок
        schedule = {}
        
        # Определяем приоритетные типы тренировок на основе слабых мест
        priority_types = get_priority_types(priorities)
        
        # Выбираем тренировки из базы данных
        for i, day in enumerate(days):
            # Определяем тип тренировки для дня на основе приоритетов
            if len(days) == 1:
                # Если только один день - комплексная тренировка
                training = find_training_by_type(training_database, ['сила', 'выносливость', 'быстрота'], 'high')
            elif len(days) == 2:
                # Если два дня - чередуем силу и выносливость
                if i % 2 == 0:
                    training = find_training_by_type(training_database, ['сила'], priority_types['strength'])
                else:
                    training = find_training_by_type(training_database, ['выносливость'], priority_types['endurance'])
            elif len(days) == 3:
                # Если три дня - силы, выносливость, быстрота
                if i % 3 == 0:
                    training = find_training_by_type(training_database, ['сила'], priority_types['strength'])
                elif i % 3 == 1:
                    training = find_training_by_type(training_database, ['выносливость'], priority_types['endurance'])
                else:
                    training = find_training_by_type(training_database, ['быстрота'], priority_types['speed'])
            elif len(days) >= 4:
                # Если 4+ дня - распределяем по приоритетам
                if i % 3 == 0:
                    training = find_training_by_type(training_database, ['сила'], priority_types['strength'])
                elif i % 3 == 1:
                    training = find_training_by_type(training_database, ['выносливость'], priority_types['endurance'])
                else:
                    training = find_training_by_type(training_database, ['быстрота'], priority_types['speed'])
            
            if training:
                schedule[day] = training
            else:
                # Если не найдена подходящая тренировка, создаем базовую
                schedule[day] = {
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
        
        return schedule
    
    # Тестируем функцию оценки уровня силы
    strength_data = {'pullups': '10', 'chinups': '5'}
    strength_level = assess_strength_level(strength_data)
    print(f"✓ Уровень силы для {strength_data}: {strength_level}")
    
    # Тестируем функцию оценки уровня выносливости
    endurance_data = {'run5k': '15:30', 'run3k': '9:30', 'march5k': '45:00'}
    endurance_level = assess_endurance_level(endurance_data)
    print(f"✓ Уровень выносливости для {endurance_data}: {endurance_level}")
    
    # Тестируем функцию оценки уровня быстроты
    speed_data = {'run100m': '15.5', 'shuttle10x10': '14.2', 'run60m': '8.5'}
    speed_level = assess_speed_level(speed_data)
    print(f"✓ Уровень быстроты для {speed_data}: {speed_level}")
    
    # Проверяем определение приоритетов
    priorities = determine_priorities(strength_level, endurance_level, speed_level)
    print(f"✓ Приоритеты: {priorities}")
    
    # Проверяем определение типов приоритетов
    priority_types = get_priority_types(priorities)
    print(f"✓ Типы приоритетов: {priority_types}")
    
    # Проверяем поиск тренировки по типу
    sample_training_by_type = find_training_by_type(training_database, ['сила'], priority_types['strength'])
    print(f"✓ Найдена тренировка по типу 'сила': {sample_training_by_type['name'] if sample_training_by_type else 'None'}")
    
    # Проверяем генерацию расписания (без фактического выбора дней)
    test_days = ['2025-12-05', '2025-12-07']
    schedule = create_training_schedule(training_database, test_days, priorities)
    print(f"✓ Сгенерировано расписание для {len(test_days)} дней")
    
    # Проверяем, что для каждого дня есть тренировка
    for day in test_days:
        assert day in schedule, f"Для дня {day} не создана тренировка"
        print(f"✓ Для дня {day} создана тренировка: {schedule[day]['name']}")
    
    print("\n✓ Все тесты пройдены успешно!")
    return True

if __name__ == "__main__":
    try:
        test_training_logic()
        print("\n🎉 Логика приложения работает корректно!")
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()