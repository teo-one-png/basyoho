// ============================================================
//  app.js — とり覚え main application logic
// ============================================================

// --------------- State ---------------
var currentQuestions = [];   // Array of bird objects selected for this session
var testAnswers = [];         // Array: { birdId, userInput, isCorrect }
var currentIndex = 0;         // Single mode: current question index
var singleAnswered = [];      // Single mode: answered flags per index
var currentSettings = null;   // Settings captured when the current session starts
var memorizePhase = 'idle';   // idle | memorize | grid-answer
var currentMode = 'bird';     // 'bird' | 'tree'
var currentSubMode = 'insect';
var currentSessionOptions = { randomizeAnswerOrder: false };
var lastSessionOptions = { randomizeAnswerOrder: false };
var answerOrderShuffled = false;
var lastSessionIdsByMode = { bird: [], tree: [], shokusou_insect: [], shokusou_plant: [] };
var recentSessionHistoryByMode = { bird: [], tree: [], shokusou_insect: [], shokusou_plant: [] };

// --------------- Active data source ---------------
function getActiveData() {
  if (currentMode === 'tree') return TREE_DATA;
  if (currentMode === 'nakigoe') return NAKIGOE_DATA;
  if (currentMode === 'shokusou') {
    return currentSubMode === 'plant' ? PLANT_DATA : INSECT_DATA;
  }
  return BIRD_DATA;
}

function isNakigoeMode() {
  return currentMode === 'nakigoe';
}

function isShokusouMode() {
  return currentMode === 'shokusou';
}

function getSessionModeKey() {
  if (currentMode === 'shokusou') return 'shokusou_' + currentSubMode;
  return currentMode;
}

// Audio playback for nakigoe mode
var currentAudioElement = null;
function playBirdAudio(audioSrc) {
  if (currentAudioElement) {
    currentAudioElement.pause();
    currentAudioElement = null;
  }
  currentAudioElement = new Audio(audioSrc);
  currentAudioElement.play().catch(function (e) {
    console.error('Audio play error:', e);
  });
}

function stopBirdAudio() {
  if (currentAudioElement) {
    currentAudioElement.pause();
    currentAudioElement = null;
  }
}

function getModeLabels(mode) {
  if (mode === 'tree') {
    return {
      title: 'じゅもく覚え',
      subtitle: '葉っぱフラッシュカード',
      resultWrongTitle: '間違えた項目',
      catalogTitle: '樹木一覧'
    };
  }

  if (mode === 'nakigoe') {
    return {
      title: 'なきごえ覚え',
      subtitle: '野鳥の鳴き声トレーニング',
      resultWrongTitle: '間違えた項目',
      catalogTitle: '鳴き声一覧'
    };
  }

  if (mode === 'shokusou') {
    return {
      title: 'しょくそう覚え',
      subtitle: currentSubMode === 'plant' ? 'しょくそう→むし' : 'むし→しょくそう',
      resultWrongTitle: '間違えた項目',
      catalogTitle: currentSubMode === 'plant' ? '植物一覧' : '昆虫一覧'
    };
  }

  return {
    title: 'とり覚え',
    subtitle: '野鳥フラッシュカード',
    resultWrongTitle: '間違えた項目',
    catalogTitle: '鳥一覧'
  };
}

function updateModeLabels() {
  var labels = getModeLabels(currentMode);
  var title = document.getElementById('home-title');
  var subtitle = document.getElementById('home-subtitle');
  var wrongTitle = document.getElementById('result-wrong-title');
  var catalogTitle = document.getElementById('catalog-title');

  if (title) title.textContent = labels.title;
  if (subtitle) subtitle.textContent = labels.subtitle;
  if (wrongTitle) wrongTitle.textContent = labels.resultWrongTitle;
  if (catalogTitle) catalogTitle.textContent = labels.catalogTitle;
}

// --------------- Screen management ---------------

function showScreen(id) {
  var screens = document.querySelectorAll('.screen');
  screens.forEach(function (s) { s.classList.remove('active'); });
  var target = document.getElementById(id);
  if (target) {
    target.classList.add('active');
    window.scrollTo(0, 0);
  }
}

// --------------- Home stats ---------------

async function updateHomeStats() {
  try {
    var activeData = getActiveData();
    var activeIds = new Set(activeData.map(function (d) { return d.id; }));
    var allProgress = await getAllProgress();
    // Filter progress to only current mode's items
    var modeProgress = allProgress.filter(function (p) { return activeIds.has(p.id); });
    var mastered = modeProgress.filter(function (p) { return p.mastered; }).length;
    var attempts = modeProgress.reduce(function (sum, p) { return sum + (p.totalAttempts || 0); }, 0);

    document.getElementById('stat-total').textContent = activeData.length;
    document.getElementById('stat-mastered').textContent = mastered;
    document.getElementById('stat-attempts').textContent = attempts;
  } catch (e) {
    console.error('updateHomeStats error:', e);
    document.getElementById('stat-total').textContent = getActiveData().length;
    document.getElementById('stat-mastered').textContent = '—';
    document.getElementById('stat-attempts').textContent = '—';
  }
}

// --------------- Memorize screen ---------------

