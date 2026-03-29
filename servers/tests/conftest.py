import sys
from pathlib import Path

servers_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(servers_dir / "lib"))
sys.path.insert(0, str(servers_dir))
