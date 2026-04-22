init python:
    import random
    from abc import ABC, abstractmethod

    class Subject:
        def __init__(self):
            self.observers: list[Observer] = []
        def attach(self, observer):
            if observer not in self.observers:
                self.observers.append(observer)
        def notify(self):
            for observer in self.observers:
                observer.update(self)
    
    class Observer(ABC):
        @abstractmethod
        def update(self, subject: Subject):
            pass

    class Teacher(Subject):
        def __init__(self, name: str):
            Subject.__init__(self)
            self.name: str = name
            self._anger: int = 0

        @property
        def anger(self):
            return self._anger

        @anger.setter
        def anger(self, value: int):
            self._anger = value
            self.notify()

    class Student(Subject):
        def __init__(self, name: str):
            Subject.__init__(self)
            self.name: str = name
            self.vpn: str = "none"
            self.ai_choice: str = "none"
            self.has_code: bool = False
            self.code_quality: str = "none"
            self._stress: int = 0

        @property
        def stress(self):
            return self._stress

        @stress.setter
        def stress(self, value: int):
            self._stress = value
            self.notify()

    class DeathObserver(Observer):
        def __init__(self):
            self.notified_angry: bool = False
            self.notified_furious: bool = False

        def update(self, subject: Teacher):
            if subject.anger >= 8:
                renpy.show("radmir furious")
            elif subject.anger >= 4:
                renpy.show("radmir angry")
            else:
                renpy.show("radmir normal")

            target_music = "audio/lab_main_theme.wav"
            if subject.anger >= 8:
                target_music = "audio/furious.wav"
            elif subject.anger >= 4:
                target_music = "audio/angry.wav"

            if renpy.music.get_playing() != target_music:
                renpy.music.play(target_music, fadein=.3, fadeout=.3)

            if subject.anger >= 10:
                renpy.jump("death_by_anger")
                
            elif subject.anger >= 8 and not self.notified_furious:
                renpy.with_statement(hpunch)
                renpy.notify("БЕГИ, ЭННС!")
                self.notified_furious = True
                
            elif subject.anger >= 4 and not self.notified_angry:
                renpy.notify("Радмир Ренатович начинает закипать...")
                self.notified_angry = True

            if subject.anger < 8:
                self.notified_furious = False
            if subject.anger < 4:
                self.notified_angry = False

    class StressRelay(Observer):
        def __init__(self, student: Student):
            self.student: Student = student

        def update(self, subject):
            self.student.stress = min(subject.anger + random.randint(1, 2), 10)


    def apply_glitch(answers: list[str], stress_level: int):
        if stress_level < 8:
            return answers

        glitched_answers: list[str] = []
        symbols: str = "!@#$%?&*"

        for ans in answers:
            res = ""
            for char in ans:
                if char != " " and random.random() < 0.4:
                    if random.random() < 0.5:
                        res += random.choice(symbols)
                    else:
                        res += char.upper()
                else:
                    res += char
            glitched_answers.append(res)

        return glitched_answers



define e_chan = Character("Рома Эннс", color="#3498db")
define r_chan = Character("Радмир Ренатович", color="#e74c3c")

screen stats_ui(teacher_obj, student_obj):
    frame:
        align (0.95, 0.05)
        vbox:
            text "Ярость Радмира:[teacher_obj.anger]/10" color "#ff0000" size 30
            text "Стресс Ромы: [student_obj.stress]/10" color "#f39c12" size 25

default hint_used = False
default naruto_used = False
default bribe_used = False

default show_hint_highlight = False
default current_correct_index = 0
default current_q_skip_label = ""