function renderMemorizeGrid() {
  var grid = document.getElementById('memorize-grid');
  var birds = currentQuestions.length ? currentQuestions : [];
  var isAnswerPhase = memorizePhase === 'grid-answer';
  var isNakigoe = isNakigoeMode();

  grid.innerHTML = '';

  if (isShokusouMode()) {
    grid.classList.add('shokusou-grid');
  } else {
    grid.classList.remove('shokusou-grid');
  }

  birds.forEach(function (bird, idx) {
    var card = document.createElement('div');
    card.className = 'bird-card';
    if (isShokusouMode()) card.classList.add('shokusou-card');
    card.dataset.idx = idx;

    if (isNakigoe) {
      // Nakigoe mode: show speaker icon + call type
      var audioArea = document.createElement('div');
      audioArea.className = 'audio-play-area';

      var speakerBtn = document.createElement('button');
      speakerBtn.className = 'speaker-btn';
      speakerBtn.innerHTML = '<svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
      speakerBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        playBirdAudio(bird.audio);
      });

      var callTypeEl = document.createElement('span');
      callTypeEl.className = 'call-type-label';
      callTypeEl.textContent = bird.callType;

      audioArea.appendChild(speakerBtn);
      audioArea.appendChild(callTypeEl);
      card.appendChild(audioArea);
    } else {
      // Image mode
      var img = document.createElement('img');
      img.src = bird.image;
      img.alt = isAnswerPhase ? '?' : bird.name;
      img.loading = 'lazy';
      card.appendChild(img);
    }

    if (isAnswerPhase) {
      if (isShokusouMode()) {
        var answerGroup = document.createElement('div');
        answerGroup.className = 'shokusou-answer-group';

        var nameLabel = document.createElement('span');
        nameLabel.className = 'answer-label';
        nameLabel.textContent = currentSubMode === 'insect' ? '昆虫名' : '植物名';
        answerGroup.appendChild(nameLabel);

        var nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.placeholder = 'カタカナ';
        nameInput.dataset.idx = idx;
        nameInput.dataset.field = 'name';
        answerGroup.appendChild(nameInput);

        var relatedNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
        if (relatedNames) {
          relatedNames.forEach(function(rn, ri) {
            var label = document.createElement('span');
            label.className = 'answer-label';
            label.textContent = (currentSubMode === 'insect' ? '食草' : '昆虫') + (ri + 1);
            answerGroup.appendChild(label);

            var inp = document.createElement('input');
            inp.type = 'text';
            inp.placeholder = 'カタカナ';
            inp.dataset.idx = idx;
            inp.dataset.field = 'related_' + ri;
            answerGroup.appendChild(inp);
          });
        }

        card.appendChild(answerGroup);
      } else {
        var input = document.createElement('input');
        input.type = 'text';
        input.className = 'bird-card-input';
        input.placeholder = 'カタカナ';
        input.dataset.idx = idx;

        input.addEventListener('keydown', function (e) {
          if (e.key === 'Enter') {
            var inputs = grid.querySelectorAll('.bird-card-input');
            var next = inputs[idx + 1];
            if (next) {
              next.focus();
            } else {
              input.blur();
            }
          }
        });

        card.appendChild(input);
      }
    } else {
      if (isShokusouMode()) {
        var nameEl = document.createElement('p');
        nameEl.className = 'bird-card-name';
        nameEl.textContent = bird.name;
        card.appendChild(nameEl);

        var relatedNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
        if (relatedNames) {
          var relatedEl = document.createElement('p');
          relatedEl.className = 'shokusou-related-names';
          relatedEl.textContent = relatedNames.join('、');
          card.appendChild(relatedEl);
        }

        card.addEventListener('click', function () { openOverlay(bird); });
      } else {
        var nameEl = document.createElement('p');
        nameEl.className = 'bird-card-name';
        nameEl.textContent = isNakigoe ? bird.name : bird.name;
        card.appendChild(nameEl);

        card.addEventListener('click', function () {
          if (isNakigoe) {
            playBirdAudio(bird.audio);
          } else {
            openOverlay(bird);
          }
        });
      }
    }

    grid.appendChild(card);
  });
}

function openOverlay(bird) {
  var overlay = document.getElementById('memorize-overlay');
  document.getElementById('overlay-img').src = bird.image;
  document.getElementById('overlay-img').alt = bird.name;
  document.getElementById('overlay-name').textContent = bird.name;
  overlay.classList.add('active');
}

function closeOverlay() {
  var overlay = document.getElementById('memorize-overlay');
  overlay.classList.remove('active');
}

// --------------- Start test ---------------

function getRandomFallbackQuestions(data, questionCount) {
  var shuffled = data.slice();
  shuffleArray(shuffled);
  return shuffled.slice(0, Math.min(questionCount, shuffled.length));
}

function getQuestionIds(items) {
  return items.map(function (item) { return item.id; });
}

function isSameQuestionOrder(items, previousIds) {
  var ids = getQuestionIds(items);
  if (!previousIds || ids.length !== previousIds.length) return false;

  for (var i = 0; i < ids.length; i++) {
    if (ids[i] !== previousIds[i]) return false;
  }
  return true;
}

function getRecentHistory(mode) {
  return recentSessionHistoryByMode[mode] || [];
}

function haveSameQuestionSet(items, previousIds) {
  var ids = getQuestionIds(items);
  if (!previousIds || ids.length !== previousIds.length) return false;

  var previousSet = new Set(previousIds);
  for (var i = 0; i < ids.length; i++) {
    if (!previousSet.has(ids[i])) return false;
  }
  return true;
}

function calculateOverlapRatio(items, previousIds) {
  var ids = getQuestionIds(items);
  if (!ids.length || !previousIds || !previousIds.length) return 0;

  var previousSet = new Set(previousIds);
  var overlap = 0;

  for (var i = 0; i < ids.length; i++) {
    if (previousSet.has(ids[i])) overlap++;
  }

  return overlap / Math.min(ids.length, previousIds.length);
}

function isTooSimilarToRecentHistory(items, history) {
  if (!history || history.length === 0) return false;

  for (var i = 0; i < history.length; i++) {
    var previousIds = history[i];

    if (haveSameQuestionSet(items, previousIds)) {
      return true;
    }

    if (items.length >= 8 && calculateOverlapRatio(items, previousIds) >= 0.8) {
      return true;
    }
  }

  return false;
}

function rememberSessionQuestions(mode, items) {
  var ids = getQuestionIds(items);
  lastSessionIdsByMode[mode] = ids;

  var history = getRecentHistory(mode).slice();
  history.unshift(ids);
  recentSessionHistoryByMode[mode] = history.slice(0, 5);
}

function normalizeSessionOptions(options) {
  return {
    randomizeAnswerOrder: Boolean(options && options.randomizeAnswerOrder)
  };
}

