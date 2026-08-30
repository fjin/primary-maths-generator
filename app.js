const DIFFICULTY_LABELS = {
  1: "Year 3",
  2: "Year 4",
  3: "Year 5",
  4: "Year 6 / NAPLAN",
  5: "Selective / ICAS",
};

const TOPIC_LABELS = {
  mixed: "Mixed Topics",
  fractions: "Fractions",
  money: "Money",
  number_patterns: "Number Patterns",
  number_system: "Number System",
  time: "Time & Date",
  word_problems: "Word Problems",
};

const state = {
  bank: [],
  selectedQuestions: [],
};

const elements = {
  topic: document.querySelector("#topic-select"),
  subtopic: document.querySelector("#subtopic-select"),
  difficulty: document.querySelector("#difficulty-select"),
  count: document.querySelector("#question-count"),
  columns: document.querySelector("#column-select"),
  seed: document.querySelector("#seed-input"),
  title: document.querySelector("#title-input"),
  multipleChoice: document.querySelector("#multiple-choice-toggle"),
  generate: document.querySelector("#generate-button"),
  print: document.querySelector("#print-button"),
  status: document.querySelector("#status-message"),
  summary: document.querySelector("#question-summary"),
  worksheetTitle: document.querySelector("#worksheet-title"),
  worksheetMeta: document.querySelector("#worksheet-meta"),
  questions: document.querySelector("#questions-list"),
  answers: document.querySelector("#answers-list"),
};

init();

async function init() {
  try {
    const response = await fetch("data/question_bank.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Question bank returned ${response.status}`);
    }
    state.bank = (await response.json()).map(normalizeQuestion).filter(Boolean);
    populateTopicOptions();
    populateSubtopicOptions();
    attachEvents();
    generateWorksheet();
  } catch (error) {
    setStatus(
      "Could not load the question bank. Open this page through GitHub Pages or a local web server.",
      true,
    );
    console.error(error);
  }
}

function attachEvents() {
  elements.topic.addEventListener("change", () => {
    populateSubtopicOptions();
    generateWorksheet();
  });
  elements.subtopic.addEventListener("change", generateWorksheet);
  elements.difficulty.addEventListener("change", generateWorksheet);
  elements.count.addEventListener("input", generateWorksheet);
  elements.columns.addEventListener("change", generateWorksheet);
  elements.seed.addEventListener("input", generateWorksheet);
  elements.title.addEventListener("input", updateWorksheetHeading);
  elements.multipleChoice.addEventListener("change", generateWorksheet);
  elements.generate.addEventListener("click", generateWorksheet);
  elements.print.addEventListener("click", () => window.print());
}

function normalizeQuestion(item) {
  if (!item || !item.question || !item.answer || !item.topic) {
    return null;
  }
  return {
    topic: item.topic,
    subtopic: item.subtopic || "general",
    difficulty: Number(item.difficulty || 3),
    question: cleanText(item.question),
    answer: cleanText(String(item.answer)),
    tags: Array.isArray(item.tags) ? item.tags : [],
    source: item.source || "question_bank",
  };
}

