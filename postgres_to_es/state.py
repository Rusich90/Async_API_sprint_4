import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Optional


class Storage:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        with open(self.file_path, "w") as write_file:
            json.dump(state, write_file)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        filename = Path(self.file_path)
        filename.touch(exist_ok=True)
        with open(self.file_path, "r") as read_file:
            try:
                state = json.load(read_file)
            except JSONDecodeError:
                state = {}
        return state


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        state = self.storage.retrieve_state()
        state[key] = value
        self.storage.save_state(state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        state = self.storage.retrieve_state()
        date = state[key] if state.get(key) else None
        return date