function resetAnswerState() {
  testAnswers = currentQuestions.map(function (bird) {
    return { birdId: bird.id, userInput: '', isCorrect: null };
  });
  currentIndex = 0;
  singleAnswered = currentQuestions.map(function () { return false; });
}

function shuffleQuestionsForAnswerPhase() {
  if (currentQuestions.length <= 1) return;

  var originalIds = getQuestionIds(currentQuestions);
  var shuffled = currentQuestions.slice();

  for (var attempt = 0; attempt < 8; attempt++) {
    shuffled = shuffleArray(currentQuestions.slice());
    if (!isSameQuestionOrder(shuffled, originalIds)) {
      currentQuestions = shuffled;
      return;
    }
  }

  shuffled = currentQuestions.slice(1).concat(currentQuestions[0]);
  currentQuestions = shuffled;
}

async function pickSessionQuestions(data, settings) {
  var previousIds = lastSessionIdsByMode[getSessionModeKey()] || [];
  var recentHistory = getRecentHistory(getSessionModeKey());
  var selected = [];
  var bestCandidate = [];
  var bestCandidateOverlap = Infinity;

  for (var attempt = 0; attempt < 20; attempt++) {
    selected = await selectQuestions(data, settings);

    if (selected.length === 0) {
      continue;
    }

    var overlap = recentHistory.length
      ? calculateOverlapRatio(selected, recentHistory[0])
      : 0;

    if (overlap < bestCandidateOverlap) {
      bestCandidate = selected.slice();
      bestCandidateOverlap = overlap;
    }

    if (
      !isSameQuestionOrder(selected, previousIds) &&
      !isTooSimilarToRecentHistory(selected, recentHistory)
    ) {
      break;
    }
  }

  if (
    selected.length === 0 ||
    isSameQuestionOrder(selected, previousIds) ||
    isTooSimilarToRecentHistory(selected, recentHistory)
  ) {
    selected = bestCandidate.length ? bestCandidate.slice() : selected;
  }

  if (isSameQuestionOrder(selected, previousIds) && selected.length > 1) {
    selected = shuffleArray(selected.slice());
  }

  rememberSessionQuestions(getSessionModeKey(), selected);
  return selected;
}

async function initializeSession() {
  currentSettings = loadSettings();
  var data = getActiveData();

  try {
    currentQuestions = await pickSessionQuestions(data, currentSettings);
  } catch (e) {
    console.error('selectQuestions error:', e);
    currentQuestions = getRandomFallbackQuestions(data, currentSettings.questionCount);
    rememberSessionQuestions(getSessionModeKey(), currentQuestions);
  }

  resetAnswerState();
  answerOrderShuffled = false;
}

function updateMemorizeActions() {
  var btnStartTest = document.getElementById('btn-start-test');
  var btnSubmitMemorize = document.getElementById('btn-submit-memorize-grid');

  if (btnStartTest) {
    btnStartTest.style.display = memorizePhase === 'memorize' ? '' : 'none';
  }

  if (btnSubmitMemorize) {
    btnSubmitMemorize.style.display = memorizePhase === 'grid-answer' ? '' : 'none';
  }
}

async function startSession(options) {
  closeOverlay();
  stopBirdAudio();
  currentSessionOptions = normalizeSessionOptions(options);
  lastSessionOptions = normalizeSessionOptions(options);
  await initializeSession();
  memorizePhase = 'memorize';
  renderMemorizeGrid();
  updateMemorizeActions();
  showScreen('screen-memorize');
}

function beginAnswerPhase() {
  if (currentQuestions.length === 0) return;

  closeOverlay();

  if (currentSessionOptions.randomizeAnswerOrder && !answerOrderShuffled) {
    shuffleQuestionsForAnswerPhase();
    resetAnswerState();
    answerOrderShuffled = true;
  }

  if (currentSettings && currentSettings.displayMode === 'single') {
    renderTestSingle();
    showScreen('screen-test-single');
  } else {
    memorizePhase = 'grid-answer';
    renderMemorizeGrid();
    updateMemorizeActions();
  }
}

// --------------- Test Grid mode ---------------

function renderTestGrid() {
  var grid = document.getElementById('test-grid');
  var isNakigoe = isNakigoeMode();
  grid.innerHTML = '';

  currentQuestions.forEach(function (bird, idx) {
    var card = document.createElement('div');
    card.className = 'bird-card';
    card.dataset.idx = idx;

    if (isNakigoe) {
      var audioArea = document.createElement('div');
      audioArea.className = 'audio-play-area';

      var speakerBtn = document.createElement('button');
      speakerBtn.className = 'speaker-btn';
      speakerBtn.innerHTML = '<svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
      speakerBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        playBirdAudio(bird.audio);
      });

      var callTypeEl = document.createElement('span');
      callTypeEl.className = 'call-type-label';
      callTypeEl.textContent = bird.callType;

      audioArea.appendChild(speakerBtn);
      audioArea.appendChild(callTypeEl);
      card.appendChild(audioArea);
    } else {
      var img = document.createElement('img');
      img.src = bird.image;
      img.alt = '?';
      img.loading = 'lazy';
      card.appendChild(img);
    }

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'bird-card-input';
    input.placeholder = 'カタカナ';
    input.dataset.idx = idx;

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        var inputs = grid.querySelectorAll('.bird-card-input');
        var next = inputs[idx + 1];
        if (next) {
          next.focus();
        } else {
          input.blur();
        }
      }
    });

    card.appendChild(input);
    grid.appendChild(card);
  });
}

