// Half-width katakana to full-width katakana mapping
const HALF_TO_FULL_KANA = {
  "ｦ": "ヲ", "ｧ": "ァ", "ｨ": "ィ", "ｩ": "ゥ", "ｪ": "ェ", "ｫ": "ォ",
  "ｬ": "ャ", "ｭ": "ュ", "ｮ": "ョ", "ｯ": "ッ", "ｰ": "ー",
  "ｱ": "ア", "ｲ": "イ", "ｳ": "ウ", "ｴ": "エ", "ｵ": "オ",
  "ｶ": "カ", "ｷ": "キ", "ｸ": "ク", "ｹ": "ケ", "ｺ": "コ",
  "ｻ": "サ", "ｼ": "シ", "ｽ": "ス", "ｾ": "セ", "ｿ": "ソ",
  "ﾀ": "タ", "ﾁ": "チ", "ﾂ": "ツ", "ﾃ": "テ", "ﾄ": "ト",
  "ﾅ": "ナ", "ﾆ": "ニ", "ﾇ": "ヌ", "ﾈ": "ネ", "ﾉ": "ノ",
  "ﾊ": "ハ", "ﾋ": "ヒ", "ﾌ": "フ", "ﾍ": "ヘ", "ﾎ": "ホ",
  "ﾏ": "マ", "ﾐ": "ミ", "ﾑ": "ム", "ﾒ": "メ", "ﾓ": "モ",
  "ﾔ": "ヤ", "ﾕ": "ユ", "ﾖ": "ヨ",
  "ﾗ": "ラ", "ﾘ": "リ", "ﾙ": "ル", "ﾚ": "レ", "ﾛ": "ロ",
  "ﾜ": "ワ", "ﾝ": "ン", "ﾞ": "゛", "ﾟ": "゜",
};

function normalizeKatakana(str) {
  let result = str.trim();
  result = result.replace(/[ｦ-ﾟ]/g, (ch) => HALF_TO_FULL_KANA[ch] || ch);
  return result;
}

function checkAnswer(input, correctName) {
  const normalizedInput = normalizeKatakana(input);
  const normalizedCorrect = normalizeKatakana(correctName);
  return normalizedInput === normalizedCorrect;
}

function shuffleArray(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

async function selectQuestions(birdData, settings, progressKeyResolver) {
  const allProgress = await getAllProgress();
  const progressMap = {};
  const resolveProgressKey = typeof progressKeyResolver === "function"
    ? progressKeyResolver
    : (bird) => bird.id;
  allProgress.forEach((p) => {
    progressMap[p.id] = p;
  });

  // Filter out mastered birds unless includeMastered is true
  let pool = birdData.filter((bird) => {
    const progress = progressMap[resolveProgressKey(bird)];
    if (!progress) return true;
    if (settings.includeMastered) return true;
    return !progress.mastered;
  });

  // If pool is empty (all mastered), fall back to full list
  if (pool.length === 0) {
    pool = [...birdData];
  }

  let selected;

  if (settings.prioritizeWrong) {
    // Birds that have been answered wrong (correctStreak === 0 and have been seen)
    const wrongBirds = pool.filter((bird) => {
      const progress = progressMap[resolveProgressKey(bird)];
      return progress && !progress.mastered && progress.correctStreak === 0 && progress.totalAttempts > 0;
    });

    const otherBirds = pool.filter((bird) => !wrongBirds.includes(bird));

    const count = Math.min(settings.questionCount, pool.length);
    const wrongCount = Math.min(Math.ceil(count * 0.6), wrongBirds.length);
    const randomCount = count - wrongCount;

    shuffleArray(wrongBirds);
    shuffleArray(otherBirds);

    selected = [
      ...wrongBirds.slice(0, wrongCount),
      ...otherBirds.slice(0, randomCount),
    ];

    // If we didn't get enough from the two groups, fill in from remaining
    if (selected.length < count) {
      const used = new Set(selected.map((b) => b.id));
      const remaining = pool.filter((b) => !used.has(b.id));
      shuffleArray(remaining);
      selected = selected.concat(remaining.slice(0, count - selected.length));
    }
  } else {
    const count = Math.min(settings.questionCount, pool.length);
    shuffleArray(pool);
    selected = pool.slice(0, count);
  }

  return shuffleArray(selected);
}

async function updateProgress(birdId, isCorrect, masteryThreshold) {
  let record = await getProgress(birdId);

  if (!record) {
    record = {
      id: birdId,
      correctStreak: 0,
      totalAttempts: 0,
      correctTotal: 0,
      mastered: false,
      lastSeen: null,
    };
  }

  record.totalAttempts += 1;
  record.lastSeen = new Date().toISOString();

  if (isCorrect) {
    record.correctStreak += 1;
    record.correctTotal += 1;
    if (record.correctStreak >= masteryThreshold) {
      record.mastered = true;
    }
  } else {
    record.correctStreak = 0;
  }

  await saveProgress(record);
  return record;
}
