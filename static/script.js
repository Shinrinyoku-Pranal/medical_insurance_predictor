document.addEventListener('DOMContentLoaded', () => {
  const blocks = Array.from(document.querySelectorAll('.question-block'));
  const nextButtons = Array.from(document.querySelectorAll('.next-btn'));
  const backButtons = Array.from(document.querySelectorAll('.back-btn'));
  const currentQuestionSpan = document.getElementById('current-question');
  const introText = document.querySelector('.intro-text');
  const quizContainer = document.getElementById('quiz-container');
  const resultBlock = document.getElementById('result-block');
  const tryAgainBtn = document.getElementById('try-again');
  const bmiPopup = document.getElementById('bmi-popup');

  const openBmiBtn = document.getElementById('open-bmi-calculator');
  const closeBmiBtn = document.getElementById('close-bmi');
  const calculateBmiBtn = document.getElementById('calculate-bmi');

  // Defensive: ensure modal is hidden on load (in case CSS hasn't applied yet)
  if (bmiPopup) {
    bmiPopup.classList.remove('open');
    bmiPopup.style.display = ''; // clear inline style if present
  }

  // Only open on click — use class toggles so CSS controls visibility and transitions
  if (openBmiBtn) {
    openBmiBtn.addEventListener('click', (e) => {
      e.preventDefault();
      if (bmiPopup) bmiPopup.classList.add('open');
    });
  }

  if (closeBmiBtn) {
    closeBmiBtn.addEventListener('click', () => bmiPopup && bmiPopup.classList.remove('open'));
  }

  window.addEventListener('click', (event) => {
    if (event.target === bmiPopup) bmiPopup && bmiPopup.classList.remove('open');
  });

  if (calculateBmiBtn) {
    calculateBmiBtn.addEventListener('click', () => {
      const weight = parseFloat(document.getElementById('weight').value);
      const feet = parseFloat(document.getElementById('feet').value);
      const inches = parseFloat(document.getElementById('inches').value);

      if (!weight || isNaN(feet) || isNaN(inches)) return alert('Please fill all fields correctly');

      const heightInMeters = ((feet * 12) + inches) * 0.0254;
      const weightInKg = weight * 0.453592;
      const bmi = weightInKg / (heightInMeters ** 2);

      const bmiInput = document.querySelector('input[name="bmi"]');
      if (bmiInput) bmiInput.value = bmi.toFixed(1);
      document.getElementById('bmi-result').textContent = `Your BMI is ${bmi.toFixed(1)}`;
    });
  }

  // ----- Quiz navigation -----
  let activeIndex = blocks.findIndex(b => b.classList.contains('active'));
  if (activeIndex === -1) activeIndex = 0;
  blocks.forEach((b,i) => b.classList.toggle('active', i === activeIndex));
  if (currentQuestionSpan) currentQuestionSpan.textContent = String(activeIndex + 1);

  function validateBlock(block) {
    if (!block) return false;
    const input = block.querySelector('input, select');
    if (!input) return true;

    const valRaw = (input.value || '').trim();
    if (input.tagName.toLowerCase() === 'select') return valRaw !== '';

    if (input.type === 'number') {
      if (valRaw === '') return false;
      const num = parseFloat(valRaw);
      if (isNaN(num)) return false;
      const min = parseFloat(input.min);
      const max = parseFloat(input.max);
      if (!isNaN(min) && num < min) return false;
      if (!isNaN(max) && num > max) return false;
      const name = input.name.toLowerCase();
      if (name === 'age' && (num < 1 || num > 120)) return false;
      if (name === 'bmi' && (num < 5 || num > 80)) return false;
      if (name === 'children' && (num < 0 || num > 20)) return false;
      return true;
    }
    return valRaw.length > 0;
  }

  function goToIndex(nextIndex) {
    if (nextIndex < 0 || nextIndex >= blocks.length) return;
    blocks[activeIndex].classList.remove('active');
    blocks[nextIndex].classList.add('active');
    activeIndex = nextIndex;
    if (currentQuestionSpan) currentQuestionSpan.textContent = String(activeIndex + 1);
  }

  nextButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const currentBlock = btn.closest('.question-block');
      const idx = blocks.indexOf(currentBlock);
      if (!validateBlock(currentBlock)) return alert('Please enter a valid input before continuing.');
      const nextIdx = idx + 1;
      if (nextIdx < blocks.length) goToIndex(nextIdx);
      else document.getElementById('quizForm')?.submit();
    });
  });

  backButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const idx = blocks.indexOf(btn.closest('.question-block'));
      if (idx > 0) goToIndex(idx - 1);
    });
  });

  // Try Again
  if (tryAgainBtn) {
    tryAgainBtn.addEventListener('click', () => {
      // hide result and reset quiz to initial state
      if (resultBlock) resultBlock.classList.remove('active');
      // remove any inline display styles so the original CSS rules apply and centering is preserved
      if (quizContainer) quizContainer.style.removeProperty('display');
      if (introText) introText.style.removeProperty('display');
      document.getElementById('quizForm')?.reset();
      blocks.forEach((b,i) => b.classList.toggle('active', i===0));
      activeIndex = 0;
      currentQuestionSpan.textContent = '1';
    });
  }

  // If server rendered a result block (it is included only when the server has a prediction),
  // show it by adding the .active class and hide the intro/quiz container.
  if (resultBlock) {
    // If the server included the resultBlock it should be shown
    resultBlock.classList.add('active');
    if (introText) introText.style.display = 'none';
    if (quizContainer) quizContainer.style.display = 'none';
  }
});
