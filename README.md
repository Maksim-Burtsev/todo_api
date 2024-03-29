# API для TODO-приложения

<img src='https://www.channelfutures.com/files/2016/03/todo_0.png'>

### **Запуск приложения**

``` 
    docker-compose up --build
```

### **Что было реализовано в проекте:**

1. Создал несколько моделей с использованием валидаторов, автоматическим заполнением полей и choise'ов.

2. Сделал кастомные permission-классы, которые проверяют принадлежность объекта (или связанного с ним через ForeignKey) пользователю.

3. Реализовал аутентификация по токенам с возможностью восстановления пароля через почту.
Модель токенов взял из **DRF**, а отправку кода на почту реализовал с помощью **smtplib** и **email.mime**. (Не брал никаких готовых решений, потому что хотелось сделать самому)  

4. Добавил **celery** и **redis**, с помощью которых осуществляется task отправки кода на почту.  

5. Создал сериализаторы с динамическими полями, которые высчитываются при запросе с помощью annotate или берутся из request'a (из запроса автоматически проставляется user с помощью HiddenField)

6. Сделал следующие «ручки»:
    + аутентификация
    + получение списка задач + добавление новых(тут есть фильтры и поиск)
    + редактирование/удаление/просмотр отдельной задачи и позадачи
    + создание подзадачи
    + регистрация
    + обновление пароля
    + отправка кода на почту
    + проверка правильности кода
    + создание нового пароля после восстановления
    + статистика: возвращается количество выполненных задач+подзадач, а так же их общую численность (всё считается в запросе)

7. Покрыл всё unittest'ами.


### **Для отправки кода восстановление на почту**
Нужно добавить EMAIL и PASSWORD gmail-почты с которой будет происходить отправка сообщений в .env файл.


