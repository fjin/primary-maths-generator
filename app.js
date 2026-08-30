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
  form: document.querySelector("#generator-form"),
  topic: document.querySelector("#topic-select"),
  subtopic: document.querySelector("#subtopic-select"),
  difficulty: document.querySelector("#difficulty-select"),
  count: document.querySelector("#question-count"),
  columns: document.querySelector("#column-select"),
  seed: document.querySelector("#seed-input"),
  title: document.querySelector("#title-input"),
  includeAnswers: document.querySelector("#answer-key-toggle"),
  generate: document.querySelector("#generate-button"),
  preview: document.querySelector("#preview-button"),
  status: document.querySelector("#status-message"),
  summary: document.querySelector("#question-summary"),
  questionPreview: document.querySelector("#question-preview"),
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
    refreshPreview();
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
    refreshPreview();
  });
  elements.subtopic.addEventListener("change", refreshPreview);
  elements.difficulty.addEventListener("change", refreshPreview);
  elements.count.addEventListener("input", refreshPreview);
  elements.seed.addEventListener("input", refreshPreview);
  elements.columns.addEventListener("change", refreshPreview);
  elements.preview.addEventListener("click", refreshPreview);
  elements.generate.addEventListener("click", generatePdf);
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

function refreshPreview() {
  const selection = selectQuestions();
  state.selectedQuestions = selection.questions;
  renderPreview(selection);
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

function renderPreview(selection) {
  const { questions, available, requested, generated } = selection;
  elements.questionPreview.innerHTML = "";

  if (!questions.length) {
    elements.questionPreview.innerHTML =
      '<p class="empty-state">No questions match these filters yet.</p>';
    elements.summary.textContent = "No questions selected.";
    setStatus("Try a different topic, subtopic, or difficulty.", true);
    return;
  }

  const fragment = document.createDocumentFragment();
  questions.slice(0, 30).forEach((question, index) => {
    const card = document.createElement("article");
    card.className = "question-card";

    const number = document.createElement("span");
    number.className = "question-number";
    number.textContent = String(index + 1);

    const text = document.createElement("p");
    text.className = "question-text";
    text.textContent = question.question;

    card.append(number, text);
    fragment.append(card);
  });
  elements.questionPreview.append(fragment);

  const hiddenCount = Math.max(0, questions.length - 30);
  if (hiddenCount) {
    const note = document.createElement("p");
    note.className = "empty-state";
    note.textContent = `${hiddenCount} more questions will be included in the PDF.`;
    elements.questionPreview.append(note);
  }

  elements.summary.textContent = `${questions.length} questions selected`;
  if (questions.length < requested) {
    setStatus(`Only ${questions.length} unique questions match these filters.`, true);
  } else if (generated) {
    setStatus(`Ready. ${available} bank questions matched; ${generated} extra number-system questions were generated.`);
  } else {
    setStatus(`Ready. ${available} questions match these filters.`);
  }
}

async function generatePdf() {
  refreshPreview();
  if (!state.selectedQuestions.length) {
    return;
  }

  const generatedByServer = await generateCliStylePdf();
  if (generatedByServer) {
    return;
  }

  if (!window.jspdf?.jsPDF) {
    setStatus("PDF library is still loading. Try again in a moment.", true);
    return;
  }

  const doc = new window.jspdf.jsPDF({ unit: "pt", format: "a4" });
  const title = elements.title.value.trim() || "Primary Maths Practice";
  const difficultyLabel = DIFFICULTY_LABELS[elements.difficulty.value] || "Worksheet";
  const columns = Number(elements.columns.value);

  drawHeader(doc, title, difficultyLabel);
  drawQuestionPages(doc, state.selectedQuestions, columns);

  if (elements.includeAnswers.checked) {
    doc.addPage();
    drawHeader(doc, "Answer Key", title);
    drawAnswerPages(doc, state.selectedQuestions);
  }

  const filename = `${slugify(title)}.pdf`;
  doc.save(filename);
  setStatus(`Downloaded ${filename}.`);
}

async function generateCliStylePdf() {
  const payload = {
    topic: elements.topic.value,
    subtopic: elements.subtopic.value,
    difficulty: elements.difficulty.value,
    questions: numberFromInput(elements.count.value, 40),
    columns: numberFromInput(elements.columns.value, 1),
    answerColumns: 3,
    seed: numberFromInput(elements.seed.value, 42),
    title: elements.title.value.trim() || "Primary Maths Practice",
  };

  try {
    setStatus("Generating CLI-style PDF...");
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (response.status === 404 || response.status === 405) {
      setStatus("Using browser PDF mode. Run the local Python server for CLI-style output.");
      return false;
    }
    if (!response.ok) {
      const message = await response.json().catch(() => null);
      throw new Error(message?.error || `PDF generation failed with ${response.status}`);
    }

    const blob = await response.blob();
    const filename = filenameFromDisposition(response.headers.get("Content-Disposition"))
      || `${slugify(payload.title)}.pdf`;
    downloadBlob(blob, filename);
    setStatus(`Downloaded ${filename}.`);
    return true;
  } catch (error) {
    console.warn(error);
    setStatus("Using browser PDF mode. Run the local Python server for CLI-style output.", true);
    return false;
  }
}

function filenameFromDisposition(value) {
  if (!value) {
    return null;
  }
  const match = value.match(/filename="([^"]+)"/);
  return match ? match[1] : null;
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function drawHeader(doc, title, subtitle) {
  const pageWidth = doc.internal.pageSize.getWidth();
  doc.setFont("helvetica", "bold");
  doc.setFontSize(17);
  doc.text(title, 44, 44, { maxWidth: pageWidth - 88 });
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(90);
  doc.text(subtitle, 44, 62, { maxWidth: pageWidth - 88 });
  doc.setTextColor(0);
  doc.setDrawColor(210);
  doc.line(44, 78, pageWidth - 44, 78);
}

function drawQuestionPages(doc, questions, columns) {
  const page = pageMetrics(doc);
  const gap = columns === 2 ? 28 : 0;
  const columnWidth = (page.width - gap) / columns;
  const yStart = 100;
  let column = 0;
  let y = yStart;

  questions.forEach((question, index) => {
    const x = page.left + column * (columnWidth + gap);
    const block = measureQuestionBlock(doc, question, index + 1, columnWidth);

    if (y + block.height > page.bottom) {
      if (columns === 2 && column === 0) {
        column = 1;
        y = yStart;
      } else {
        doc.addPage();
        drawHeader(doc, elements.title.value.trim() || "Primary Maths Practice", DIFFICULTY_LABELS[elements.difficulty.value]);
        column = 0;
        y = yStart;
      }
    }

    drawQuestionBlock(doc, question, index + 1, x, y, columnWidth);
    y += block.height;
  });
}

function drawAnswerPages(doc, questions) {
  const page = pageMetrics(doc);
  const columns = 3;
  const gap = 18;
  const columnWidth = (page.width - gap * 2) / columns;
  let column = 0;
  let y = 104;

  questions.forEach((question, index) => {
    const x = page.left + column * (columnWidth + gap);
    const lines = doc.splitTextToSize(`${index + 1}. ${question.answer}`, columnWidth);
    const height = Math.max(18, lines.length * 12 + 6);

    if (y + height > page.bottom) {
      if (column < columns - 1) {
        column += 1;
        y = 104;
      } else {
        doc.addPage();
        drawHeader(doc, "Answer Key", elements.title.value.trim() || "Primary Maths Practice");
        column = 0;
        y = 104;
      }
    }

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(lines, x, y);
    y += height;
  });
}

function pageMetrics(doc) {
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  return {
    left: 44,
    width: pageWidth - 88,
    bottom: pageHeight - 46,
  };
}

function measureQuestionBlock(doc, question, number, width) {
  const parsed = parseMultipleChoice(question.question);
  const stemWidth = width - 28;
  const stemLines = doc.splitTextToSize(parsed.stem, stemWidth);
  const optionLines = parsed.options
    ? parsed.options.reduce((count, option) => {
        const optionWidth = width > 360 ? (width - 44) / 2 : width - 28;
        return count + doc.splitTextToSize(`${option.label}. ${option.text}`, optionWidth).length;
      }, 0)
    : 0;
  const optionRows = parsed.options && width > 360 ? Math.ceil(optionLines / 2) : optionLines;
  const lineHeight = 13;
  return {
    height: Math.max(34, stemLines.length * lineHeight + optionRows * 13 + 20),
  };
}

function drawQuestionBlock(doc, question, number, x, y, width) {
  const parsed = parseMultipleChoice(question.question);
  const numberSize = 19;
  const stemX = x + 28;
  const stemWidth = width - 28;

  doc.setFillColor(232, 242, 237);
  doc.circle(x + 9, y - 4, numberSize / 2, "F");
  doc.setFont("helvetica", "bold");
  doc.setFontSize(8);
  doc.setTextColor(31, 79, 65);
  doc.text(String(number), x + 9, y - 1, { align: "center" });

  doc.setTextColor(25);
  doc.setFont("helvetica", "normal");
  doc.setFontSize(width > 300 ? 10 : 9);
  const stemLines = doc.splitTextToSize(parsed.stem, stemWidth);
  doc.text(stemLines, stemX, y);

  let optionY = y + stemLines.length * 13 + 7;
  if (parsed.options) {
    const twoColumnOptions = width > 360;
    const optionWidth = twoColumnOptions ? (width - 44) / 2 : stemWidth;
    parsed.options.forEach((option, index) => {
      const optionX = twoColumnOptions && index % 2 === 1 ? stemX + optionWidth + 22 : stemX;
      const rowY = twoColumnOptions
        ? optionY + Math.floor(index / 2) * 15
        : optionY + index * 15;
      doc.setFont("helvetica", "bold");
      doc.text(`${option.label}.`, optionX, rowY);
      doc.setFont("helvetica", "normal");
      const lines = doc.splitTextToSize(option.text, optionWidth - 18);
      doc.text(lines, optionX + 18, rowY);
    });
  }

  doc.setDrawColor(225);
  doc.line(x, y + measureQuestionBlock(doc, question, number, width).height - 9, x + width, y + measureQuestionBlock(doc, question, number, width).height - 9);
}

function parseMultipleChoice(text) {
  const questionEnd = text.lastIndexOf("?");
  const searchStart = questionEnd === -1 ? 0 : questionEnd;
  const firstOption = text.slice(searchStart).search(/\sA\.?\s/);
  if (firstOption === -1) {
    return { stem: text, options: null };
  }

  const optionStart = searchStart + firstOption + 1;
  const stem = text.slice(0, optionStart).trim();
  const optionText = text.slice(optionStart).trim();
  const order = optionText.includes(" D ") && optionText.indexOf(" D ") < optionText.indexOf(" B ")
    ? ["A", "D", "B", "E", "C"]
    : ["A", "B", "C", "D", "E"];
  const options = [];
  let cursor = 0;

  for (let index = 0; index < order.length; index += 1) {
    const label = order[index];
    const pattern = new RegExp(`(?:^|\\\\s)${label}\\\\.?\\\\s+`, "g");
    pattern.lastIndex = cursor;
    const match = pattern.exec(optionText);
    if (!match) {
      return { stem: text, options: null };
    }
    const valueStart = match.index + match[0].length;
    let valueEnd = optionText.length;
    for (let nextIndex = index + 1; nextIndex < order.length; nextIndex += 1) {
      const nextPattern = new RegExp(`\\\\s${order[nextIndex]}\\\\.?\\\\s+`, "g");
      nextPattern.lastIndex = valueStart;
      const nextMatch = nextPattern.exec(optionText);
      if (nextMatch) {
        valueEnd = nextMatch.index;
        break;
      }
    }
    options.push({ label, text: optionText.slice(valueStart, valueEnd).trim() });
    cursor = valueEnd;
  }

  return { stem, options: options.sort((a, b) => a.label.localeCompare(b.label)) };
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

function slugify(value) {
  return (
    value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "maths-worksheet"
  );
}