screen lifelines():
    zorder 100 
    
    if (not hint_used) or (not naruto_used) or (not bribe_used):
        frame:
            align (0.02, 0.5) 
            background Solid("#f1c40f") 
            padding (2, 2) 
            frame:
                background Solid("#000000cc") 
                padding (15, 20) 
                
                vbox:
                    spacing 25 
                
                    if not hint_used:
                        imagebutton:
                            idle im.MatrixColor(im.Scale("phone_icon.png", 70, 70), im.matrix.brightness(0.3))
                            hover im.MatrixColor(im.Scale("phone_icon.png", 70, 70), im.matrix.brightness(0.5))
                            action[SetVariable("hint_used", True), SetVariable("show_hint_highlight", True)]
                    
                    if not naruto_used:
                        imagebutton:
                            idle im.MatrixColor(im.Scale("naruto_icon.png", 70, 70), im.matrix.brightness(0.3))
                            hover im.MatrixColor(im.Scale("naruto_icon.png", 70, 70), im.matrix.brightness(0.5))
                            action[SetVariable("naruto_used", True), Jump("naruto_action")]
                            
                    if not bribe_used:
                        imagebutton:
                            idle im.MatrixColor(im.Scale("candy_icon.png", 70, 70), im.matrix.brightness(0.3))
                            hover im.MatrixColor(im.Scale("candy_icon.png", 70, 70), im.matrix.brightness(0.5))
                            action [SetVariable("bribe_used", True), Jump("bribe_action")]

    if show_hint_highlight:
        frame:
            align (0.5, 0.1) 
            background Solid("#000000aa")
            padding (2, 2) # Ободок для текста
            frame:
                background Solid("#000000dd")
                padding (15, 10)
                text "Петр незаметно снизу показывает телефон с правильным ответом!" color "#00ff00" size 30 outlines [(2, "#000", 0, 0)]

label start:
    $ enns = Student("Рома")
    $ radmir = Teacher("Радмир Ренатович")

    python:
        radmir.attach(DeathObserver())
        radmir.attach(StressRelay(enns))
    play music "audio/enns_room.wav"
    scene bg room cs at Transform(xsize=config.screen_width, ysize=config.screen_height)
    "Ночь. Рома сидит перед компом и играет в КС с Максимом и Петром."
    voice "audio/ctwin.wav"
    "Игра" "Counter Terrorists Win"
    voice "audio/maxim1.wav"
    "Максим" "Ты сделал лабу по ооап?"
    voice "audio/enns1.wav"
    e_chan "Блиииииин, а что там много делать?"
    voice "audio/maxim2.wav"
    "Максим" "Не мало."
    "Рома решил сесть делать лабу."
    "Ну все мы знаем Рому."
    "Сам он это делать не будет."
    "Рома заходит в HAPP и смотрит на рабочие серверы впн."
    "Тяжелое нынче время."
    menu:
        "Какой VPN включить?"
        "США":
            $ enns.vpn = "usa"
            "Рома включил впн с регионом США."
        "Германия":
            $ enns.vpn = "germany"
            "Рома включил впн с регионом Германия."
        "Не включать":
            $ enns.vpn = "none"
            "Рома не включил впн."

    menu:
        "Какую нейронку выбрать?"
        "DeepSeek":
            $ enns.ai_choice = "deepseek"
            $ enns.has_code = True
            $ enns.code_quality = "mid"
            scene bg room deepseek at Transform(xsize=config.screen_width, ysize=config.screen_height)
            "Рома открыл deepseek."
            "Не плохая нейронка."
            "Спустя полчаса лаба готова."
            "Код выглядит максимально нейронным. Рома даже не почистил коментарии на китайском."
        "Алиса AI":
            scene bg room alice at Transform(xsize=config.screen_width, ysize=config.screen_height)
            $ enns.ai_choice = "alice"
            if enns.vpn != "none":
                $ enns.has_code = False
                voice "audio/enns2.wav"
                e_chan "Алиса, сделай мне лабу по ООАП."
                voice "audio/alice1.wav"
                "Алиса" "Ошибка! Нет доступа к сети."
                "Рома не смог разобраться в проблеме и пошел спать."
            else:
                $ enns.has_code = True
                $ enns.code_quality = "trash"
                voice "audio/enns2.wav"
                e_chan "Алиса, сделай мне лабу по ООАП."
                voice "audio/alice2.wav"
                "Алиса" "Готово вот ваша лабораторная работа по ООАП"
                "Рома даже не запустил сгенерированный код и пошел спать."
        "Gemini":
            scene bg room gemeni at Transform(xsize=config.screen_width, ysize=config.screen_height)
            $ enns.ai_choice = "gemini"
            if enns.vpn == "usa":
                $ enns.has_code = True
                $ enns.code_quality = "top"
                voice "audio/enns3.wav"
                e_chan "Так посмотрим. Сгенерируй мне..."
                "Рома сгенерировал код через Gemeni."
                "Код был довольно не плохой."
            else:
                $ enns.has_code = False
                voice "audio/enns3.wav"
                e_chan "Так посмотрим. Сгенерируй мне..."
                "Gemeni" "Ошибка! Нет доступа к сети."
                "Рома не смог разобраться в проблеме и пошел спать."


    jump lab_scene


