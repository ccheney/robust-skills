export function rank(scores) {
  return scores.sort((a, b) => b.points - a.points);
}

