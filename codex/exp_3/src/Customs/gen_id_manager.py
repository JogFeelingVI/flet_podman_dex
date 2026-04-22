# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-04-22 07:26:08
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-22 13:24:54
import json
import os
import pathlib
import re

try:
    from .jackpot_core import randomData
except:
    from jackpot_core import randomData

class systemConfigManager:

    app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
    app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
    app_assets_dir = os.getenv("FLET_ASSETS_DIR")

    def __init__(self):
        self.config_path = os.path.join(self.app_data_path, "systemconfig.json")
        self.config_data = self.load_config()

    def default_config(self) -> dict:
        return {
            "stored_id": None,
            "stored_path": None
        }

    def load_config(self) -> dict:
        defconf = self.default_config()
        try:
            with open(self.config_path, 'r') as f:
                defconf.update(json.load(f))
            return defconf
        except FileNotFoundError:
            return self.default_config()
        

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def get_stored_id(self):
        return self.config_data.get("stored_id")

    def set_stored_id(self):
        new_id = randomData.generate_secure_string(8)
        self.config_data["stored_id"] = new_id
        self.save_config()
        return self

    def get_stored_path(self):
        return self.config_data.get("stored_path")

    def set_stored_path(self):
        stored_path = os.path.join(self.app_temp_path, f"gen_{self.get_stored_id()}.dict")
        filePath = pathlib.Path(stored_path)
        for item in filePath.parent.iterdir():
            if (
                item.is_file() or item.is_symlink() and item.name.startswith("gen_")
            ):  # 确保只删除文件
                item.unlink()
        filePath.parent.mkdir(parents=True, exist_ok=True)
        filePath.write_text("")
        self.config_data["stored_path"] = stored_path
        self.save_config()
        return self
    
    def open_from_file(self, path:str=None):
        stored_path = self.get_stored_path() if not path else path
        if stored_path and os.path.exists(stored_path):
            with open(stored_path, "r", encoding="utf-8") as f:
                return json.load(f)
    

    def write_to_file(self, data:list, path:str=None):
        stored_path = self.get_stored_path() if not path else path
        if stored_path:
            with open(stored_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

system_conf = systemConfigManager()

