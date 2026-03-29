// ============================================================
//  app.js — とり覚え main application logic
// ============================================================

// --------------- State ---------------
var currentQuestions = [];   // Array of bird objects selected for this session
var testAnswers = [];         // Array: { birdId, userInput, isCorrect }
var currentIndex = 0;         // Single mode: current question index
var singleAnswered = [];      // Single mode: answered flags per index

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
    var allProgress = await getAllProgress();
    var mastered = allProgress.filter(function (p) { return p.mastered; }).length;
    var attempts = allProgress.reduce(function (sum, p) { return sum + (p.totalAttempts || 0); }, 0);

    document.getElementById('stat-total').textContent = BIRD_DATA.length;
    document.getElementById('stat-mastered').textContent = mastered;
    document.getElementById('stat-attempts').textContent = attempts;
  } catch (e) {
    console.error('updateHomeStats error:', e);
    document.getElementById('stat-total').textContent = BIRD_DATA.length;
    document.getElementById('stat-mastered').textContent = '—';
    document.getElementById('stat-attempts').textContent = '—';
  }
}

// --------------- Memorize screen ---------------

function renderMemorizeGrid() {
  var grid = document.getElementById('memorize-grid');
  grid.innerHTML = '';

  BIRD_DATA.forEach(function (bird) {
    var card = document.createElement('div');
    card.className = 'bird-card';

    var img = document.createElement('img');
    img.src = bird.image;
    img.alt = bird.name;
    img.loading = 'lazy';

    var nameEl = document.createElement('p');
    nameEl.className = 'bird-card-name';
    nameEl.textContent = bird.name;

    card.appendChild(img);
    card.appendChild(nameEl);

    card.addEventListener('click', function () {
      openOverlay(bird);
    });

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

async function startTest() {
  var settings = loadSettings();

  try {
    currentQuestions = await selectQuestions(BIRD_DATA, settings);
  } catch (e) {
    console.error('selectQuestions error:', e);
    currentQuestions = BIRD_DATA.slice(0, Math.min(settings.questionCount, BIRD_DATA.length));
  }

  // Reset answers array
  testAnswers = currentQuestions.map(function (bird) {
    return { birdId: bird.id, userInput: '', isCorrect: null };
  });

  if (settings.displayMode === 'single') {
    currentIndex = 0;
    singleAnswered = currentQuestions.map(function () { return false; });
    renderTestSingle();
    showScreen('screen-test-single');
  } else {
    renderTestGrid();
    showScreen('screen-test-grid');
  }
}

// --------------- Test Grid mode ---------------

function renderTestGrid() {
  var grid = document.getElementById('test-grid');
  grid.innerHTML = '';

  currentQuestions.forEach(function (bird, idx) {
    var card = document.createElement('div');
    card.className = 'bird-card';
    card.dataset.idx = idx;

    var img = document.createElement('img');
    img.src = bird.image;
    img.alt = '?';
    img.loading = 'lazy';

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'bird-card-input';
    input.placeholder = 'カタカナ';
    input.dataset.idx = idx;

    // Enter key moves to next input
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

    card.appendChild(img);
    card.appendChild(input);
    grid.appendChild(card);
  });
}

async function submitGridTest() {
  var settings = loadSettings();
  var grid = document.getElementById('test-grid');
  var inputs = grid.querySelectorAll('.bird-card-input');
  var cards = grid.querySelectorAll('.bird-card');

  var correctCount = 0;

  for (var i = 0; i < currentQuestions.length; i++) {
    var bird = currentQuestions[i];
    var userInput = inputs[i] ? inputs[i].value : '';
    var isCorrect = checkAnswer(userInput, bird.name);

    if (isCorrect) correctCount++;

    testAnswers[i].userInput = userInput;
    testAnswers[i].isCorrect = isCorrect;

    // Visual feedback
    var card = cards[i];
    if (card) {
      card.classList.remove('correct', 'wrong');
      card.classList.add(isCorrect ? 'correct' : 'wrong');

      // Show correct name on wrong cards
      var nameEl = card.querySelector('.bird-card-name');
      if (!nameEl) {
        nameEl = document.createElement('p');
        nameEl.className = 'bird-card-name';
        card.appendChild(nameEl);
      }
      nameEl.textContent = bird.name;
    }

    // Disable input
    if (inputs[i]) {
      inputs[i].disabled = true;
    }

    // Update DB progress
    try {
      await updateProgress(bird.id, isCorrect, settings.masteryThreshold);
    } catch (e) {
      console.error('updateProgress error:', e);
    }
  }

  // Hide submit button
  var btnSubmit = document.getElementById('btn-submit-grid');
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

  // Update counter
  var counter = document.getElementById('single-counter');
  if (counter) {
    counter.textContent = (currentIndex + 1) + ' / ' + currentQuestions.length;
  }

  // Update image
  var img = document.getElementById('single-img');
  if (img) {
    img.src = bird.image;
    img.alt = '?';
  }

  // Reset input area visibility
  var answerArea = document.getElementById('single-answer-area');
  var feedback = document.getElementById('single-feedback');
  var input = document.getElementById('single-input');

  if (singleAnswered[currentIndex]) {
    // Already answered — show result state
    if (answerArea) answerArea.style.display = 'none';
    if (input) input.value = testAnswers[currentIndex].userInput;
    if (feedback) {
      feedback.textContent = testAnswers[currentIndex].isCorrect
        ? '正解！ ' + bird.name
        : '不正解… 正解は「' + bird.name + '」';
      feedback.className = 'single-feedback ' + (testAnswers[currentIndex].isCorrect ? 'correct' : 'wrong');
    }
  } else {
    // Not yet answered
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

  var settings = loadSettings();
  var bird = currentQuestions[currentIndex];
  var input = document.getElementById('single-input');
  var userInput = input ? input.value : '';
  var isCorrect = checkAnswer(userInput, bird.name);

  // Save answer
  testAnswers[currentIndex].userInput = userInput;
  testAnswers[currentIndex].isCorrect = isCorrect;
  singleAnswered[currentIndex] = true;

  // Show feedback
  var feedback = document.getElementById('single-feedback');
  if (feedback) {
    feedback.textContent = isCorrect
      ? '正解！ ' + bird.name
      : '不正解… 正解は「' + bird.name + '」';
    feedback.className = 'single-feedback ' + (isCorrect ? 'correct' : 'wrong');
  }

  // Hide answer area
  var answerArea = document.getElementById('single-answer-area');
  if (answerArea) answerArea.style.display = 'none';

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
      var bird = BIRD_DATA.find(function (b) { return b.id === answer.birdId; });
      if (!bird) return;

      var li = document.createElement('li');
      li.className = 'result-wrong-item';

      var img = document.createElement('img');
      img.src = bird.image;
      img.alt = bird.name;

      var info = document.createElement('div');
      info.className = 'result-wrong-item-info';

      var nameEl = document.createElement('span');
      nameEl.className = 'result-wrong-item-name';
      nameEl.textContent = bird.name;

      var answerEl = document.createElement('span');
      answerEl.className = 'result-wrong-item-answer';
      answerEl.textContent = answer.userInput
        ? '入力: 「' + answer.userInput + '」'
        : '（未入力）';

      info.appendChild(nameEl);
      info.appendChild(answerEl);
      li.appendChild(img);
      li.appendChild(info);
      wrongList.appendChild(li);
    });
  }

  showScreen('screen-result');
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
        s.questionCount = Math.min(val, BIRD_DATA.length);
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
  var btnMemorize = document.getElementById('btn-memorize');
  if (btnMemorize) {
    btnMemorize.addEventListener('click', function () {
      renderMemorizeGrid();
      showScreen('screen-memorize');
    });
  }

  var btnTest = document.getElementById('btn-test');
  if (btnTest) {
    btnTest.addEventListener('click', function () {
      startTest();
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
      showScreen('screen-home');
    });
  }

  var btnStartTest = document.getElementById('btn-start-test');
  if (btnStartTest) {
    btnStartTest.addEventListener('click', function () {
      startTest();
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
      submitGridTest();
    });
  }

  // ----- Test Single -----
  var btnBackTestSingle = document.getElementById('btn-back-test-single');
  if (btnBackTestSingle) {
    btnBackTestSingle.addEventListener('click', function () {
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
      startTest();
    });
  }

  var btnHome = document.getElementById('btn-home');
  if (btnHome) {
    btnHome.addEventListener('click', function () {
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

  setupSettingsEvents();
}

// --------------- Init ---------------

document.addEventListener('DOMContentLoaded', function () {
  setupEvents();
  updateHomeStats();
});
