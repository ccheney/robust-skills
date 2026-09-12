export async function saveAll(items, save) {
  const results = [];
  items.forEach(async item => { results.push(await save(item)); });
  return results;
}