function cleanText(value) {
  return String(value)
    .replace(/\\\$/g, "$")
    .replace(/\\_/g, "_")
    .replace(/\\%/g, "%")
    .replace(/\\&/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

function populateTopicOptions() {
  const topics = unique(state.bank.map((question) => question.topic)).sort();
  elements.topic.innerHTML = "";
  elements.topic.append(new Option(TOPIC_LABELS.mixed, "mixed"));
  for (const topic of topics) {
    elements.topic.append(new Option(TOPIC_LABELS[topic] || titleCase(topic), topic));
  }
}

function populateSubtopicOptions() {
  const topic = elements.topic.value;
  const questions = state.bank.filter((question) => topic === "mixed" || question.topic === topic);
  const subtopics = unique(questions.map((question) => question.subtopic)).sort();
  elements.subtopic.innerHTML = "";
  elements.subtopic.append(new Option("All subtopics", "all"));
  for (const subtopic of subtopics) {
    elements.subtopic.append(new Option(titleCase(subtopic), subtopic));
  }
}

function generateWorksheet() {
  const selection = selectQuestions();
  state.selectedQuestions = selection.questions;
  renderWorksheet(selection);
}

function selectQuestions() {
  const rng = mulberry32(numberFromInput(elements.seed.value, 42));
  const requestedCount = clamp(numberFromInput(elements.count.value, 40), 1, 250);
  const difficulty = Number(elements.difficulty.value);
  const topic = elements.topic.value;
  const subtopic = elements.subtopic.value;
  const pool = state.bank.filter((question) => {
    const topicMatches = topic === "mixed" || question.topic === topic;
    const subtopicMatches = subtopic === "all" || question.subtopic === subtopic;
    return topicMatches && subtopicMatches && question.difficulty <= difficulty;
  });

  const selected = sampleUnique(pool, Math.min(requestedCount, pool.length), rng);
  while (selected.length < requestedCount && canCreateProcedural(topic, subtopic)) {
    const next = createProceduralNumberSystemQuestion(rng, difficulty, subtopic);
    if (!selected.some((question) => question.question === next.question)) {
      selected.push(next);
    }
  }

  return {
    questions: selected,
    available: pool.length,
    requested: requestedCount,
    generated: Math.max(0, selected.length - Math.min(requestedCount, pool.length)),
  };
}

function canCreateProcedural(topic, subtopic) {
  const topicMatches = topic === "mixed" || topic === "number_system";
  const proceduralSubtopics = new Set([
    "all",
    "place_value",
    "expanded_form",
    "ordering_numbers",
    "rounding",
    "number_patterns",
    "digit_logic",
  ]);
  return topicMatches && proceduralSubtopics.has(subtopic);
}

function sampleUnique(items, count, rng) {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const target = Math.floor(rng() * (index + 1));
    [shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]];
  }
  return shuffled.slice(0, count);
}

function renderWorksheet(selection) {
  const { questions, available, requested, generated } = selection;
  updateWorksheetHeading();
  elements.questions.innerHTML = "";
  elements.answers.innerHTML = "";
  document.documentElement.style.setProperty("--worksheet-columns", elements.columns.value);

  if (!questions.length) {
    elements.questions.innerHTML = '<li class="empty-state">No questions match these filters yet.</li>';
    elements.summary.textContent = "No questions selected.";
    setStatus("Try a different topic, subtopic, or difficulty.", true);
    return;
  }

  questions.forEach((question) => {
    const questionItem = document.createElement("li");
    appendQuestionContent(questionItem, question.question, elements.multipleChoice.checked);
    elements.questions.append(questionItem);

    const answerItem = document.createElement("li");
    appendFormattedText(answerItem, answerTextForDisplay(question));
    elements.answers.append(answerItem);
  });

  elements.summary.textContent = `${questions.length} questions`;
  if (questions.length < requested) {
    setStatus(`Only ${questions.length} unique questions match these filters.`, true);
  } else if (generated) {
    setStatus(`${questions.length} questions ready. ${generated} extra number-system questions were generated.`);
  } else {
    setStatus(`${questions.length} questions ready from ${available} matching bank questions.`);
  }
}

function appendQuestionContent(questionItem, questionText, showChoices) {
  const parsed = parseMultipleChoice(questionText);

  if (!parsed) {
    questionItem.textContent = questionText;
    return;
  }

  const stem = document.createElement("p");
  stem.className = "question-stem";
  stem.textContent = parsed.stem;
  questionItem.append(stem);

  if (!showChoices) {
    return;
  }

  const choices = document.createElement("ol");
  choices.className = "choice-list";
  choices.setAttribute("aria-label", "Answer choices");

  parsed.options.forEach((option) => {
    const choice = document.createElement("li");

    const label = document.createElement("span");
    label.className = "choice-label";
    label.textContent = option.label;

    const value = document.createElement("span");
    value.className = "choice-text";
    appendFormattedText(value, option.text);

    choice.append(label, value);
    choices.append(choice);
  });

  questionItem.append(choices);
}

function answerTextForDisplay(question) {
  if (elements.multipleChoice.checked) {
    return question.answer;
  }

  const parsed = parseMultipleChoice(question.question);
  const labelMatch = question.answer.match(/^([A-E])\.?\s*(.*)$/);
  if (!parsed || !labelMatch) {
    return question.answer;
  }

  const [, answerLabel, answerText] = labelMatch;
  const choice = parsed.options.find((option) => option.label === answerLabel);
  if (!choice) {
    return answerText || question.answer;
  }

  return answerText && answerText !== answerLabel ? answerText : choice.text;
}

