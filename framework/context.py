class SceneContext:
    """子场景间共享状态的类型安全容器"""

    def __init__(self):
        self._store = {}

    def put(self, key: str, mobject):
        self._store[key] = mobject

    def get(self, key: str):
        return self._store.get(key)

    def remove(self, key: str):
        self._store.pop(key, None)
