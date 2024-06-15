## Установка

1. Создайте виртуальное окружение и активируйте его:
   - windows
   ```shell
   python -m venv venv
   ```
   
   - linux/macOS
   ```shell
   source venv/bin/activate
   ```
2. Установите зависимости:
    ```shell
    pip install -r requirements.txt
    ```

3. Измените файл <*.env*> и подставьте значение ключа.

4. Переход в директорию:
   ```shell
   cd ldt
   ```

5. Примените миграции:
   ```shell
   python manage.py migrate
   ```

6. Запуск приложения:

   ```shell
   python manage.py runserver
   ```

--------------------------------