async function submitGridTest(gridId, submitButtonId) {
  var settings = currentSettings || loadSettings();
  var grid = document.getElementById(gridId || 'test-grid');
  var inputs = grid.querySelectorAll('.bird-card-input');
  var cards = grid.querySelectorAll('.bird-card');

  var correctCount = 0;

  for (var i = 0; i < currentQuestions.length; i++) {
    var bird = currentQuestions[i];
    var card = cards[i];

    if (isShokusouMode()) {
      var shokusouInputs = card.querySelectorAll('.shokusou-answer-group input');
      var allCorrect = true;

      if (shokusouInputs[0]) {
        var nameOk = checkAnswer(shokusouInputs[0].value, bird.name);
        shokusouInputs[0].classList.add(nameOk ? 'correct' : 'wrong');
        if (!nameOk) {
          shokusouInputs[0].value = shokusouInputs[0].value + ' → ' + bird.name;
          allCorrect = false;
        }
        shokusouInputs[0].disabled = true;
      }

      var relNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
      for (var ri = 0; ri < relNames.length; ri++) {
        var relInp = shokusouInputs[ri + 1];
        if (relInp) {
          var relOk = checkAnswer(relInp.value, relNames[ri]);
          relInp.classList.add(relOk ? 'correct' : 'wrong');
          if (!relOk) {
            relInp.value = relInp.value + ' → ' + relNames[ri];
            allCorrect = false;
          }
          relInp.disabled = true;
        }
      }

      if (allCorrect) correctCount++;
      testAnswers[i].isCorrect = allCorrect;
      testAnswers[i].userInput = shokusouInputs[0] ? shokusouInputs[0].value : '';

      var nameEl = card.querySelector('.bird-card-name');
      if (!nameEl) {
        nameEl = document.createElement('p');
        nameEl.className = 'bird-card-name';
        card.appendChild(nameEl);
      }
      nameEl.textContent = bird.name;
      card.classList.add(allCorrect ? 'correct' : 'wrong');

      try { await updateProgress(bird.id, allCorrect, settings.masteryThreshold); } catch(e) {}

      continue;
    }

    var userInput = inputs[i] ? inputs[i].value : '';
    var isCorrect = checkAnswer(userInput, bird.name);

    if (isCorrect) correctCount++;

    testAnswers[i].userInput = userInput;
    testAnswers[i].isCorrect = isCorrect;

    if (card) {
      card.classList.remove('correct', 'wrong');
      card.classList.add(isCorrect ? 'correct' : 'wrong');

      var nameEl = card.querySelector('.bird-card-name');
      if (!nameEl) {
        nameEl = document.createElement('p');
        nameEl.className = 'bird-card-name';
        card.appendChild(nameEl);
      }
      nameEl.textContent = bird.name;
    }

    if (inputs[i]) {
      inputs[i].disabled = true;
    }

    try {
      await updateProgress(bird.id, isCorrect, settings.masteryThreshold);
    } catch (e) {
      console.error('updateProgress error:', e);
    }
  }

  // Hide submit button
  var btnSubmit = document.getElementById(submitButtonId || 'btn-submit-grid');
  if (btnSubmit) btnSubmit.style.display = 'none';

  // Navigate to result after delay
  setTimeout(function () {
    showResult(correctCount, currentQuestions.length);
  }, 2000);
}

// --------------- Test Single mode ---------------

function renderTestSingle() {
  updateSingleDisplay();
}

function updateSingleDisplay() {
  if (currentQuestions.length === 0) return;

  var bird = currentQuestions[currentIndex];
  var isNakigoe = isNakigoeMode();

  // Update counter
  var counter = document.getElementById('single-counter');
  if (counter) {
    counter.textContent = (currentIndex + 1) + ' / ' + currentQuestions.length;
  }

  // Update image or audio area
  var img = document.getElementById('single-img');
  var singleAudioArea = document.getElementById('single-audio-area');

  if (isNakigoe) {
    if (img) img.style.display = 'none';
    if (!singleAudioArea) {
      singleAudioArea = document.createElement('div');
      singleAudioArea.id = 'single-audio-area';
      singleAudioArea.className = 'single-audio-area';
      var singleCard = document.querySelector('.single-card');
      if (singleCard && img) {
        singleCard.insertBefore(singleAudioArea, img.nextSibling);
      }
    }
    singleAudioArea.style.display = '';
    singleAudioArea.innerHTML = '';

    var speakerBtn = document.createElement('button');
    speakerBtn.className = 'speaker-btn speaker-btn-large';
    speakerBtn.innerHTML = '<svg viewBox="0 0 24 24" width="64" height="64" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
    speakerBtn.addEventListener('click', function () {
      playBirdAudio(bird.audio);
    });

    var callTypeEl = document.createElement('span');
    callTypeEl.className = 'call-type-label-large';
    callTypeEl.textContent = bird.callType;

    singleAudioArea.appendChild(speakerBtn);
    singleAudioArea.appendChild(callTypeEl);
  } else {
    if (img) {
      img.style.display = '';
      img.src = bird.image;
      img.alt = '?';
    }
    if (singleAudioArea) singleAudioArea.style.display = 'none';
  }

  // Reset input area visibility
  var answerArea = document.getElementById('single-answer-area');
  var feedback = document.getElementById('single-feedback');
  var input = document.getElementById('single-input');

  if (isShokusouMode() && !singleAnswered[currentIndex]) {
    answerArea.innerHTML = '';
    answerArea.style.display = '';

    var answerGroup = document.createElement('div');
    answerGroup.className = 'shokusou-answer-group';

    var nameLabel = document.createElement('span');
    nameLabel.className = 'answer-label';
    nameLabel.textContent = currentSubMode === 'insect' ? '昆虫名' : '植物名';
    answerGroup.appendChild(nameLabel);

    var nameInput = document.createElement('input');
    nameInput.type = 'text';
    nameInput.className = 'answer-input';
    nameInput.id = 'single-input';
    nameInput.placeholder = 'カタカナで入力';
    nameInput.dataset.field = 'name';
    answerGroup.appendChild(nameInput);

    var relNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
    if (relNames) {
      relNames.forEach(function(rn, ri) {
        var label = document.createElement('span');
        label.className = 'answer-label';
        label.textContent = (currentSubMode === 'insect' ? '食草' : '昆虫') + (ri + 1);
        answerGroup.appendChild(label);

        var inp = document.createElement('input');
        inp.type = 'text';
        inp.className = 'answer-input';
        inp.placeholder = 'カタカナで入力';
        inp.dataset.field = 'related_' + ri;
        answerGroup.appendChild(inp);
      });
    }

    var submitBtn = document.createElement('button');
    submitBtn.className = 'btn btn-primary';
    submitBtn.id = 'btn-single-submit';
    submitBtn.textContent = '答え合わせ';
    submitBtn.addEventListener('click', submitSingleAnswer);

    answerArea.appendChild(answerGroup);
    answerArea.appendChild(submitBtn);

    if (feedback) {
      feedback.textContent = '';
      feedback.className = 'single-feedback';
    }
  } else if (singleAnswered[currentIndex]) {
    if (answerArea) answerArea.style.display = 'none';
    if (input) input.value = testAnswers[currentIndex].userInput;
    if (feedback) {
      feedback.textContent = testAnswers[currentIndex].isCorrect
        ? '正解！ ' + bird.name
        : '不正解… 正解は「' + bird.name + '」';
      feedback.className = 'single-feedback ' + (testAnswers[currentIndex].isCorrect ? 'correct' : 'wrong');
    }
  } else {
    if (answerArea) answerArea.style.display = '';
    if (input) input.value = '';
    if (feedback) {
      feedback.textContent = '';
      feedback.className = 'single-feedback';
    }
  }
}

