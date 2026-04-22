# Лабораторная работа 3: Наблюдатель

## Предметная область: Визуальная новелла (Симулятор сдачи лабораторной)

### 1. Описание проблемы

В игре присутствует преподаватель (`Teacher`), уровень гнева которого (`anger`) меняется в зависимости от действий студента (неправильные ответы, отсутствие кода). При изменении уровня гнева в игре должно происходить множество событий: рост стресса у студента, вывод предупреждений на экран, а при достижении максимума — поражение (Game Over).

Без применения паттерна логика обработки этих последствий находилась бы прямо в сеттере гнева преподавателя:

```python
class Teacher:
        def __init__(self, name):
            self.name = name
            self._anger = 0
            self.student = None 
            self.notified_angry = False 
            self.notified_furious = False 

        @property
        def anger(self):
            return self._anger

        @anger.setter
        def anger(self, value):
            self._anger = value
            
            if self._anger >= 8:
                renpy.show("radmir furious")
            elif self._anger >= 4:
                renpy.show("radmir angry")
            else:
                renpy.show("radmir normal")

            if self._anger >= 8:
                target_music = "audio/furious.wav"
            elif self._anger >= 4:
                target_music = "audio/angry.wav"
            else:
                target_music = "audio/lab_main_theme.wav"

            if renpy.music.get_playing() != target_music:
                renpy.music.play(target_music, fadein=.3, fadeout=.3)

            if self.student is not None:
                self.student.stress = self._anger + random.randint(1, 2)

            if self._anger >= 10:
                renpy.jump("death_by_anger")
                
            elif self._anger >= 8 and not self.notified_furious:
                renpy.with_statement(hpunch)
                renpy.notify("БЕГИ, ЭННС!")
                self.notified_furious = True
                
            elif self._anger >= 4 and not self.notified_angry:
                renpy.notify("Радмир Ренатович начинает закипать...")
                self.notified_angry = True

            if self._anger < 8:
                self.notified_furious = False
            if self._anger < 4:
                self.notified_angry = False
```

Это приводит к следующим проблемам:
- **Нарушение принципа единственной ответственности (SRP)** — класс `Teacher` вынужден знать о логике поражения в игре (`renpy.jump`), интерфейсе уведомлений и состоянии объекта `Student`.
- **Нарушение принципа открытости/закрытости (OCP)** — если мы захотим добавить новое последствие гнева (например, разблокировку достижения или реакцию других студентов в аудитории), нам придется менять класс `Teacher`.
- **Сильная связанность (Tight Coupling)** — преподаватель жестко связан с конкретными экземплярами и глобальным состоянием визуальной новеллы.

### 2. Решение: паттерн Observer (Наблюдатель)

Паттерн Observer позволяет вынести реакцию на изменение состояния субъекта в отдельные классы-наблюдатели. Субъект (`Teacher`) лишь оповещает подписанных наблюдателей о том, что его состояние изменилось, ничего не зная о том, кто они и как отреагируют.

#### Структура проекта

Создан базовый класс `Subject`, который управляет списком подписчиков (метод `attach`) и рассылает им уведомления (метод `notify`). Класс `Teacher` (как и `Student`) наследуется от `Subject` и вызывает `self.notify()` внутри сеттера свойства `anger`.

Определён абстрактный класс `Observer` с абстрактным методом:
- `update(subject: Subject)` — метод, который вызывается субъектом при изменении состояния.

Два конкретных наблюдателя реализуют этот интерфейс:

| Итератор / Наблюдатель | Поведение |
|---|---|
| `DeathObserver` | Следит за уровнем гнева учителя. Выводит на экран предупреждения (при `anger >= 4` и `anger >= 8`). Если гнев достигает 10, вызывает экран поражения (`death_by_anger`). Хранит флаги, чтобы не спамить уведомлениями. |
| `StressRelay` | Выступает в роли реле (связующего звена). При инициализации получает ссылку на `Student`. При обновлении считывает гнев учителя и динамически пересчитывает уровень стресса студента с элементом псевдослучайности. |

В основном скрипте игры мы просто связываем объекты во время выполнения (Runtime):

```python
$ enns = Student("Рома")
$ radmir = Teacher("Радмир Ренатович")

python:
  radmir.attach(DeathObserver())
  radmir.attach(StressRelay(enns))
```

### 3. Диаграмма классов
![Диаграмма классов](https://github.com/sanrish-lan/Object-oriented-analysis-and-design-2/blob/main/lab03/ooap3lab.drawio.png)

### 4. Вывод

Внедрение паттерна Observer повлияло на проект следующим образом:

**Слабая связанность (Loose Coupling).** Класс `Teacher` теперь ничего не знает об объекте `Student`, логике проигрыша (`DeathObserver`) или механике стресса. Он отвечает только за свои собственные данные (имя, гнев).

**Расширяемость (OCP).** Если в игру потребуется добавить логику, при которой из-за криков преподавателя в аудиторию заходит декан, достаточно будет создать класс `DeanObserver` и сделать `radmir.attach(DeanObserver())`. Исходный код классов `Teacher` или `Student` вообще не придется менять.

**Динамическое поведение.** Наблюдателей можно добавлять и удалять прямо по ходу сюжета. Например, если студент выпьет успокоительное, можно динамически отписать `StressRelay` от учителя, и рост гнева перестанет влиять на стресс студента.
