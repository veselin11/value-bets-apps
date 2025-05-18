// Надградена версия на приложението за стойностни залози с допълнителни функции

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const mockMatches = [
  {
    id: 1,
    league: "България - efbet Лига",
    time: "18:30",
    home: "ЦСКА София",
    away: "Славия",
    prediction: "1",
    odds: 1.75,
    analysis: "ЦСКА са в битка за титлата, Славия без мотивация",
  },
  {
    id: 2,
    league: "Англия - Висша лига",
    time: "21:00",
    home: "Брайтън",
    away: "Челси",
    prediction: "Гол/Гол",
    odds: 1.95,
    analysis: "И двата отбора са резултатни и без напрежение",
  },
];

export default function BetApp() {
  const [matches, setMatches] = useState(mockMatches);
  const [bankroll, setBankroll] = useState(500);
  const [history, setHistory] = useState([]);
  const [wins, setWins] = useState(0);
  const [losses, setLosses] = useState(0);

  const placeBet = (matchId, decision) => {
    const match = matches.find((m) => m.id === matchId);
    const stake = parseFloat((bankroll * 0.1).toFixed(2));
    const bet = {
      match,
      decision,
      stake,
    };
    setHistory((prev) => [...prev, bet]);
    if (decision === "Съгласен") {
      setBankroll((prev) => prev - stake);
    }
  };

  const simulateResult = (matchId, isWin) => {
    const bet = history.find((b) => b.match.id === matchId);
    if (!bet || bet.decision !== "Съгласен") return;

    const winAmount = parseFloat((bet.stake * bet.match.odds).toFixed(2));
    if (isWin) {
      setWins((w) => w + 1);
      setBankroll((prev) => prev + winAmount);
    } else {
      setLosses((l) => l + 1);
    }
  };

  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">Стойностни залози за днес</h1>
      <p>Банка: {bankroll.toFixed(2)} лв.</p>
      <p>Печалби: {wins} | Загуби: {losses}</p>

      {matches.map((match) => (
        <Card key={match.id} className="bg-white shadow p-4">
          <CardContent>
            <p className="font-semibold">{match.league}</p>
            <p>
              {match.time} - {match.home} vs {match.away}
            </p>
            <p>
              Прогноза: <strong>{match.prediction}</strong> (Коеф.: {match.odds})
            </p>
            <p className="text-sm text-gray-600">{match.analysis}</p>
            <div className="mt-2 space-x-2">
              <Button onClick={() => placeBet(match.id, "Съгласен")}>Заложи</Button>
              <Button onClick={() => placeBet(match.id, "Пропусни")} variant="outline">
                Пропусни
              </Button>
              <Button onClick={() => simulateResult(match.id, true)} variant="default">
                Симулирай Печалба
              </Button>
              <Button onClick={() => simulateResult(match.id, false)} variant="destructive">
                Симулирай Загуба
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}

      <div>
        <h2 className="text-xl font-bold mt-6">История на залозите</h2>
        <ul className="list-disc ml-6">
          {history.map((bet, idx) => (
            <li key={idx}>
              {bet.match.home} - {bet.match.away}: {bet.decision} ({bet.stake} лв.)
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