async function submitSingleAnswer() {
  if (singleAnswered[currentIndex]) return;

  var settings = currentSettings || loadSettings();
  var bird = currentQuestions[currentIndex];
  var isCorrect;

  if (isShokusouMode()) {
    var answerGroup = document.querySelector('#single-answer-area .shokusou-answer-group');
    var inputs = answerGroup ? answerGroup.querySelectorAll('input') : [];
    var allCorrect = true;
    var feedbackParts = [];

    if (inputs[0]) {
      var nameOk = checkAnswer(inputs[0].value, bird.name);
      inputs[0].classList.add(nameOk ? 'correct' : 'wrong');
      if (!nameOk) {
        feedbackParts.push(inputs[0].value + ' → ' + bird.name);
        allCorrect = false;
      }
      inputs[0].disabled = true;
    }

    var relNames = currentSubMode === 'insect' ? bird.foodPlants : bird.insects;
    for (var ri = 0; ri < relNames.length; ri++) {
      var relInp = inputs[ri + 1];
      if (relInp) {
        var relOk = checkAnswer(relInp.value, relNames[ri]);
        relInp.classList.add(relOk ? 'correct' : 'wrong');
        if (!relOk) {
          feedbackParts.push(relInp.value + ' → ' + relNames[ri]);
          allCorrect = false;
        }
        relInp.disabled = true;
      }
    }

    isCorrect = allCorrect;
    testAnswers[currentIndex].userInput = inputs[0] ? inputs[0].value : '';
    testAnswers[currentIndex].isCorrect = isCorrect;
    singleAnswered[currentIndex] = true;

    var feedback = document.getElementById('single-feedback');
    if (feedback) {
      feedback.textContent = isCorrect
        ? '正解！ ' + bird.name
        : '不正解… 正解は「' + bird.name + '」';
      feedback.className = 'single-feedback ' + (isCorrect ? 'correct' : 'wrong');
    }

    var answerArea = document.getElementById('single-answer-area');
    if (answerArea) answerArea.style.display = 'none';
  } else {
    var input = document.getElementById('single-input');
    var userInput = input ? input.value : '';
    isCorrect = checkAnswer(userInput, bird.name);

    testAnswers[currentIndex].userInput = userInput;
    testAnswers[currentIndex].isCorrect = isCorrect;
    singleAnswered[currentIndex] = true;

    var feedback = document.getElementById('single-feedback');
    if (feedback) {
      feedback.textContent = isCorrect
        ? '正解！ ' + bird.name
        : '不正解… 正解は「' + bird.name + '」';
      feedback.className = 'single-feedback ' + (isCorrect ? 'correct' : 'wrong');
    }

    var answerArea = document.getElementById('single-answer-area');
    if (answerArea) answerArea.style.display = 'none';
  }

  // Update DB progress
  try {
    await updateProgress(bird.id, isCorrect, settings.masteryThreshold);
  } catch (e) {
    console.error('updateProgress error:', e);
  }

  // Check if all answered
  var allAnswered = singleAnswered.every(function (v) { return v; });
  if (allAnswered) {
    var correctCount = testAnswers.filter(function (a) { return a.isCorrect; }).length;
    setTimeout(function () {
      showResult(correctCount, currentQuestions.length);
    }, 1500);
  }
}

// --------------- Result screen ---------------

function showResult(correct, total) {
  memorizePhase = 'idle';
  var rate = total > 0 ? Math.round((correct / total) * 100) : 0;

  document.getElementById('result-score').textContent = correct + ' / ' + total;
  document.getElementById('result-rate').textContent = rate + '%';

  // Wrong answers list
  var wrongItems = testAnswers.filter(function (a) { return !a.isCorrect; });
  var wrongBlock = document.getElementById('result-wrong-block');
  var wrongList = document.getElementById('result-wrong-list');

  wrongList.innerHTML = '';

  if (wrongItems.length === 0) {
    if (wrongBlock) wrongBlock.style.display = 'none';
  } else {
    if (wrongBlock) wrongBlock.style.display = '';

    wrongItems.forEach(function (answer) {
      var bird = getActiveData().find(function (b) { return b.id === answer.birdId; });
      if (!bird) return;

      var li = document.createElement('li');
      li.className = 'result-wrong-item';

      if (isNakigoeMode() && bird.audio) {
        var audioBtn = document.createElement('button');
        audioBtn.className = 'result-speaker-btn';
        audioBtn.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
        audioBtn.addEventListener('click', function () {
          playBirdAudio(bird.audio);
        });
        li.appendChild(audioBtn);
      } else {
        var img = document.createElement('img');
        img.src = bird.image;
        img.alt = bird.name;
        li.appendChild(img);
      }

      var info = document.createElement('div');
      info.className = 'result-wrong-item-info';

      var nameEl = document.createElement('span');
      nameEl.className = 'result-wrong-item-name';
      nameEl.textContent = isNakigoeMode() && bird.callType
        ? bird.callType + '：' + bird.name
        : bird.name;

      var answerEl = document.createElement('span');
      answerEl.className = 'result-wrong-item-answer';
      answerEl.textContent = answer.userInput
        ? '入力: 「' + answer.userInput + '」'
        : '（未入力）';

      info.appendChild(nameEl);
      info.appendChild(answerEl);
      li.appendChild(info);
      wrongList.appendChild(li);
    });
  }

  showScreen('screen-result');
}

