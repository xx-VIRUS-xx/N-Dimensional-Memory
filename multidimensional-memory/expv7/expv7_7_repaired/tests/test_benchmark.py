import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.validate import main

def test_repaired_dataset():
    main()
