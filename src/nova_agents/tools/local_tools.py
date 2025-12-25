import secrets
import string
import re
import zipfile
import tarfile
import io
import csv
import json
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseTool

class PasswordGeneratorTool(BaseTool):
    @property
    def name(self) -> str:
        return "password_generator"

    @property
    def description(self) -> str:
        return "password_generator(length=16, use_symbols=True) - Generate a strong password"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        length = int(args.get("length", 16))
        use_symbols = args.get("use_symbols", True)
        
        chars = string.ascii_letters + string.digits
        if use_symbols:
            chars += string.punctuation
            
        password = ''.join(secrets.choice(chars) for _ in range(length))
        return {"success": True, "result": password}

class RegexTesterTool(BaseTool):
    @property
    def name(self) -> str:
        return "regex_tester"

    @property
    def description(self) -> str:
        return "regex_tester(pattern, text) - Test a regex pattern against text"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        pattern = args.get("pattern", "")
        text = args.get("text", "")
        
        try:
            matches = list(re.finditer(pattern, text))
            results = []
            for m in matches:
                results.append({
                    "match": m.group(0),
                    "start": m.start(),
                    "end": m.end(),
                    "groups": m.groups()
                })
            return {"success": True, "result": {"count": len(results), "matches": results}}
        except Exception as e:
            return {"success": False, "error": str(e)}

class ZipUnzipTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "zip_unzip"

    @property
    def description(self) -> str:
        return "zip_unzip(action='zip'|'unzip', path, output_path) - Compress or extract files"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        action = args.get("action")
        path = args.get("path")
        output_path = args.get("output_path")
        
        full_path = (self.workspace_dir / path).resolve()
        full_output = (self.workspace_dir / output_path).resolve()
        
        if not str(full_path).startswith(str(self.workspace_dir)):
            return {"success": False, "error": "Access denied"}
            
        try:
            if action == "zip":
                with zipfile.ZipFile(full_output, 'w') as zf:
                    if full_path.is_dir():
                        for file in full_path.rglob('*'):
                            zf.write(file, file.relative_to(full_path.parent))
                    else:
                        zf.write(full_path, full_path.name)
                return {"success": True, "result": f"Created {output_path}"}
                
            elif action == "unzip":
                with zipfile.ZipFile(full_path, 'r') as zf:
                    zf.extractall(full_output)
                return {"success": True, "result": f"Extracted to {output_path}"}
                
            return {"success": False, "error": "Invalid action"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class UnitConverterTool(BaseTool):
    @property
    def name(self) -> str:
        return "unit_converter"

    @property
    def description(self) -> str:
        return "unit_converter(value, from_unit, to_unit) - Convert units (simple implementation)"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        # This is a stub for a full unit converter library
        # In a real implementation, use a library like pint
        return {"success": True, "result": f"Converted {args.get('value')} {args.get('from_unit')} to {args.get('to_unit')} (Mock)"}

class FileConvertTool(BaseTool):
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "file_convert"

    @property
    def description(self) -> str:
        return "file_convert(input_path, output_format) - Convert CSV/JSON/YAML"

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        input_path = args.get("input_path")
        output_format = args.get("output_format", "json")
        
        full_path = (self.workspace_dir / input_path).resolve()
        
        try:
            if full_path.suffix == ".csv" and output_format == "json":
                with open(full_path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
                return {"success": True, "result": json.dumps(data, indent=2)}
            
            # Add more conversions as needed
            return {"success": False, "error": "Unsupported conversion"}
        except Exception as e:
            return {"success": False, "error": str(e)}