// --------------- Catalog screen ---------------

async function setItemMastered(itemId, mastered) {
  var settings = loadSettings();
  var record = await getProgress(itemId);

  if (!record) {
    record = {
      id: itemId,
      correctStreak: 0,
      totalAttempts: 0,
      correctTotal: 0,
      mastered: false,
      lastSeen: null
    };
  }

  record.mastered = mastered;
  if (mastered) {
    record.correctStreak = Math.max(record.correctStreak || 0, settings.masteryThreshold);
  } else if ((record.correctStreak || 0) >= settings.masteryThreshold) {
    record.correctStreak = 0;
  }

  await saveProgress(record);
  return record;
}

async function renderCatalog() {
  var list = document.getElementById('catalog-list');
  if (!list) return;

  updateModeLabels();
  list.innerHTML = '';

  var data = getActiveData();
  var allProgress = await getAllProgress();
  var progressMap = {};

  allProgress.forEach(function (record) {
    progressMap[record.id] = record;
  });

  var isNakigoe = currentMode === 'nakigoe';

  data.forEach(function (item) {
    var progress = progressMap[item.id];
    var isMastered = Boolean(progress && progress.mastered);

    var row = document.createElement('div');
    row.className = 'catalog-item' + (isMastered ? ' mastered' : '');
    var mediaEl;

    if (isNakigoe && item.audio) {
      var audioBtn = document.createElement('button');
      audioBtn.className = 'catalog-speaker-btn';
      audioBtn.innerHTML = '<svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>';
      audioBtn.addEventListener('click', function () {
        playBirdAudio(item.audio);
      });
      mediaEl = audioBtn;
    } else {
      var img = document.createElement('img');
      img.src = item.image;
      img.alt = item.name;
      img.loading = 'lazy';
      mediaEl = img;
    }

    var main = document.createElement('div');
    main.className = 'catalog-item-main';

    var nameEl = document.createElement('span');
    nameEl.className = 'catalog-item-name';
    nameEl.textContent = isNakigoe && item.callType
      ? item.callType + '：' + item.name
      : item.name;

    var metaEl = document.createElement('span');
    metaEl.className = 'catalog-item-meta';
    metaEl.textContent = item.tags && item.tags.length ? item.tags.join(' / ') : (item.callType || item.category);

    var toggle = document.createElement('label');
    toggle.className = 'catalog-toggle';

    var checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = isMastered;

    var toggleText = document.createElement('span');
    toggleText.textContent = '覚えた';

    checkbox.addEventListener('change', function () {
      var nextChecked = checkbox.checked;
      checkbox.disabled = true;

      setItemMastered(item.id, nextChecked).then(function () {
        row.classList.toggle('mastered', nextChecked);
        updateHomeStats();
      }).catch(function (e) {
        checkbox.checked = !nextChecked;
        alert('チェックの更新に失敗しました: ' + e.message);
      }).finally(function () {
        checkbox.disabled = false;
      });
    });

    main.appendChild(nameEl);
    main.appendChild(metaEl);
    toggle.appendChild(checkbox);
    toggle.appendChild(toggleText);
    row.appendChild(mediaEl);
    row.appendChild(main);
    row.appendChild(toggle);
    list.appendChild(row);
  });
}

// --------------- Settings ---------------

function renderSettings() {
  var s = loadSettings();

  // Question count
  var countInput = document.getElementById('setting-count');
  if (countInput) countInput.value = s.questionCount;

  // Display mode toggle
  var displayBtns = document.querySelectorAll('#toggle-display-mode .toggle-btn');
  displayBtns.forEach(function (btn) {
    btn.classList.toggle('active', btn.dataset.value === s.displayMode);
  });

  // Mastery threshold toggle
  var masteryBtns = document.querySelectorAll('#toggle-mastery .toggle-btn');
  masteryBtns.forEach(function (btn) {
    btn.classList.toggle('active', Number(btn.dataset.value) === s.masteryThreshold);
  });

  // Include mastered toggle
  var inclBtn = document.getElementById('toggle-include-mastered');
  if (inclBtn) {
    inclBtn.classList.toggle('active', s.includeMastered);
    inclBtn.textContent = s.includeMastered ? 'ON' : 'OFF';
    inclBtn.dataset.value = String(s.includeMastered);
  }

  // Prioritize wrong toggle
  var prioBtn = document.getElementById('toggle-prioritize-wrong');
  if (prioBtn) {
    prioBtn.classList.toggle('active', s.prioritizeWrong);
    prioBtn.textContent = s.prioritizeWrong ? 'ON' : 'OFF';
    prioBtn.dataset.value = String(s.prioritizeWrong);
  }
}