function appendFormattedText(container, text) {
  const fractionPattern = /(?:^|[^\w/])(?:(\d+)\s+)?(\d+)\/(\d+)(?![\w/])/g;
  let cursor = 0;
  let match = fractionPattern.exec(text);

  while (match) {
    const prefixLength = match[0].length - match[0].trimStart().length;
    const fractionStart = match.index + prefixLength;
    const fractionEnd = match.index + match[0].length;

    container.append(document.createTextNode(text.slice(cursor, fractionStart)));
    appendFraction(container, match[1], match[2], match[3]);
    cursor = fractionEnd;
    match = fractionPattern.exec(text);
  }

  container.append(document.createTextNode(text.slice(cursor)));
}

function appendFraction(container, whole, numerator, denominator) {
  const wrapper = document.createElement("span");
  wrapper.className = whole ? "mixed-number" : "simple-fraction";

  if (whole) {
    const wholeNumber = document.createElement("span");
    wholeNumber.className = "whole-number";
    wholeNumber.textContent = whole;
    wrapper.append(wholeNumber);
  }

  const fraction = document.createElement("span");
  fraction.className = "stacked-fraction";

  const numeratorText = document.createElement("span");
  numeratorText.className = "fraction-numerator";
  numeratorText.textContent = numerator;

  const denominatorText = document.createElement("span");
  denominatorText.className = "fraction-denominator";
  denominatorText.textContent = denominator;

  fraction.append(numeratorText, denominatorText);
  wrapper.append(fraction);
  container.append(wrapper);
}

function parseMultipleChoice(questionText) {
  const stemEnd = questionText.lastIndexOf("?");
  if (stemEnd === -1) {
    return null;
  }

  const stem = questionText.slice(0, stemEnd + 1).trim();
  const choicesText = questionText.slice(stemEnd + 1).trim();
  if (!stem || !choicesText) {
    return null;
  }

  const matches = [...choicesText.matchAll(/(?:^|\s)([A-E])\.?\s+/g)];
  if (matches.length < 2 || matches[0][1] !== "A") {
    return null;
  }

  const options = matches.map((match, index) => {
    const nextMatch = matches[index + 1];
    const valueStart = match.index + match[0].length;
    const valueEnd = nextMatch ? nextMatch.index : choicesText.length;
    return {
      label: match[1],
      text: choicesText.slice(valueStart, valueEnd).trim(),
    };
  });

  const labels = new Set(options.map((option) => option.label));
  if (!labels.has("B") || !labels.has("C") || options.some((option) => !option.text)) {
    return null;
  }

  return {
    stem,
    options: options.sort((left, right) => left.label.localeCompare(right.label)),
  };
}

function updateWorksheetHeading() {
  const title = elements.title.value.trim() || "Primary Maths Practice";
  const topic = TOPIC_LABELS[elements.topic.value] || titleCase(elements.topic.value);
  const subtopic = elements.subtopic.value === "all" ? "All subtopics" : titleCase(elements.subtopic.value);
  elements.worksheetTitle.textContent = title;
  elements.worksheetMeta.textContent = `${DIFFICULTY_LABELS[elements.difficulty.value]} - ${topic} - ${subtopic}`;
}

