# System & Network Tools (Nova v2.1)

Nova v2.1 introduces a suite of powerful system and network tools, enabling autonomous operations.

## System Tools (`sys.*`, `shell.*`)

| Tool | Description | Safety |
|---|---|---|
| `sys.usage` | CPU & RAM usage | Safe |
| `sys.disk_usage` | Disk space info | Safe |
| `sys.network_info` | Network interfaces | Safe |
| `sys.open_file` | Open file in default app | Safe |
| `shell.run` | Run shell command | **Restricted** |
| `shell.run_safe` | Run shell command (alias) | **Restricted** |
| `shell.list_processes` | List running processes | Safe |
| `shell.kill_safe` | Kill process by PID | **Restricted** |

## Network Tools (`net.*`)

| Tool | Description | Safety |
|---|---|---|
| `net.get` | GET request | Safe |
| `net.post` | POST request | Safe |
| `net.download` | Download file | Safe |
| `net.check` | Check connectivity | Safe |
| `dns.lookup` | DNS lookup (via `net.check` or `shell`) | Safe |

## Usage Examples

### Check System Health
```json
{"tool": "sys.usage", "args": {}}
{"tool": "sys.disk_usage", "args": {"path": "/"}}
```

### Download & Execute (Hypothetical)
```json
{"tool": "net.download", "args": {"url": "https://example.com/script.sh", "dest": "script.sh"}}
{"tool": "shell.run", "args": {"command": "chmod +x script.sh && ./script.sh"}}
```
*Note: The second step will trigger a safety confirmation.*