function setupSettingsEvents() {
  // Question count
  var countInput = document.getElementById('setting-count');
  if (countInput) {
    countInput.addEventListener('change', function () {
      var s = loadSettings();
      var val = parseInt(this.value, 10);
      if (!isNaN(val) && val >= 1) {
        s.questionCount = val;
        saveSettings(s);
        this.value = s.questionCount;
      }
    });
  }

  // Display mode toggle
  var displayBtns = document.querySelectorAll('#toggle-display-mode .toggle-btn');
  displayBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var s = loadSettings();
      s.displayMode = btn.dataset.value;
      saveSettings(s);
      displayBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
    });
  });

  // Mastery threshold toggle
  var masteryBtns = document.querySelectorAll('#toggle-mastery .toggle-btn');
  masteryBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var s = loadSettings();
      s.masteryThreshold = Number(btn.dataset.value);
      saveSettings(s);
      masteryBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
    });
  });

  // Include mastered toggle
  var inclBtn = document.getElementById('toggle-include-mastered');
  if (inclBtn) {
    inclBtn.addEventListener('click', function () {
      var s = loadSettings();
      s.includeMastered = !s.includeMastered;
      saveSettings(s);
      inclBtn.classList.toggle('active', s.includeMastered);
      inclBtn.textContent = s.includeMastered ? 'ON' : 'OFF';
      inclBtn.dataset.value = String(s.includeMastered);
    });
  }

  // Prioritize wrong toggle
  var prioBtn = document.getElementById('toggle-prioritize-wrong');
  if (prioBtn) {
    prioBtn.addEventListener('click', function () {
      var s = loadSettings();
      s.prioritizeWrong = !s.prioritizeWrong;
      saveSettings(s);
      prioBtn.classList.toggle('active', s.prioritizeWrong);
      prioBtn.textContent = s.prioritizeWrong ? 'ON' : 'OFF';
      prioBtn.dataset.value = String(s.prioritizeWrong);
    });
  }

  // Export
  var btnExport = document.getElementById('btn-export');
  if (btnExport) {
    btnExport.addEventListener('click', function () {
      exportData().then(function (json) {
        var blob = new Blob([json], { type: 'application/json' });
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'torioboe_backup.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }).catch(function (e) {
        alert('エクスポートに失敗しました: ' + e.message);
      });
    });
  }

  // Import
  var btnImport = document.getElementById('btn-import');
  var inputImport = document.getElementById('input-import');
  if (btnImport && inputImport) {
    btnImport.addEventListener('click', function () {
      inputImport.click();
    });
    inputImport.addEventListener('change', function () {
      var file = this.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function (e) {
        importData(e.target.result).then(function () {
          alert('インポートが完了しました');
          renderSettings();
          updateHomeStats();
        }).catch(function (err) {
          alert('インポートに失敗しました: ' + err.message);
        });
      };
      reader.readAsText(file);
      inputImport.value = '';
    });
  }

  // Reset
  var btnReset = document.getElementById('btn-reset');
  if (btnReset) {
    btnReset.addEventListener('click', function () {
      if (!confirm('すべての学習データをリセットしますか？\nこの操作は取り消せません。')) return;
      clearAllProgress().then(function () {
        alert('リセットしました');
        updateHomeStats();
      }).catch(function (e) {
        alert('リセットに失敗しました: ' + e.message);
      });
    });
  }
}

// --------------- Global event setup ---------------

function setupEvents() {
  // ----- Home -----
  var btnStartSession = document.getElementById('btn-start-session');
  if (btnStartSession) {
    btnStartSession.addEventListener('click', function () {
      startSession({ randomizeAnswerOrder: false });
    });
  }

  var btnStartSessionRandom = document.getElementById('btn-start-session-random');
  if (btnStartSessionRandom) {
    btnStartSessionRandom.addEventListener('click', function () {
      startSession({ randomizeAnswerOrder: true });
    });
  }

  var btnCatalogHome = document.getElementById('btn-catalog-home');
  if (btnCatalogHome) {
    btnCatalogHome.addEventListener('click', function () {
      renderCatalog();
      showScreen('screen-catalog');
    });
  }

  // ----- Mode switcher -----
  var modeBtns = document.querySelectorAll('.mode-btn');
  var submodeSwitcher = document.getElementById('submode-switcher');
  modeBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      modeBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      currentMode = btn.getAttribute('data-mode');
      if (submodeSwitcher) {
        submodeSwitcher.style.display = (currentMode === 'shokusou') ? '' : 'none';
      }
      updateModeLabels();
      updateHomeStats();
    });
  });

  if (submodeSwitcher) {
    submodeSwitcher.querySelectorAll('.submode-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        currentSubMode = btn.dataset.submode;
        submodeSwitcher.querySelectorAll('.submode-btn').forEach(function(b) {
          b.classList.toggle('active', b.dataset.submode === currentSubMode);
        });
        updateModeLabels();
        updateHomeStats();
      });
    });
  }

  var btnSettingsHome = document.getElementById('btn-settings-home');
  if (btnSettingsHome) {
    btnSettingsHome.addEventListener('click', function () {
      renderSettings();
      showScreen('screen-settings');
    });
  }

  // ----- Memorize -----
  var btnBackMemorize = document.getElementById('btn-back-memorize');
  if (btnBackMemorize) {
    btnBackMemorize.addEventListener('click', function () {
      memorizePhase = 'idle';
      closeOverlay();
      showScreen('screen-home');
    });
  }

  var btnStartTest = document.getElementById('btn-start-test');
  if (btnStartTest) {
    btnStartTest.addEventListener('click', function () {
      beginAnswerPhase();
    });
  }

  var btnSubmitMemorize = document.getElementById('btn-submit-memorize-grid');
  if (btnSubmitMemorize) {
    btnSubmitMemorize.addEventListener('click', function () {
      submitGridTest('memorize-grid', 'btn-submit-memorize-grid');
    });
  }

  // Overlay close
  var overlayClose = document.getElementById('overlay-close');
  if (overlayClose) {
    overlayClose.addEventListener('click', function () {
      closeOverlay();
    });
  }

  var overlay = document.getElementById('memorize-overlay');
  if (overlay) {
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeOverlay();
    });
  }

  // ----- Test Grid -----
  var btnBackTestGrid = document.getElementById('btn-back-test-grid');
  if (btnBackTestGrid) {
    btnBackTestGrid.addEventListener('click', function () {
      showScreen('screen-home');
    });
  }

  var btnSubmitGrid = document.getElementById('btn-submit-grid');
  if (btnSubmitGrid) {
    btnSubmitGrid.addEventListener('click', function () {
      submitGridTest('test-grid', 'btn-submit-grid');
    });
  }

  // ----- Test Single -----
  var btnBackTestSingle = document.getElementById('btn-back-test-single');
  if (btnBackTestSingle) {
    btnBackTestSingle.addEventListener('click', function () {
      memorizePhase = 'idle';
      showScreen('screen-home');
    });
  }

  var btnSingleSubmit = document.getElementById('btn-single-submit');
  if (btnSingleSubmit) {
    btnSingleSubmit.addEventListener('click', function () {
      submitSingleAnswer();
    });
  }

  var singleInput = document.getElementById('single-input');
  if (singleInput) {
    singleInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') submitSingleAnswer();
    });
  }

  var btnSinglePrev = document.getElementById('btn-single-prev');
  if (btnSinglePrev) {
    btnSinglePrev.addEventListener('click', function () {
      if (currentIndex > 0) {
        currentIndex--;
        updateSingleDisplay();
      }
    });
  }

  var btnSingleNext = document.getElementById('btn-single-next');
  if (btnSingleNext) {
    btnSingleNext.addEventListener('click', function () {
      if (currentIndex < currentQuestions.length - 1) {
        currentIndex++;
        updateSingleDisplay();
      }
    });
  }

  // ----- Result -----
  var btnRetry = document.getElementById('btn-retry');
  if (btnRetry) {
    btnRetry.addEventListener('click', function () {
      startSession(lastSessionOptions);
    });
  }

  var btnHome = document.getElementById('btn-home');
  if (btnHome) {
    btnHome.addEventListener('click', function () {
      memorizePhase = 'idle';
      updateModeLabels();
      updateHomeStats();
      showScreen('screen-home');
    });
  }

  var btnBackCatalog = document.getElementById('btn-back-catalog');
  if (btnBackCatalog) {
    btnBackCatalog.addEventListener('click', function () {
      updateModeLabels();
      updateHomeStats();
      showScreen('screen-home');
    });
  }

  // ----- Settings -----
  var btnBackSettings = document.getElementById('btn-back-settings');
  if (btnBackSettings) {
    btnBackSettings.addEventListener('click', function () {
      showScreen('screen-home');
    });
  }

  // ----- Credits -----
  var btnCredits = document.getElementById('btn-credits');
  if (btnCredits) {
    btnCredits.addEventListener('click', function () {
      var creditsTitle = document.getElementById('credits-screen-title');
      var creditsIntro = document.getElementById('credits-intro-text');
      if (currentMode === 'nakigoe') {
        if (creditsTitle) creditsTitle.textContent = '音源クレジット';
        if (creditsIntro) creditsIntro.textContent = '鳥の鳴き声はすべてxeno-cantoのCC BY-NC 4.0ライセンス音源を使用しています。';
      } else {
        if (creditsTitle) creditsTitle.textContent = '写真クレジット';
        if (creditsIntro) creditsIntro.textContent = '鳥の写真はすべてWikimedia Commonsのフリーライセンス画像を使用しています。';
      }
      renderCredits();
      showScreen('screen-credits');
    });
  }

  var btnBackCredits = document.getElementById('btn-back-credits');
  if (btnBackCredits) {
    btnBackCredits.addEventListener('click', function () {
      showScreen('screen-settings');
    });
  }

  setupSettingsEvents();
}

