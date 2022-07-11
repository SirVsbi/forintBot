from __future__ import annotations

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

    class RecordNotFoundException(Exception):
        pass

    @classmethod
    def fromJson(cls, jsonPath: Path) -> ExchangeRateHistory:
        with open(jsonPath, "r") as jsonFile:
            data: JsonDict = json.load(jsonFile)
            history = ExchangeRateHistory([])
            for timestampStr, exchangeRate in data.items():
                time = datetime.fromtimestamp(float(timestampStr))
                history.records.append(ExchangeRateRecord(time, float(exchangeRate)))
            return history

    def _recordCountSince(self, since: datetime) -> int:
        index = 0
        while self.records[-(index+1)].time >= since:
            index += 1

    def historySince(self, since: datetime) -> ExchangeRateHistory:
        index = self._recordCountSince(since)
        if index == 0:
            raise ExchangeRateHistory.RecordNotFoundException(f"No record since {since.isoformat()}")
        return ExchangeRateHistory(self.records[-(index+1):])


    def plot(self, output: Path, since: datetime | None = None) -> None:
        fig, ax = plt.subplots()

        index = self._recordCountSince(since) + 1 if since is not None else 0
        x, y = zip(*self.records[-index:])

        ax.plot(x, y, **ExchangeRateHistory.plotFormat)
        plt.savefig(output)


ExchangeRateHistory.plotFormat = {
    "linestyle": "dashed",
    "linewidth": 2,
    "color": "green",
    "marker": "D",
    "markersize": 4,
    "markerfacecolor": "red",
    "markeredgecolor": "red"
}
