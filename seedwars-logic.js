// Seed Wars: shared game rules (phone + host + node test). Pure functions, no Firebase.
//
// A strip of 12 farm counties runs from cool (north) to hot (south). Each round every company
// releases one variety bred for a summer temperature. Breeding takes a year: the variety is
// planted NEXT year, after the climate warms. In each county, farmers split their seed purchases
// by yield (better-adapted varieties win most of the farmers); an old public variety, adapted to
// the original climate, keeps the farmers nobody beats, and it fades as the climate warms.
// It's a teaching simulation, not real data.

export const COUNTIES = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]; // summer high, round 1 (deg C)
export const FARMERS  = [3, 4, 6, 8, 10, 11, 11, 10, 8, 6, 4, 3];         // farmers per county (sum 84)
export const WARMING = 1.0;          // deg C per year
export const ROUNDS = 4;
export const WIDTH = 1.5;            // how narrowly a variety is adapted (deg C)
export const PEAK = 12;              // yield at its target climate (t/ha)
export const POWER = 6;              // how strongly farmers favour the higher-yielding seed
export const DOLLARS_PER_FARMER = 1; // $M of seed sales per farmer per year
export const COLORS = ["#e6194b","#3cb44b","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#9a6324",
  "#469990","#800000","#808000","#000075","#ff6f91","#2f4f4f","#bfa000","#a9a9a9","#5b8c00"];

// climate farmers actually plant in during round r (1-based): one more year of warming
export const plantClimate = (r) => COUNTIES.map((t) => t + WARMING * r);
// climate shown as "this year" when round r opens
export const nowClimate = (r) => COUNTIES.map((t) => t + WARMING * (r - 1));

export const yieldAt = (target, T) => PEAK * Math.exp(-((T - target) ** 2) / (2 * WIDTH ** 2));
const publicYield = (T0, T) => 8 * Math.exp(-((T - T0) ** 2) / (2 * 2 ** 2));

// moves: {group: target}. Returns per-county shares and per-group revenue for round r.
export function scoreRound(moves, r) {
  const groups = Object.keys(moves).map(Number).sort((a, b) => a - b);
  const climate = plantClimate(r);
  const revenue = Object.fromEntries(groups.map((g) => [g, 0]));
  const counties = climate.map((T, c) => {
    const ys = groups.map((g) => yieldAt(moves[g], T));
    const pub = publicYield(COUNTIES[c], T);
    const w = ys.map((y) => y ** POWER), wp = pub ** POWER;
    const den = w.reduce((a, b) => a + b, 0) + wp;
    const shares = {};
    groups.forEach((g, i) => {
      shares[g] = w[i] / den;
      revenue[g] += FARMERS[c] * shares[g] * DOLLARS_PER_FARMER;
    });
    let top = null, best = wp / den;
    groups.forEach((g) => { if (shares[g] > best) { best = shares[g]; top = g; } });
    return { T, farmers: FARMERS[c], shares, publicShare: wp / den, top, topShare: best };
  });
  return { counties, revenue };
}

// Parse the poll responses into game state. Messages (text field):
//   J|g|tok          a phone claims group g (first claim per group wins)
//   M|r|g|tok|t      group g's move for round r: target temperature t (last valid one counts)
//   H|open|r  H|reveal|r  H|reset   host control (latest wins; reset starts a fresh game)
export function parse(responses) {
  const list = Object.values(responses || {}).filter((x) => x && typeof x.text === "string")
    .sort((a, b) => (a.ts || 0) - (b.ts || 0));
  let start = 0;
  list.forEach((x, i) => { if (x.text === "H|reset") start = i + 1; });
  const owner = {}, moves = {}, state = { phase: "lobby", round: 0 };
  for (const x of list.slice(start)) {
    const p = x.text.split("|");
    if (p[0] === "J" && p.length === 3) {
      const g = +p[1];
      if (g >= 1 && g <= 17 && !(g in owner)) owner[g] = p[2];
    } else if (p[0] === "M" && p.length === 5) {
      const r = +p[1], g = +p[2], t = +p[4];
      if (owner[g] === p[3] && r === state.round && state.phase === "open" && t >= 15 && t <= 40) {
        (moves[r] ||= {})[g] = t;
      }
    } else if (p[0] === "H" && (p[1] === "open" || p[1] === "reveal")) {
      state.phase = p[1]; state.round = +p[2];
    }
  }
  const results = {}, total = {};
  Object.keys(owner).forEach((g) => (total[g] = 0));
  for (let r = 1; r <= ROUNDS; r++) {
    const done = r < state.round || (r === state.round && state.phase === "reveal");
    if (done && moves[r] && Object.keys(moves[r]).length) {
      results[r] = scoreRound(moves[r], r);
      for (const [g, v] of Object.entries(results[r].revenue)) total[g] = (total[g] || 0) + v;
    }
  }
  return { state, owner, moves, results, total };
}