label lab_scene:
    play music "audio/lab_main_theme.wav"
    scene bg lab at Transform(xsize=config.screen_width, ysize=config.screen_height) with fade 
    show radmir normal at right:
        yoffset 200
    show screen stats_ui(radmir, enns)

    "На следующий день на занятии..."
    voice "audio/radmir1.wav"
    r_chan "Эннс! Показывай свою реализацию паттернов."

    if not enns.has_code:
        $ radmir.anger = 8
        jump death_no_code

    if enns.code_quality == "trash":
        $ radmir.anger = 8
        voice "audio/radmir2.wav"
        r_chan "Ты принес мне код на 1С? Серьезно?"
        jump death_no_code

    if enns.code_quality == "mid":
        voice "audio/radmir3.wav"
        r_chan "Код подозрительный. Буду спрашивать строго."
        $ radmir.anger += 4
    else:
        voice "audio/radmir4.wav"
        r_chan "Идеальное форматирование. Проверим твои знания."

    voice "audio/radmir5.wav"
    r_chan "Я задам тебе 10 вопросов. Отвечай быстро."

    show screen lifelines

label q1:
    $ current_correct_index = 0 
    $ show_hint_highlight = False 
    $ current_q_skip_label = "q2"

    $ a1, a2, a3, a4 = apply_glitch(["Фабричный метод (Factory Method)", "Абстрактная фабрика (Abstract Factory)", "Строитель (Builder)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Ты пишешь логистический симулятор. Клиентский код не должен знать точный класс транспорта. Тебе нужно делегировать логику инстанцирования подклассам создателя. Какой это паттерн?"
        "[a1]":
            pass
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q2:
    $ current_correct_index = 1
    $ show_hint_highlight = False
    $ current_q_skip_label = "q3"

    $ a1, a2, a3, a4 = apply_glitch(["Прототип (Prototype)", "Одиночка (Singleton)", "Компоновщик (Composite)", "Я не знаю"], enns.stress)
    menu:
        r_chan "В приложении нужно управлять глобальным пулом подключений. Этот паттерн гарантирует единственный экземпляр класса, но за это его часто критикуют из-за усложнения модульного тестирования. О ком речь?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            pass
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q3:
    $ current_correct_index = 2
    $ show_hint_highlight = False
    $ current_q_skip_label = "q4"

    $ a1, a2, a3, a4 = apply_glitch(["Адаптер (Adapter)", "Прокси (Proxy)", "Декоратор (Decorator)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Нужно добавить опциональное шифрование и сжатие текста перед сохранением. Использование наследования приведет к комбинаторному взрыву подклассов. Какой паттерн позволяет оборачивать объекты для динамического добавления свойств?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            pass
        "[a4]":
            $ radmir.anger += 2

label q4:
    $ current_correct_index = 0
    $ show_hint_highlight = False
    $ current_q_skip_label = "q5"

    $ a1, a2, a3, a4 = apply_glitch(["Фасад (Facade)", "Посредник (Mediator)", "Мост (Bridge)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Твой код вынужден работать с десятками сложных классов сторонней библиотеки рендеринга. Ты создаешь один класс с простым интерфейсом, скрывающим сложную подсистему. Это..."
        "[a1]":
            pass
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q5:
    $ current_correct_index = 1
    $ show_hint_highlight = False
    $ current_q_skip_label = "q6"

    $ a1, a2, a3, a4 = apply_glitch(["Адаптер (Adapter)", "Прокси (Proxy)", "Приспособленец (Flyweight)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Загрузка 3D-модели занимает много RAM. Ты хочешь отложить её загрузку на потом, когда она понадобится, подставив вместо нее легковесную «заглушку», контролирующую доступ к оригиналу. Какой паттерн применим?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            pass
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q6:
    $ current_correct_index = 2
    $ show_hint_highlight = False
    $ current_q_skip_label = "q7"

    $ a1, a2, a3, a4 = apply_glitch(["Состояние (State)", "Стратегия (Strategy)", "Команда (Command)", "Я не знаю"], enns.stress)
    menu:
        r_chan "В графическом редакторе требуется внедрить функционал отмены и повтора операций. Какой паттерн инкапсулирует каждый запрос пользователя как отдельный объект, позволяя ставить их в очередь и логировать?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            pass
        "[a4]":
            $ radmir.anger += 2

label q7:
    $ current_correct_index = 0
    $ show_hint_highlight = False
    $ current_q_skip_label = "q8"

    $ a1, a2, a3, a4 = apply_glitch(["Хранитель (Memento)", "Прототип (Prototype)", "Шаблонный метод (Template Method)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Нужно реализовать систему сохранения, не раскрывая внутреннее устройство классов персонажа. Состояние должно надежно прятаться от внешнего вмешательства, чтобы не нарушать инкапсуляцию. Чей это функционал?"
        "[a1]":
            pass
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q8:
    $ current_correct_index = 1
    $ show_hint_highlight = False
    $ current_q_skip_label = "q9"

    $ a1, a2, a3, a4 = apply_glitch(["Цепочка обязанностей (Chain of Responsibility)", "Наблюдатель (Observer)", "Посредник (Mediator)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Сервер котировок регулярно обновляет цены акций. Десятки различных виджетов должны реагировать на это. Чтобы не заставлять виджеты постоянно опрашивать сервер, какой паттерн организует механизм подписки на события?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            pass
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label q9:
    $ current_correct_index = 2
    $ show_hint_highlight = False
    $ current_q_skip_label = "q10"

    $ a1, a2, a3, a4 = apply_glitch(["Шаблонный метод (Template Method)", "Состояние (State)", "Стратегия (Strategy)", "Я не знаю"], enns.stress)
    menu:
        r_chan "Интернет-магазин должен рассчитывать стоимость доставки разными способами. Чтобы не плодить огромный switch-case, ты выносишь эти алгоритмы в отдельные классы, позволяя клиенту менять их на лету. Что это?"
        "[a1]":
            $ radmir.anger += 1
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            pass
        "[a4]":
            $ radmir.anger += 2

label q10:
    $ current_correct_index = 0
    $ show_hint_highlight = False
    $ current_q_skip_label = "end_lab"

    $ a1, a2, a3, a4 = apply_glitch(["Посредник (Mediator)", "Фасад (Facade)", "Наблюдатель (Observer)", "Я не знаю"], enns.stress)
    menu:
        r_chan "У тебя есть UI: при выборе чекбокса выпадает список и активируется кнопка. Чтобы компоненты не ссылались друг на друга напрямую, ты вводишь независимый объект для инкапсуляции их связей. Как он зовется?"
        "[a1]":
            pass
        "[a2]":
            $ radmir.anger += 1
        "[a3]":
            $ radmir.anger += 1
        "[a4]":
            $ radmir.anger += 2

label end_lab:
    hide screen lifelines
    hide screen stats_ui

    stop music fadeout 2.0
    
    show radmir normal at center with dissolve:
        zoom 1.1 
    
    "Тишина в аудитории..."
    "Радмир Ренатович внимательно просматривает ваш код в последний раз."
    voice "audio/radmir6.wav"
    r_chan "Знаешь, Эннс... Я ожидал увидеть здесь кучу нейро-кода."
    voice "audio/radmir7.wav"
    r_chan "Но ты меня удивил."
    voice "audio/enns5.wav"
    e_chan "Правда? То есть я... сдал?"
    voice "audio/radmir8.wav"
    r_chan "Не просто сдал. Ты продемонстрировал отличную сильную связанность между своими знаниями и моими вопросами."
    
    show layer master:
        truecenter
        matrixcolor BrightnessMatrix(0.2)
        linear 0.5 matrixcolor BrightnessMatrix(0.0)
    voice "audio/radmir9.wav"
    r_chan "Твоя реализация паттернов была чистой. Никаких утечек памяти, никакой избыточности."
    voice "audio/radmir10.wav"
    r_chan "Я ставлю 'Отлично'. И, пожалуй..."   
    voice "audio/radmir11.wav"
    r_chan "Зайди на следующей неделе. Нам на кафедре нужны люди, которые умеют проектировать системы в условиях экстремального стресса."    
    voice "audio/enns6.wav"
    e_chan "Да! Есть! Спасибо большое, Радмир Ренатович!"
    
    scene black with fade
    play music "audio/good_end.wav"
    show text "{b}{color=#3498db}ХОРОШАЯ КОНЦОВКА{/color}{/b}\n{size=30}Вы не просто сдали лабу, вы заслужили уважение Радмира Ренатовича.{/size}" at truecenter with dissolve
    $ renpy.pause(5.0, hard=True)
    hide text
    with fade
    scene bg good end at Transform(xsize=config.screen_width, ysize=config.screen_height) with fade 
    "Рома вышел из универа. Солнце светило как-то по-особенному."
    "Теперь он знал: жизнь это не только баги и стресс..."
    "...это правильно выбранный паттерн."
    window hide 
    stop music fadeout 13.0 
    $ renpy.pause(10.0, hard=True)
    scene black with Dissolve(3.0)
    
    return

label naruto_action:
    voice "audio/radmir12.wav"
    r_chan "Какой еще Наруто на паре?! Ну ладно, раз ты так хочешь..."
    voice "audio/radmir13.wav"
    r_chan "Сколько хвостов у Сон Гоку?"
    menu:
        "Четыре":
            voice "audio/radmir14.wav"
            r_chan "Хм... Правильно. Но это вам не поможет в программировании! Едем дальше."
        "Six Seven":
            $ radmir.anger += 2
            voice "audio/radmir15.wav"
            r_chan "Идиот..."
        "Пять":
            $ radmir.anger += 1
            voice "audio/radmir16.wav"
            r_chan "Чем ты Артема слушал? Неверно!"
    jump expression current_q_skip_label

label bribe_action:
    voice "audio/enns7.wav"
    e_chan "Радмир Ренатович, а хотите кислинку?"
    "Рома протягивает преподавателю фиолетовую кислинку."
    r_chan "..."
    voice "audio/radmir17.wav"
    r_chan "Давайте сюда. Мои любимые."
    "Радмир Ренатович съедает конфету, его лицо становится чуть менее напряженным."
    $ radmir.anger = max(0, radmir.anger - 2)
    voice "audio/radmir18.wav"
    r_chan "Ладно, этот вопрос проехали."
    jump expression current_q_skip_label

label death_no_code:
    voice "audio/radmir19.wav"
    r_chan "Ты пришел на лабу без кода."
    voice "audio/radmir20.wav"
    r_chan "Зачем ты сюда пришел?"
    jump death_by_anger

label death_by_anger:
    hide screen lifelines
    hide screen stats_ui
    
    stop music fadeout 0.5
    play sound "audio/glitch_noise.wav" 
    scene bg lab at Transform(xsize=config.screen_width, ysize=config.screen_height) with hpunch 
    
    show radmir furious at center with dissolve:
        zoom 2 
        yoffset 1000
    voice "audio/radmir21.wav"
    r_chan "ЗНАЧИТ ТАК, ЭННС..."
    voice "audio/radmir22.wav"
    r_chan "Ты не понимаешь паттерны? Ты не чувствуешь архитектуру?"
    voice "audio/radmir23.wav"
    r_chan "Ты принес мне мусор вместо кода."
    
    play music "audio/dark_ambient.mp3" fadein 2.0
    voice "audio/radmir24.wav"
    r_chan "Раз ты не можешь реализовать паттерн, ты САМ станешь паттерном."
    voice "audio/enns8.wav"
    e_chan "В-в смысле? Радмир Ренатович, я всё переделаю!"
    voice "audio/radmir25.wav"
    r_chan "Поздно. Я применяю к тебе приватный конструктор."
    voice "audio/radmir26.wav"
    r_chan "Отныне ты Одиночка (Singleton)."
    
    show layer master:
        truecenter
        parallel:
            matrixcolor InvertMatrix(0.0)
            linear 0.2 matrixcolor InvertMatrix(1.0)
            linear 0.2 matrixcolor InvertMatrix(0.0)
            repeat
    voice "audio/radmir27.wav"
    r_chan "У тебя не будет друзей. У тебя не будет наследников."
    voice "audio/radmir28.wav"
    r_chan "Ты будешь существовать в единственном экземпляре в этой лаборатории... ВЕЧНО!"
    
    
    scene black with dissolve
    play sound "audio/system_error.wav"
    show text "{color=#ff0000}{size=50}ОШИБКА КОМПИЛЯЦИИ ЖИЗНИ{/size}{/color}" at truecenter with dissolve
    $ renpy.pause(5.0, hard=True)
    hide text
    with fade
    scene bg bad end at Transform(xsize=config.screen_width, ysize=config.screen_height) with fade 
    "Рома Эннс был статически инициализирован в углу лаборантской."
    "Теперь он часть глобальной области видимости кафедры."
    "Его нельзя удалить. Его нельзя изменить. Его можно только вызвать для проверки отчетов первокурсников."
    window hide 
    stop music fadeout 13.0 
    $ renpy.pause(10.0, hard=True)
    scene black with Dissolve(3.0)
    
    
    
    return