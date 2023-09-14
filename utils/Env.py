from __future__ import annotations

import os


class Env:

    def __init__(self, env_dict):
        self.env_dict = env_dict

    def get_or_default(self, key, default):
        return self.env_dict[key] if key in self.env_dict else default

    __instance = None

    @classmethod
    def instance(cls) -> Env:
        if Env.__instance is None:
            # Env.load_env(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))
            Env.load_env(os.environ.get('env') if 'env' in os.environ.keys() else '.env')
        return Env.__instance

    @classmethod
    def load_env(cls, env_path):
        with open(env_path, "r") as env_file:
            rows = env_file.readlines()
            env_dict = {}
            for row in rows:
                if row.strip() != "" and row.strip()[0] != '#':
                    key, value = row.split("=", 1)
                    env_dict[key.strip()] = value.strip()
            Env.__instance = Env(env_dict)