function createProceduralNumberSystemQuestion(rng, difficulty, selectedSubtopic) {
  const subtopics =
    selectedSubtopic === "all"
      ? ["place_value", "expanded_form", "ordering_numbers", "rounding", "number_patterns", "digit_logic"]
      : [selectedSubtopic];
  const subtopic = subtopics[Math.floor(rng() * subtopics.length)];
  const upper = difficulty >= 3 ? 999999 : 99999;

  if (subtopic === "place_value") {
    const places = [
      ["tens", 10],
      ["hundreds", 100],
      ["thousands", 1000],
      ["ten-thousands", 10000],
      ["hundred-thousands", 100000],
    ].filter(([, value]) => value <= upper);
    const [, placeValue] = places[Math.floor(rng() * places.length)];
    const digit = randomInt(rng, 1, 9);
    let number = randomInt(rng, 10000, upper);
    number = number - (Math.floor(number / placeValue) % 10) * placeValue + digit * placeValue;
    return proceduralQuestion(
      subtopic,
      `What is the value of the digit ${digit} in ${formatNumber(number)}?`,
      formatNumber(digit * placeValue),
    );
  }

  if (subtopic === "expanded_form") {
    const number = randomInt(rng, 10000, upper);
    const parts = [];
    String(number)
      .split("")
      .forEach((digit, index, digits) => {
        const value = Number(digit) * 10 ** (digits.length - index - 1);
        if (value) parts.push(formatNumber(value));
      });
    return proceduralQuestion(subtopic, `Write ${parts.join(" + ")} as one number.`, formatNumber(number));
  }

  if (subtopic === "ordering_numbers") {
    const values = [];
    while (values.length < 4) {
      const next = randomInt(rng, 1000, upper);
      if (!values.includes(next)) values.push(next);
    }
    return proceduralQuestion(
      subtopic,
      `Put these numbers in order from smallest to largest: ${values.map(formatNumber).join(", ")}`,
      [...values].sort((a, b) => a - b).map(formatNumber).join(", "),
    );
  }

  if (subtopic === "rounding") {
    const places = difficulty >= 3 ? [10, 100, 1000] : [10, 100];
    const place = places[Math.floor(rng() * places.length)];
    const number = randomInt(rng, 1000, upper);
    const answer = Math.round(number / place) * place;
    return proceduralQuestion(
      subtopic,
      `Round ${formatNumber(number)} to the nearest ${formatNumber(place)}.`,
      formatNumber(answer),
    );
  }

  if (subtopic === "number_patterns") {
    const steps = [25, 50, 100, 250, -25, -50, -100, -250];
    const step = steps[Math.floor(rng() * steps.length)];
    let start = randomInt(rng, 1000, difficulty >= 3 ? 90000 : 9000);
    let values = Array.from({ length: 5 }, (_, index) => start + step * index);
    while (Math.min(...values) < 0) {
      start = randomInt(rng, 1000, 90000);
      values = Array.from({ length: 5 }, (_, index) => start + step * index);
    }
    return proceduralQuestion(
      subtopic,
      `Complete the pattern: ${values.slice(0, 3).map(formatNumber).join(", ")}, _____, _____`,
      values.slice(3).map(formatNumber).join(", "),
    );
  }

  const thousands = randomInt(rng, 2, 8);
  const hundreds = randomInt(rng, 0, 9);
  const tens = (thousands + hundreds + randomInt(rng, 1, 4)) % 10;
  const ones = randomInt(rng, 0, 9);
  const number = thousands * 1000 + hundreds * 100 + tens * 10 + ones;
  return proceduralQuestion(
    "digit_logic",
    `I am a four-digit number. My thousands digit is ${thousands}. My hundreds digit is ${hundreds}. My tens digit is ${tens}. My ones digit is ${ones}. What number am I?`,
    formatNumber(number),
  );
}

function proceduralQuestion(subtopic, question, answer) {
  return {
    topic: "number_system",
    subtopic,
    difficulty: 3,
    question,
    answer,
    tags: ["number_system"],
    source: "procedural",
  };
}

function setStatus(message, isWarning = false) {
  elements.status.textContent = message;
  elements.status.classList.toggle("warning", isWarning);
}

function mulberry32(seed) {
  let value = seed >>> 0;
  return function nextRandom() {
    value += 0x6d2b79f5;
    let mixed = value;
    mixed = Math.imul(mixed ^ (mixed >>> 15), mixed | 1);
    mixed ^= mixed + Math.imul(mixed ^ (mixed >>> 7), mixed | 61);
    return ((mixed ^ (mixed >>> 14)) >>> 0) / 4294967296;
  };
}

function numberFromInput(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function randomInt(rng, min, max) {
  return Math.floor(rng() * (max - min + 1)) + min;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function unique(values) {
  return [...new Set(values)];
}

function titleCase(value) {
  return value
    .replace(/_/g, " ")
    .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-AU").format(value);
}