// --------------- Credits screen ---------------

function renderCredits() {
  var list = document.getElementById('credits-list');
  if (!list) return;
  list.innerHTML = '';

  if (currentMode === 'nakigoe') {
    // Nakigoe credits from nakigoe_credits.json (embedded)
    var nakigoeCredits = typeof NAKIGOE_CREDITS !== 'undefined' ? NAKIGOE_CREDITS : {};
    var nakigoeData = typeof NAKIGOE_DATA !== 'undefined' ? NAKIGOE_DATA : [];
    nakigoeData.forEach(function (item) {
      var credit = nakigoeCredits[item.id] || null;
      var div = document.createElement('div');
      div.className = 'credit-item';

      var nameEl = document.createElement('span');
      nameEl.className = 'credit-name';
      nameEl.textContent = item.callType + '：' + item.name;

      var infoEl = document.createElement('span');
      infoEl.className = 'credit-info';
      if (credit) {
        infoEl.textContent = credit.recorder + ' / CC BY-NC 4.0';
      } else {
        infoEl.textContent = 'xeno-canto';
      }

      div.appendChild(nameEl);
      div.appendChild(infoEl);
      list.appendChild(div);
    });
    return;
  }

  var allData = [].concat(BIRD_DATA, typeof TREE_DATA !== 'undefined' ? TREE_DATA : []);
  allData.forEach(function (bird) {
    var credit = null;
    if (typeof BIRD_CREDITS !== 'undefined') {
      credit = BIRD_CREDITS[bird.id] || BIRD_CREDITS['tree_' + bird.id] || null;
    }
    var div = document.createElement('div');
    div.className = 'credit-item';

    var nameEl = document.createElement('span');
    nameEl.className = 'credit-name';
    nameEl.textContent = bird.name;

    var infoEl = document.createElement('span');
    infoEl.className = 'credit-info';
    if (credit) {
      infoEl.textContent = credit.artist + ' / ' + credit.license;
    } else {
      infoEl.textContent = 'Wikimedia Commons';
    }

    div.appendChild(nameEl);
    div.appendChild(infoEl);
    list.appendChild(div);
  });
}

// --------------- Lock screen ---------------

function setupLockScreen() {
  var btnSubmit = document.getElementById('btn-lock-submit');
  var idInput = document.getElementById('lock-id');
  var passInput = document.getElementById('lock-pass');
  var error = document.getElementById('lock-error');

  function tryUnlock() {
    if (idInput.value === '1' && passInput.value === '1') {
      showScreen('screen-home');
      updateHomeStats();
    } else {
      error.textContent = 'IDまたはパスワードが違います';
    }
  }

  btnSubmit.addEventListener('click', tryUnlock);
  passInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') tryUnlock();
  });
  idInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') passInput.focus();
  });
}

// --------------- Init ---------------

document.addEventListener('DOMContentLoaded', function () {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js");
  }
  setupEvents();
  setupLockScreen();
  updateModeLabels();
});
