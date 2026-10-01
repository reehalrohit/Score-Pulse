"use client";

interface Batter {
  name: string;
  runs?: number | string;
  balls?: number | string;
  fours?: number | string;
  sixes?: number | string;
  strikeRate?: number | string;
  out?: string;
}

interface Bowler {
  name: string;
  overs?: number | string;
  maidens?: number | string;
  runs?: number | string;
  wickets?: number | string;
  economy?: number | string;
}

interface CricketScorecardProps {
  innings: {
    team: string;
    score: string;
    overs?: string;
    batters?: Batter[];
    bowlers?: Bowler[];
  }[];
}

export default function CricketScorecard({
  innings,
}: CricketScorecardProps) {
  if (!innings.length) {
    return (
      <div className="rounded-2xl border border-zinc-800 p-6 text-center text-sm text-zinc-500">
        Cricket scorecard data is not available yet.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {innings.map((inning, index) => (
        <section
          key={`${inning.team}-${index}`}
          className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950"
        >
          <div className="flex items-center justify-between border-b border-zinc-800 p-4">
            <div>
              <h3 className="font-bold">
                {inning.team}
              </h3>

              <p className="mt-1 text-xs text-zinc-500">
                Innings {index + 1}
              </p>
            </div>

            <div className="text-right">
              <p className="text-xl font-black">
                {inning.score}
              </p>

              {inning.overs && (
                <p className="text-xs text-zinc-500">
                  {inning.overs} overs
                </p>
              )}
            </div>
          </div>

          {inning.batters?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b border-zinc-800 text-xs text-zinc-500">
                  <tr>
                    <th className="px-4 py-3 text-left">
                      Batter
                    </th>
                    <th className="px-3 py-3 text-right">
                      R
                    </th>
                    <th className="px-3 py-3 text-right">
                      B
                    </th>
                    <th className="px-3 py-3 text-right">
                      4s
                    </th>
                    <th className="px-3 py-3 text-right">
                      6s
                    </th>
                    <th className="px-4 py-3 text-right">
                      SR
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {inning.batters.map(
                    (batter) => (
                      <tr
                        key={batter.name}
                        className="border-b border-zinc-900 last:border-0"
                      >
                        <td className="px-4 py-3">
                          <div className="font-medium">
                            {batter.name}
                          </div>

                          {batter.out && (
                            <div className="mt-1 text-[11px] text-zinc-600">
                              {batter.out}
                            </div>
                          )}
                        </td>

                        <td className="px-3 py-3 text-right font-bold">
                          {batter.runs ?? "-"}
                        </td>

                        <td className="px-3 py-3 text-right text-zinc-400">
                          {batter.balls ?? "-"}
                        </td>

                        <td className="px-3 py-3 text-right text-zinc-400">
                          {batter.fours ?? "-"}
                        </td>

                        <td className="px-3 py-3 text-right text-zinc-400">
                          {batter.sixes ?? "-"}
                        </td>

                        <td className="px-4 py-3 text-right text-zinc-400">
                          {batter.strikeRate ?? "-"}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          ) : null}

          {inning.bowlers?.length ? (
            <div className="border-t border-zinc-800">
              <div className="px-4 py-3 text-xs font-bold uppercase tracking-widest text-zinc-500">
                Bowling
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-zinc-800 text-xs text-zinc-500">
                    <tr>
                      <th className="px-4 py-3 text-left">
                        Bowler
                      </th>
                      <th className="px-3 py-3 text-right">
                        O
                      </th>
                      <th className="px-3 py-3 text-right">
                        M
                      </th>
                      <th className="px-3 py-3 text-right">
                        R
                      </th>
                      <th className="px-3 py-3 text-right">
                        W
                      </th>
                      <th className="px-4 py-3 text-right">
                        Econ
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {inning.bowlers.map(
                      (bowler) => (
                        <tr
                          key={bowler.name}
                          className="border-b border-zinc-900 last:border-0"
                        >
                          <td className="px-4 py-3 font-medium">
                            {bowler.name}
                          </td>

                          <td className="px-3 py-3 text-right">
                            {bowler.overs ?? "-"}
                          </td>

                          <td className="px-3 py-3 text-right text-zinc-400">
                            {bowler.maidens ?? "-"}
                          </td>

                          <td className="px-3 py-3 text-right text-zinc-400">
                            {bowler.runs ?? "-"}
                          </td>

                          <td className="px-3 py-3 text-right font-bold">
                            {bowler.wickets ?? "-"}
                          </td>

                          <td className="px-4 py-3 text-right text-zinc-400">
                            {bowler.economy ?? "-"}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
        </section>
      ))}
    </div>
  );
                      }
