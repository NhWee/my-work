"""Small starter script for the research workspace."""

import numpy as np
import pandas as pd


def main() -> None:
    values = np.array([1, 2, 3, 4, 5])
    summary = pd.DataFrame(
        {
            "metric": ["count", "mean", "std"],
            "value": [values.size, values.mean(), values.std()],
        }
    )

    print("Research environment is ready.")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
