import json
import os

SETTINGS_FILE = "config.json"

class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
            except Exception as e:
                print("Erro ao carregar configurações:", e)
                self.settings = {}
        else:
            self.settings = {
                "mic_permission": False
            }
            self.save_settings()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print("Erro ao salvar configurações:", e)

    def get_mic_permission(self):
        return self.settings.get("mic_permission", False)

    def set_mic_permission(self, granted: bool):
        self.settings["mic_permission"] = granted
        self.save_settings()

    def get_credentials(self):
        return self.settings.get("credentials", {})

    def set_credentials(self, email, password):
        self.settings["credentials"] = {"email": email, "password": password}
        self.save_settings()

    def clear_credentials(self):
        if "credentials" in self.settings:
            del self.settings["credentials"]
        self.save_settings()

    def get_wake_words(self):
        return self.settings.get("wake_words", ["computador", "jarvis", "agente"])

    def set_wake_words(self, words: list):
        self.settings["wake_words"] = [w.strip().lower() for w in words if w.strip()]
        self.save_settings()
