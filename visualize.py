from __future__ import annotations
from itertools import count

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, NamedTuple
from datetime import datetime
import matplotlib.pyplot as plt

JsonDict = Dict[str, float]


class ExchangeRateRecord(NamedTuple):
    time: datetime
    exchangeRate: float


@dataclass(repr=False, eq=False)
class ExchangeRateHistory:
    records: List[ExchangeRateRecord]
    plotFormat: ClassVar[Dict[str, Any]]

    @classmethod
    def fromJson(cls, jsonPath: Path) -> ExchangeRateHistory:
        with open(jsonPath, "r") as jsonFile:
            data: JsonDict = json.load(jsonFile)
            history = ExchangeRateHistory([])
            for timestampStr, exchangeRate in data.items():
                time = datetime.fromtimestamp(float(timestampStr))
                history.records.append(ExchangeRateRecord(time, float(exchangeRate)))
            return history

    def _recordCount(self, since: datetime) -> int:
        count = 0
        while self.records[-(count+1)].time >= since:
            count += 1
        return count

    def lastRecords(self, since: datetime) -> ExchangeRateHistory:
        count = self._recordCountSince(since)
        if count == 0:
            return ExchangeRateHistory([])
        else:
            return ExchangeRateHistory(self.records[-count:])


    def plot(self, output: Path, since: datetime | None = None) -> None:
        fig, ax = plt.subplots()

        index = self._recordCount(since) + 1 if since is not None else 0
        x, y = zip(*self.records[-index:])

        ax.plot(x, y, **ExchangeRateHistory.plotFormat)
        plt.savefig(output)


ExchangeRateHistory.plotFormat = {
    "linestyle": "dashed",
    "linewidth": 2,
    "color": "salmon",
    "marker": "D",
    "markersize": 4,
    "markerfacecolor": "crimson",
    "markeredgecolor": "crimson"
}

if __name__ == "__main__":
    hist = ExchangeRateHistory.fromJson(Path("data.json"))
    hist.plot(Path("amogus.png"))
